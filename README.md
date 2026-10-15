# Monitor de preços do Supermercado Bistek

Automação em **Python** que faz *web scraping* de uma categoria do site do Supermercado Bistek com **Requests** e **BeautifulSoup** (seletores CSS) e grava os produtos num banco **MySQL**. Cada execução registra a data e a hora da extração, formando um histórico para monitorar a variação de preços. Foi um trabalho individual do curso **Python para Inteligência Artificial** do **Entra21** (Blusoft e ACATE), em 2026.

> **English:** Python web scraper (Entra21 Python for AI course, 2026) that collects a product category from the Bistek supermarket website with Requests and BeautifulSoup CSS selectors, follows the category pages and stores name, link, regular, current and club prices in MySQL with an extraction timestamp, building a price history. Includes offline unit tests.

## O que o enunciado pedia

| Requisito | Como foi atendido |
|---|---|
| Requests, BeautifulSoup e seletores CSS | Seletores da plataforma VTEX reunidos num só lugar no `scraper.py` |
| Coletar uma categoria específica | A categoria é escolhida na linha de comando, e todas as páginas dela são percorridas |
| Nome, link, preço antigo (se houver), preço atual e preço do Clube | Colunas `nomeProduto`, `link`, `precoAntigo`, `valor` e `precoClube` |
| Categoria definida pela URL | Coluna `categoria`, tirada do final da URL (por exemplo `floricultura-e-jardim`) |
| Data e hora da extração | Coluna `dataConsulta`, com o mesmo horário para todos os produtos de uma execução |

## Como funciona

1. O script baixa a página da categoria com `requests` e segue para as próximas (`?page=2`, `?page=3`...) até não aparecerem produtos novos, com uma pausa de 1 segundo entre as páginas.
2. O BeautifulSoup encontra cada cartão de produto pelos seletores CSS da plataforma VTEX, usada pelo site. Cartões sem nome são ignorados.
3. Os preços em texto, como `R$ 1.234,56`, são convertidos para número, e os links relativos viram endereços completos.
4. Todos os produtos são gravados no MySQL de uma vez, com o mesmo horário de extração. Rodando o script várias vezes (por exemplo, uma vez por dia), a tabela acumula o histórico.

Se nenhum produto for encontrado, o script avisa que os seletores do site podem ter mudado, em vez de terminar em silêncio.

## Como rodar

1. Crie o banco e a tabela.
   ```bash
   mysql -u root -p < schema.sql
   ```
2. Instale as dependências.
   ```bash
   pip install -r requirements.txt
   ```
3. Informe a senha do MySQL por variável de ambiente e rode.

   **Linux ou macOS**
   ```bash
   export MYSQL_PASSWORD="sua_senha"
   python scraper.py
   ```

   **Windows (PowerShell)**
   ```powershell
   $env:MYSQL_PASSWORD="sua_senha"
   python scraper.py
   ```

   Também dá para mudar `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER` e `MYSQL_DATABASE`. Os valores padrão são `localhost`, `3306`, `root` e `bistek`.

Para coletar outra categoria, passe a URL ou só o final dela. A opção `--paginas` limita quantas páginas serão lidas.

```bash
python scraper.py bebidas
python scraper.py https://www.bistek.com.br/hortifruti --paginas 3
```

## Consultando o histórico

O arquivo `consultas.sql` traz consultas prontas para ver o histórico de um produto, o preço mais recente de cada item e os produtos que mudaram de preço entre as extrações.

```sql
SELECT dataConsulta, nomeProduto, valor, precoClube
FROM produtos
WHERE nomeProduto LIKE '%vaso%'
ORDER BY nomeProduto, dataConsulta;
```

## Testes

```bash
python -m unittest discover -s tests -v
```

São 8 testes que rodam sem internet e sem banco. Eles usam uma página de exemplo com produtos fictícios, salva em `tests/`, e verificam a conversão dos preços, a leitura de cada campo, o produto sem promoção e a parada da paginação.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `scraper.py` | Script de coleta |
| `schema.sql` | Criação do banco e da tabela |
| `consultas.sql` | Consultas de acompanhamento de preços |
| `tests/` | Testes automatizados e página de exemplo |
| `requirements.txt` | Dependências do Python |

## O que eu faria diferente hoje

Revisei o código depois da entrega. Passei a ler a senha do banco de variável de ambiente, acrescentei a paginação, a escolha da categoria pela linha de comando e os testes, e tirei uma coluna `valorPromocional` que só repetia o preço antigo. Ainda daria para melhorar:

- **API em vez do HTML.** A plataforma VTEX tem uma API de busca que devolve os produtos em JSON. Ela é mais estável que os seletores CSS, que mudam quando o site é atualizado.
- **Preço do Clube.** O seletor usado para esse preço é o mesmo do bloco de parcelamento da VTEX. Eu confirmaria no site se ele sempre traz o preço do Clube.
- **Agendamento.** Para o monitor funcionar sozinho, o script poderia rodar todo dia pelo agendador do sistema (cron no Linux ou Agendador de Tarefas no Windows).

---

Desenvolvido por **Isadora Fernanda Zappe Schmidt** · [LinkedIn](https://www.linkedin.com/in/isadora-fernanda)
