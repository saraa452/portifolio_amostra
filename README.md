# Data Analysis and Business Intelligence Dashboard

Projeto de portfólio construído a partir do arquivo `dados_vendas_50k.csv`, com foco em transformar dados brutos de vendas em indicadores executivos, insights comerciais e uma página pública para apresentação no GitHub Pages.

Repositório GitHub: https://github.com/saraa452/portifolio_amostra

## O que foi criado

- Pipeline em Python para agregar KPIs e gerar um JSON consumido pelo front-end.
- Dashboard estático com foco em receita, lucro, categorias, regiões, produtos e vendedores.
- Estrutura pronta para publicar no GitHub Pages usando a pasta `docs/`.

## Estrutura

- `scripts/build_sales_dashboard.py`: lê o CSV e gera `docs/data/sales_dashboard.json`.
- `docs/index.html`: página principal do projeto.
- `docs/assets/styles.css`: identidade visual do dashboard.
- `docs/assets/app.js`: carregamento dos dados e renderização dos gráficos.

## Como atualizar os dados do dashboard

No terminal, dentro da pasta do projeto, execute:

```bash
/home/sara/Documentos/Portifólio/venv/bin/python scripts/build_sales_dashboard.py
```

## Como publicar no GitHub Pages

1. Crie um repositório no GitHub.
2. Envie os arquivos deste projeto para a branch `main`.
3. No GitHub, abra `Settings` > `Pages`.
4. Em `Build and deployment`, escolha `Deploy from a branch`.
5. Selecione a branch `main` e a pasta `/docs`.
6. Salve e aguarde a URL pública ser gerada.

## Comandos úteis para subir o projeto

```bash
git init
git add .
git commit -m "Add BI sales dashboard portfolio project"
git branch -M main
git remote add origin https://github.com/saraa452/portifolio_amostra.git
git push -u origin main
```

## Ferramentas usadas

- Python
- pandas
- Chart.js
- HTML, CSS e JavaScript
