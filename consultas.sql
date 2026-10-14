-- Consultas úteis para acompanhar os preços

USE bistek;

-- Histórico de preço de um produto, da extração mais antiga para a mais recente
SELECT dataConsulta, nomeProduto, valor, precoClube
FROM produtos
WHERE nomeProduto LIKE '%vaso%'
ORDER BY nomeProduto, dataConsulta;

-- Preço mais recente de cada produto da categoria
SELECT p.nomeProduto, p.valor, p.precoAntigo, p.precoClube, p.dataConsulta
FROM produtos p
JOIN (
    SELECT link, MAX(dataConsulta) AS ultima
    FROM produtos
    GROUP BY link
) u ON u.link = p.link AND u.ultima = p.dataConsulta
ORDER BY p.nomeProduto;

-- Produtos cujo preço variou entre a primeira e a última extração
SELECT nomeProduto,
       MIN(valor) AS menor_preco,
       MAX(valor) AS maior_preco,
       COUNT(*)   AS extracoes
FROM produtos
GROUP BY link, nomeProduto
HAVING MIN(valor) <> MAX(valor);
