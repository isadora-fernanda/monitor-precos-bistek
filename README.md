# Monitor de preços do Supermercado Bistek

Automação em **Python** que faz *web scraping* de uma categoria do site do Supermercado Bistek com **Requests** e **BeautifulSoup** (seletores CSS) e grava os produtos num banco **MySQL**. Cada execução registra a data e a hora da extração, formando um histórico para monitorar a variação de preços.

> **English:** Python web scraper (Requests and BeautifulSoup with CSS selectors) that collects a product category from the Bistek supermarket website and stores name, link, regular, current and club prices in MySQL with an extraction timestamp, building a price history.

## O que é coletado

| Coluna | Conteúdo |
|---|---|
| `dataConsulta` | Data e hora da extração |
| `nomeProduto` | Nome do produto |
| `link` | Endereço da página do produto |
| `precoAntigo` | Preço "de", quando o produto está em promoção |
| `valor` | Preço atual |
| `precoClube` | Preço para clientes do clube |
| `categoria` | Categoria, tirada do final da URL (por exemplo `floricultura-e-jardim`) |

## Como funciona

1. O script baixa a página da categoria com `requests`.
2. O BeautifulSoup encontra cada cartão de produto pelos seletores CSS da plataforma VTEX, usada pelo site.
3. Os preços em texto, como `R$ 1.234,56`, são convertidos para número.
4. Cada produto é gravado no MySQL com o mesmo horário de extração. Rodando o script várias vezes (por exemplo, uma vez por dia), a tabela acumula o histórico.

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

Para trocar de categoria, altere a variável `url` no início do `scraper.py`.

## Consultando o histórico

O arquivo `consultas.sql` traz consultas prontas para ver o histórico de um produto, o preço mais recente de cada item e os produtos que mudaram de preço entre as extrações.

```sql
SELECT dataConsulta, nomeProduto, valor, precoClube
FROM produtos
WHERE nomeProduto LIKE '%vaso%'
ORDER BY nomeProduto, dataConsulta;
```

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `scraper.py` | Script de coleta |
| `schema.sql` | Criação do banco e da tabela |
| `consultas.sql` | Consultas de acompanhamento de preços |
| `requirements.txt` | Dependências do Python |

## O que eu faria diferente hoje

- **Paginação.** O script lê só a primeira página da categoria. Lojas na plataforma VTEX costumam mostrar poucos produtos por página e carregar o resto conforme a rolagem, então seria preciso percorrer as páginas seguintes ou usar a API de busca da plataforma.
- **Seletores frágeis.** As classes CSS da VTEX mudam com atualizações do site. Eu centralizaria os seletores num só lugar e registraria um aviso quando nenhum produto for encontrado.
- **Coluna duplicada.** `valorPromocional` recebe o mesmo valor de `precoAntigo`. Eu removeria essa coluna ou passaria a gravar nela o preço promocional de fato.
- **Agendamento.** Para o monitor funcionar sozinho, o script poderia rodar todo dia pelo agendador do sistema (cron no Linux ou Agendador de Tarefas no Windows).

---

Desenvolvido por **Isadora Fernanda Zappe Schmidt** · [LinkedIn](https://www.linkedin.com/in/isadora-fernanda)
