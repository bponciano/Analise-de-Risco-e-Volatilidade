#Pacotes Necessarios
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import date

#Definindo as Empresas 
tickets_brutos = ['VALE3', 'ITUB4', 'ABEV3', 'BBDC4','PETR4','WEGE3','MGLU3','BPAC11','EQTL3','RENT3']
sufixo = '.SA'
tickets = [item + sufixo for item in tickets_brutos]
mapa_setores = {
    'VALE3': 'Mineração', 'PETR4': 'Petróleo', 'ABEV3': 'Bebidas',
    'BBDC4': 'Bancos', 'ITUB4': 'Bancos', 'MGLU3': 'Varejo',
    'WEGE3': 'Indústria', 'BPAC11': 'Bancos', 'EQTL3': 'Energia', 'RENT3': 'Serviços'
}

#Definindo o Periodo
inicio = '2020-01-01'
fim = date.today().strftime('%Y-%m-%d')

#Extraindo os Dados
dados_brutos = yf.download(tickets, start=inicio,end=fim)

#Camada Bronze
dados_bronze = dados_brutos['Close']
print(dados_bronze.isna().sum())
dados_bronze.to_parquet('bronze.parquet', engine='pyarrow', compression='snappy')

#Camada Silver
dados_silver = dados_bronze.pct_change().dropna()
dados_silver.columns = [ticker.replace('.SA', '') for ticker in dados_silver.columns]
volatilidade_movel = dados_silver.rolling(window=21,min_periods=5).std()
volatilidade_movel = volatilidade_movel.dropna()
print(volatilidade_movel.head())
volatilidade_movel.to_parquet('silver.parquet', engine='pyarrow', compression='snappy')

#Camada Gold
dados_gold = volatilidade_movel * np.sqrt(252)
dados_gold = dados_gold.reset_index()
dados_gold = pd.melt(dados_gold,id_vars="Date", var_name = "Ticker", value_name = "Volatilidade")
dados_gold['Setor'] = dados_gold['Ticker'].map(mapa_setores)
dados_gold.to_parquet('gold.parquet', engine='pyarrow', compression='snappy')
