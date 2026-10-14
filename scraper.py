"""Coleta os produtos de uma categoria do site do Supermercado Bistek e grava no MySQL.

Cada execução registra a data e a hora da extração, formando um histórico de preços.
"""

import os
from datetime import datetime

import pymysql
import requests
from bs4 import BeautifulSoup

# Credenciais do banco lidas de variáveis de ambiente (com valores padrão para uso local)
conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DATABASE", "bistek"),
    charset="utf8mb4",
)
cursor = conn.cursor()

url = "https://www.bistek.com.br/floricultura-e-jardim"
categoria = url.split("/")[-1]  # a categoria vem do final da URL

# Mesmo horário para todos os produtos desta extração
data_consulta = datetime.now()

response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)


def converter_preco(valor):
    """Converte um texto como 'R$ 1.234,56' em 1234.56. Devolve None se não houver preço."""
    if not valor:
        return None
    try:
        valor = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(valor)
    except ValueError:
        return None


if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    produtos = soup.select(".vtex-product-summary-2-x-container")
    print("Produtos encontrados:", len(produtos))

    for box in produtos:
        nome_tag = box.select_one(".vtex-product-summary-2-x-productBrand")
        preco_tag = box.select_one(".vtex-product-price-1-x-sellingPrice")
        preco_antigo_tag = box.select_one(".vtex-product-price-1-x-listPrice")
        preco_clube_tag = box.select_one(".vtex-product-price-1-x-installmentContainer")

        if not nome_tag:
            continue

        nome = nome_tag.text.strip()
        valor = converter_preco(preco_tag.text if preco_tag else None)
        preco_antigo = converter_preco(preco_antigo_tag.text if preco_antigo_tag else None)
        preco_clube = converter_preco(preco_clube_tag.text if preco_clube_tag else None)

        link = ""
        link_tag = box.select_one("a")
        if link_tag:
            link = link_tag.get("href", "")
            if link.startswith("/"):
                link = "https://www.bistek.com.br" + link

        sql = """
            INSERT INTO produtos
                (dataConsulta, nomeProduto, link, precoAntigo, valor,
                 valorPromocional, precoClube, categoria)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                precoAntigo = VALUES(precoAntigo),
                valor = VALUES(valor),
                valorPromocional = VALUES(valorPromocional),
                precoClube = VALUES(precoClube),
                categoria = VALUES(categoria),
                dataConsulta = VALUES(dataConsulta)
        """
        cursor.execute(
            sql,
            (data_consulta, nome, link, preco_antigo, valor, preco_antigo, preco_clube, categoria),
        )
        print("Salvo:", nome, "|", valor)

    conn.commit()
else:
    print("Falha ao acessar a página. Código HTTP:", response.status_code)

cursor.close()
conn.close()
print("FIM!")
