import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker('pt_BR')
random.seed(42)
np.random.seed(42)

num_linhas = 50000
data_inicio = datetime(2023, 1, 1)
data_fim = datetime(2024, 12, 31)

# Campanhas
campanhas = ['Promo_Verão', 'Black_Friday', 'Dia_das_Mães', 'Natal', 'Lançamento_Produto', 'Aniversário_Loja']
canais = ['Google Ads', 'Facebook', 'Instagram', 'TikTok', 'LinkedIn', 'E-mail Marketing']

dados_mkt = []
for _ in range(num_linhas):
    data = fake.date_between(start_date=data_inicio, end_date=data_fim)
    campanha = random.choice(campanhas)
    canal = random.choice(canais)
    
    # Gerar métricas com alguma correlação
    impressoes = int(np.random.poisson(lam=20000)) + random.randint(1000, 50000)
    if impressoes < 0:
        impressoes = 1000
    
    ctr = random.uniform(0.01, 0.15)  # taxa de clique entre 1% e 15%
    cliques = int(impressoes * ctr)
    
    taxa_conversao = random.uniform(0.01, 0.20)  # 1% a 20%
    conversoes = int(cliques * taxa_conversao)
    
    cpc = random.uniform(0.5, 5.0)  # custo por clique
    investimento = cliques * cpc
    
    ticket_medio = random.uniform(50, 500)
    receita = conversoes * ticket_medio
    
    # Adicionar ruído e outliers
    if random.random() < 0.02:  # 2% de chance de campanha muito bem sucedida
        conversoes = int(conversoes * random.uniform(2, 5))
        receita = conversoes * ticket_medio * random.uniform(1, 2)
    
    dados_mkt.append({
        'data': data,
        'campanha': campanha,
        'canal': canal,
        'impressoes': impressoes,
        'cliques': cliques,
        'conversoes': conversoes,
        'investimento': round(investimento, 2),
        'receita_gerada': round(receita, 2),
        'ctr': round(ctr*100, 2),
        'taxa_conversao': round(taxa_conversao*100, 2),
        'roi': round((receita - investimento) / investimento * 100, 2) if investimento > 0 else 0
    })

df_mkt = pd.DataFrame(dados_mkt)
df_mkt['data'] = pd.to_datetime(df_mkt['data'])
df_mkt = df_mkt.sort_values('data')

df_mkt.to_csv('dados_marketing_50k.csv', index=False, encoding='utf-8-sig')
print("Arquivo dados_marketing_50k.csv gerado com sucesso!")