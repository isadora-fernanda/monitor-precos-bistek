-- Banco e tabela usados pelo scraper.
-- Cada execução grava uma nova linha por produto, com a data e hora da extração,
-- o que forma o histórico de preços.

CREATE DATABASE IF NOT EXISTS bistek
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE bistek;

CREATE TABLE IF NOT EXISTS produtos (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    dataConsulta     DATETIME      NOT NULL,
    nomeProduto      VARCHAR(255)  NOT NULL,
    link             VARCHAR(500)  NOT NULL,
    precoAntigo      DECIMAL(10,2) NULL,
    valor            DECIMAL(10,2) NULL,
    precoClube       DECIMAL(10,2) NULL,
    categoria        VARCHAR(100)  NOT NULL,
    -- Evita gravar o mesmo produto duas vezes na mesma extração
    UNIQUE KEY uq_produto_consulta (link(255), dataConsulta)
);
