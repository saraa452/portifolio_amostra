import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker('pt_BR')
random.seed(42)
np.random.seed(42)

num_linhas = 50000
data_inicio = datetime(2023, 1, 1).date()
data_fim = datetime(2024, 12, 31).date()

departamentos = ['Compras', 'Jurídico', 'TI', 'RH', 'Marketing', 'Financeiro', 'Operações']
tipos_contrato = ['Fornecedor', 'Prestação de Serviços', 'Software', 'Treinamento', 'Evento', 'Consultoria']
status_list = ['Aprovado', 'Pendente', 'Rejeitado', 'Cancelado']

aprovadores = [fake.name() for _ in range(20)]

dados_proc = []
for i in range(num_linhas):
    id_contrato = f'CT{str(i+1).zfill(5)}'
    data_solicitacao = fake.date_between(start_date=data_inicio, end_date=data_fim)
    
    # Definir data de aprovação (se aplicável)
    status = random.choices(status_list, weights=[0.7, 0.15, 0.1, 0.05])[0]
    if status == 'Aprovado':
        dias_aprovacao = random.randint(1, 30)
        data_aprovacao = data_solicitacao + timedelta(days=dias_aprovacao)
        if data_aprovacao > data_fim:
            data_aprovacao = data_fim
        aprovador = random.choice(aprovadores)
    else:
        data_aprovacao = None
        dias_aprovacao = None
        aprovador = None
    
    departamento = random.choice(departamentos)
    tipo = random.choice(tipos_contrato)
    valor = round(random.uniform(1000, 500000), 2)
    
    # Adicionar alguns atrasados
    if status == 'Pendente' and random.random() < 0.3:
        data_solicitacao = data_fim - timedelta(days=random.randint(60, 90))
    
    dados_proc.append({
        'id_contrato': id_contrato,
        'data_solicitacao': data_solicitacao,
        'data_aprovacao': data_aprovacao,
        'departamento': departamento,
        'tipo_contrato': tipo,
        'valor': valor,
        'status': status,
        'dias_para_aprovacao': dias_aprovacao,
        'aprovador': aprovador
    })

df_proc = pd.DataFrame(dados_proc)
df_proc['data_solicitacao'] = pd.to_datetime(df_proc['data_solicitacao'])
df_proc['data_aprovacao'] = pd.to_datetime(df_proc['data_aprovacao']) if any(df_proc['data_aprovacao'].notna()) else None
df_proc = df_proc.sort_values('data_solicitacao')

df_proc.to_csv('dados_processos_50k.csv', index=False, encoding='utf-8-sig')
print("Arquivo dados_processos_50k.csv gerado com sucesso!")