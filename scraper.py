"""Coleta os produtos de uma categoria do site do Supermercado Bistek e grava no MySQL.

Cada execução registra a data e a hora da extração, formando um histórico de preços.

Uso:
    python scraper.py                                   # categoria padrão
    python scraper.py https://www.bistek.com.br/bebidas  # outra categoria
    python scraper.py bebidas --paginas 3                # só o final da URL também funciona
"""

import argparse
import logging
import os
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bistek")

SITE = "https://www.bistek.com.br"
CATEGORIA_PADRAO = "floricultura-e-jardim"
CABECALHOS = {"User-Agent": "Mozilla/5.0 (monitor de precos de estudo)"}
TEMPO_LIMITE = 30           # segundos por requisição
PAUSA_ENTRE_PAGINAS = 1.0   # para não sobrecarregar o site

# Seletores CSS da plataforma VTEX, usada pelo site do Bistek.
# Ficam juntos aqui porque são o que mais muda quando o site é atualizado.
SELETORES = {
    "produto": ".vtex-product-summary-2-x-container",
    "nome": ".vtex-product-summary-2-x-productBrand",
    "preco": ".vtex-product-price-1-x-sellingPrice",
    "preco_antigo": ".vtex-product-price-1-x-listPrice",
    "preco_clube": ".vtex-product-price-1-x-installmentContainer",
    "link": "a",
}


def converter_preco(texto):
    """Converte um texto como 'R$ 1.234,56' em 1234.56. Devolve None se não houver preço."""
    if not texto:
        return None
    limpo = texto.replace("R$", "").replace("\xa0", " ").replace(".", "").replace(",", ".").strip()
    try:
        return float(limpo)
    except ValueError:
        return None


def montar_url(categoria):
    """Aceita a URL completa da categoria ou só o final dela, como 'bebidas'."""
    if categoria.startswith("http"):
        return categoria.rstrip("/")
    return f"{SITE}/{categoria.strip('/')}"


def extrair_produtos(html):
    """Lê o HTML de uma página de categoria e devolve a lista de produtos encontrados."""
    soup = BeautifulSoup(html, "html.parser")
    produtos = []

    for box in soup.select(SELETORES["produto"]):
        nome_tag = box.select_one(SELETORES["nome"])
        if not nome_tag:
            continue

        def preco(chave):
            tag = box.select_one(SELETORES[chave])
            return converter_preco(tag.get_text()) if tag else None

        link_tag = box.select_one(SELETORES["link"])
        link = urljoin(SITE, link_tag.get("href", "")) if link_tag else ""

        produtos.append({
            "nome": nome_tag.get_text(strip=True),
            "link": link,
            "preco_antigo": preco("preco_antigo"),
            "valor": preco("preco"),
            "preco_clube": preco("preco_clube"),
        })

    return produtos


def coletar_categoria(url, max_paginas, sessao=None):
    """Percorre as páginas da categoria (?page=1, 2, ...) até não aparecerem produtos novos."""
    sessao = sessao or requests.Session()
    todos, links_vistos = [], set()

    for pagina in range(1, max_paginas + 1):
        resposta = sessao.get(url, params={"page": pagina}, headers=CABECALHOS, timeout=TEMPO_LIMITE)
        if resposta.status_code != 200:
            log.warning("Página %d respondeu HTTP %d, parando.", pagina, resposta.status_code)
            break

        novos = [p for p in extrair_produtos(resposta.text) if p["link"] not in links_vistos]
        if not novos:
            break

        log.info("Página %d: %d produtos", pagina, len(novos))
        links_vistos.update(p["link"] for p in novos)
        todos.extend(novos)
        time.sleep(PAUSA_ENTRE_PAGINAS)

    if not todos:
        log.warning("Nenhum produto encontrado. Os seletores CSS do site podem ter mudado.")
    return todos


def salvar(conexao, produtos, categoria, data_consulta):
    """Grava os produtos com o mesmo horário de extração, formando um ponto do histórico."""
    sql = """
        INSERT INTO produtos
            (dataConsulta, nomeProduto, link, precoAntigo, valor, precoClube, categoria)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            precoAntigo = VALUES(precoAntigo),
            valor       = VALUES(valor),
            precoClube  = VALUES(precoClube)
    """
    with conexao.cursor() as cursor:
        cursor.executemany(sql, [
            (data_consulta, p["nome"], p["link"], p["preco_antigo"], p["valor"], p["preco_clube"], categoria)
            for p in produtos
        ])
    conexao.commit()


def conectar():
    """Abre a conexão com o MySQL usando as variáveis de ambiente (veja o README)."""
    import pymysql  # importado aqui para os testes rodarem sem o driver

    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "bistek"),
        charset="utf8mb4",
    )


def main():
    parser = argparse.ArgumentParser(description="Monitor de preços do Supermercado Bistek")
    parser.add_argument("categoria", nargs="?", default=CATEGORIA_PADRAO,
                        help="URL ou final da URL da categoria (padrão: %(default)s)")
    parser.add_argument("--paginas", type=int, default=10, help="máximo de páginas a percorrer")
    args = parser.parse_args()

    url = montar_url(args.categoria)
    categoria = url.split("/")[-1]  # a categoria vem do final da URL
    data_consulta = datetime.now().replace(microsecond=0)

    produtos = coletar_categoria(url, args.paginas)
    if not produtos:
        return

    conexao = conectar()
    try:
        salvar(conexao, produtos, categoria, data_consulta)
    finally:
        conexao.close()
    log.info("%d produtos de '%s' gravados em %s.", len(produtos), categoria, data_consulta)


if __name__ == "__main__":
    main()
