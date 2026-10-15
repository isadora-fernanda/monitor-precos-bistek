"""Testes do scraper sem acessar o site: usam uma página de exemplo salva em tests/."""

import os
import sys
import unittest
from unittest import mock

PASTA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(PASTA))
import scraper  # noqa: E402

with open(os.path.join(PASTA, "pagina_exemplo.html"), encoding="utf-8") as arquivo:
    HTML = arquivo.read()


class ConversaoTests(unittest.TestCase):
    def test_preco_com_milhar_e_virgula(self):
        self.assertEqual(scraper.converter_preco("R$ 1.234,56"), 1234.56)

    def test_espaco_nao_separavel(self):
        self.assertEqual(scraper.converter_preco("R$\xa039,90"), 39.90)

    def test_sem_preco(self):
        self.assertIsNone(scraper.converter_preco(None))
        self.assertIsNone(scraper.converter_preco("Indisponível"))

    def test_categoria_pela_url_ou_pelo_nome(self):
        self.assertEqual(scraper.montar_url("bebidas"), "https://www.bistek.com.br/bebidas")
        self.assertEqual(scraper.montar_url("https://www.bistek.com.br/bebidas/"),
                         "https://www.bistek.com.br/bebidas")


class ExtracaoTests(unittest.TestCase):
    def setUp(self):
        self.produtos = scraper.extrair_produtos(HTML)

    def test_ignora_cartao_sem_nome(self):
        self.assertEqual(len(self.produtos), 2)

    def test_campos_do_produto_em_promocao(self):
        vaso = self.produtos[0]
        self.assertEqual(vaso["nome"], "Vaso de Cerâmica 20 cm")
        self.assertEqual(vaso["link"], "https://www.bistek.com.br/vaso-de-ceramica-p")
        self.assertEqual(vaso["preco_antigo"], 49.90)
        self.assertEqual(vaso["valor"], 39.90)
        self.assertEqual(vaso["preco_clube"], 35.90)

    def test_produto_sem_promocao(self):
        terra = self.produtos[1]
        self.assertIsNone(terra["preco_antigo"])
        self.assertIsNone(terra["preco_clube"])
        self.assertEqual(terra["valor"], 1299.00)


class PaginacaoTests(unittest.TestCase):
    def test_para_quando_a_pagina_repete_os_produtos(self):
        resposta = mock.Mock(status_code=200, text=HTML)
        sessao = mock.Mock()
        sessao.get.return_value = resposta
        with mock.patch.object(scraper.time, "sleep"):
            produtos = scraper.coletar_categoria("https://www.bistek.com.br/x", 10, sessao)
        self.assertEqual(len(produtos), 2)
        self.assertEqual(sessao.get.call_count, 2)  # a página 2 não trouxe nada novo


if __name__ == "__main__":
    unittest.main()
