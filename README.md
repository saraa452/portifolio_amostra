# Data Analysis and Business Intelligence Dashboard

Portfólio profissional da Dalumia Consultoria com múltiplos projetos de Data Analytics, cada um com página própria e dashboards de apoio à decisão.

Repositório GitHub: https://github.com/saraa452/portifolio_amostra

## O que foi criado

- Home profissional de portfólio em `docs/index.html` com navegação por projetos.
- Projeto 01: Business Data Analysis and Reporting (vendas) com dashboard executivo.
- Projeto 02: Administrative Process Optimization com dashboard operacional.
- Pipelines em Python para gerar JSONs consumidos pelo front-end.
- Estrutura pronta para publicação no GitHub Pages usando a pasta `docs/`.

## Estrutura

- `docs/index.html`: home do portfólio profissional (Dalumia Consultoria).
- `docs/projetos/business-data-analysis-reporting.html`: página do Projeto 01.
- `docs/projetos/administrative-process-optimization.html`: página do Projeto 02.
- `scripts/build_sales_dashboard.py`: lê `dados_vendas_50k.csv` e gera `docs/data/sales_dashboard.json`.
- `scripts/build_admin_dashboard.py`: lê `dados_processos_50k.csv` e gera `docs/data/admin_dashboard.json`.
- `docs/assets/app.js`: script do dashboard do Projeto 01.
- `docs/assets/admin-dashboard.js`: script do dashboard do Projeto 02.
- `docs/assets/styles.css`: estilo dos dashboards de projetos.
- `docs/assets/portfolio.css`: estilo da home profissional.

## Como atualizar os dados do dashboard

No terminal, dentro da pasta do projeto, execute:

```bash
/home/sara/Documentos/Portifólio/venv/bin/python scripts/build_sales_dashboard.py
/home/sara/Documentos/Portifólio/venv/bin/python scripts/build_admin_dashboard.py
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
