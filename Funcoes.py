import tweepy
import pandas as pd
import datetime as dt
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def Coletar_Tweets(day=dt.datetime.now().day-1):
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

def Coletar_Precos():
    #Coletar Arquivo de Dados
    df = pd.read_csv("Data\Tweets.csv", sep=";", index_col="Unnamed: 0")

    # Coletar a data do primeiro tweet coletado
    inicio = df.index.min()
    inicio = inicio[:10]
    inicio

    # Coletar data do último tweet coletado
    fim = df.index.max()
    fim = fim[:10]
    fim

    # Obter preços do BTC-USD em intervalos de uma hora desde o primeiro (Somente Preço em que a hora fecha)
    Precos = yf.Ticker("BTC-USD").history(start=inicio, end=fim, interval="1h")["Close"]

    # Exportar Preços
    Precos.to_csv("Data\Precos.csv", sep=";")

def Sentimento():

    VADER = SentimentIntensityAnalyzer()

    # Ler Tweets Coletados
    Tweets = pd.read_csv("Data\Tweets.csv", sep=";", index_col="Unnamed: 0")

    # Lista para conter os sentimentos agregados
    Sentiment = []

    # Popular Lista
    for i in range(Tweets.shape[0]):
        Sentiment.append(VADER.polarity_scores(text=Tweets.iloc[i,0])["compound"])

    # Criar Coluna de sentimento no dataframe principal
    Tweets["Sentimento"] = Sentiment

    # Salvar Dataframe com sentiments
    Tweets.to_csv("Data\Sentimento_Agregado.csv", sep=";")

def Juntar_Base():
    
    # Ler dados de sentimentos e precos
    Precos = pd.read_csv("Data\Precos.csv", sep=";", index_col="Unnamed: 0")
    Sentimentos = pd.read_csv("Data\Sentimento_Agregado.csv", sep=";")
    
    # Converter coluna de horário para datetime, para podermos manipular os valores a serem compatíveis com aqueles
    # presentes no dataframe Precos, nos quais minutos e segundos são sempre 0
    Sentimentos["Unnamed: 0"] = pd.to_datetime(Sentimentos["Unnamed: 0"])
    
    # Trocar minutos diferentes de  0 por 0
    Sentimentos["Unnamed: 0"] = Sentimentos["Unnamed: 0"].mask(Sentimentos["Unnamed: 0"].dt.minute != 0, Sentimentos["Unnamed: 0"] \
    + pd.offsets.DateOffset(minute=0))    

    # Trocar segundos diferentes de 0 por 0
    Sentimentos["Unnamed: 0"] = Sentimentos["Unnamed: 0"].mask(Sentimentos["Unnamed: 0"].dt.second != 0, Sentimentos["Unnamed: 0"] \
    + pd.offsets.DateOffset(second=0))
    
    # Transformar coluna de datas em índice e ordená-la
    Sentimentos.set_index("Unnamed: 0", inplace=True)
    Sentimentos.sort_index(inplace=True)

    # Transformar índice do dataframe de preços em DateTime, para merge funcionar
    Precos.index = pd.to_datetime(Precos.index)

    # Juntar ambos os DataFrames
    Base_Completa = Sentimentos.merge(Precos, left_index=True, right_index=True)
    
    # Nomear Índice
    Base_Completa.index.name = "Horario"

    # Exportar para csv
    Base_Completa.to_csv("Data\Base_Completa.csv", sep=";")    