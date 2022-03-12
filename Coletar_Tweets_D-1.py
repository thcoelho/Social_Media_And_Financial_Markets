# Importar Bibliotecas

import tweepy
import pandas as pd
import datetime as dt

# Criar variável para dia anterior
dia = dt.datetime.now()
dia = dia.replace(day=dia.day-1, hour=0, minute=0, second=0, microsecond=0)

# Criar variável com os termos a serem pesquisados
Termos = "Bitcoin"

# Obter Tokens
with open("Twitter_API.txt", "r", encoding="utf-8") as f:
    Tokens = f.readlines()
    f.close()

# Inicializar objeto Client para pesquisa de Tweets
Cliente = tweepy.Client(
    bearer_token=Tokens[-1], access_token=Tokens[1], access_token_secret=Tokens[4])

# Criar dicionário cujas keys são as horas do dia
resultados = {}

# Criar listas para segurar os Tweets e as datas correspondentes
Tweets = []
Datas = []

# Recuperar 100 tweets para cada hora do dia anterior e preencher o dicionário
for hora in range(0, 24):
    resultados[hora] = Cliente.search_recent_tweets(Termos, max_results=100, tweet_fields="created_at",
                                                    start_time=dia, end_time=dia.replace(hour=dia.hour+1))
    for i in range(len(resultados[hora].data)):
        Datas.append(resultados[hora].data[i].created_at)
        Tweets.append(resultados[hora].data[i].text)
    dia = dia.replace(hour=hora)

# Criar DataFrame Dados

Df = pd.DataFrame()
Df["Tweets"] = Tweets
Df.index = Datas

# Ler Arquivo existente
Df_Antigo = pd.read_csv("Data\Tweets.csv", sep=";", index_col="Unnamed: 0")

# Adicionar Novas Linhas

Df = pd.concat([Df, Df_Antigo])

# Exportar DataFrame para CSV.
Df.to_csv("Data\Tweets.csv", sep=";")
