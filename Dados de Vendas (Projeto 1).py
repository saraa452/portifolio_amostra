import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker('pt_BR')
random.seed(42)
np.random.seed(42)

# Parâmetros
num_linhas = 50000
data_inicio = datetime(2023, 1, 1)
data_fim = datetime(2024, 12, 31)

# Categorias e produtos
categorias = {
    'Eletrônicos': ['Smartphone', 'Notebook', 'Tablet', 'Fone de Ouvido', 'Smartwatch'],
    'Vestuário': ['Camiseta', 'Calça Jeans', 'Vestido', 'Jaqueta', 'Tênis'],
    'Casa': ['Cafeteira', 'Liquidificador', 'Jogo de Panelas', 'Toalha de Banho', 'Travesseiro'],
    'Informática': ['Mouse', 'Teclado', 'Monitor', 'HD Externo', 'Webcam'],
    'Livros': ['Ficção', 'Não Ficção', 'Didático', 'Infantil', 'Autoajuda']
}

# Gerar produtos
produtos = []
for cat, prods in categorias.items():
    for prod in prods:
        preco_base = random.uniform(20, 5000)
        produtos.append({
            'id_produto': fake.unique.bothify(text='P???###'),
            'produto': prod,
            'categoria': cat,
            'preco_unitario': round(preco_base, 2),
            'custo_unitario': round(preco_base * random.uniform(0.5, 0.8), 2)
        })
# Adicionar mais produtos variados
for _ in range(30):
    cat = random.choice(list(categorias.keys()))
    prod = fake.word().capitalize() + ' ' + fake.word()
    preco_base = random.uniform(20, 5000)
    produtos.append({
        'id_produto': fake.unique.bothify(text='P???###'),
        'produto': prod,
        'categoria': cat,
        'preco_unitario': round(preco_base, 2),
        'custo_unitario': round(preco_base * random.uniform(0.5, 0.8), 2)
    })

# Vendedores
vendedores = [{'id_vendedor': f'V{str(i).zfill(3)}', 'nome': fake.name()} for i in range(1, 51)]

# Regiões
regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']

# Gerar dados de vendas
dados_vendas = []
for _ in range(num_linhas):
    data = fake.date_between(start_date=data_inicio, end_date=data_fim)
    produto = random.choice(produtos)
    regiao = random.choice(regioes)
    vendedor = random.choice(vendedores)
    qtd = np.random.poisson(lam=5) + 1  # média 5, mínimo 1
    # Ajustar para ter alguns outliers
    if random.random() < 0.05:  # 5% de chance de ser uma venda grande
        qtd = random.randint(10, 50)
    
    preco_unit = produto['preco_unitario']
    custo_unit = produto['custo_unitario']
    receita = qtd * preco_unit
    lucro = qtd * (preco_unit - custo_unit)
    
    dados_vendas.append({
        'data_venda': data,
        'id_produto': produto['id_produto'],
        'produto': produto['produto'],
        'categoria': produto['categoria'],
        'regiao': regiao,
        'qtd_vendida': qtd,
        'preco_unitario': preco_unit,
        'custo_unitario': custo_unit,
        'receita': receita,
        'lucro': lucro,
        'id_vendedor': vendedor['id_vendedor'],
        'nome_vendedor': vendedor['nome']
    })

df_vendas = pd.DataFrame(dados_vendas)
df_vendas['data_venda'] = pd.to_datetime(df_vendas['data_venda'])
df_vendas = df_vendas.sort_values('data_venda')

# Salvar
df_vendas.to_csv('dados_vendas_50k.csv', index=False, encoding='utf-8-sig')
print("Arquivo dados_vendas_50k.csv gerado com sucesso!")