import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go


# Configurações da página
st.set_page_config(
    page_title="Traffic Accidents - Porto Alegre, Brazil",
    page_icon="	:car:",
    layout="wide",
    initial_sidebar_state='collapsed'
)

px.set_mapbox_access_token(st.secrets['MAPBOX_TOKEN'])

@st.cache_data(ttl='24h')
def load_data():
    acidentes_poa = pd.read_csv('https://dadosabertos.poa.br/dataset/d6cfbe48-ee1f-450f-87f5-9426f6a09328/resource/b56f8123-716a-4893-9348-23945f1ea1b9/download/cat_acidentes.csv', sep=';')
    #puxando diretamente do site, o banco de dados fica sempre atualizado
    acidentes_poa.drop(['data_extracao', 'idacidente' ], axis=1, inplace=True) #limpando o dataframe
    
    acidentes_poa['data'] = pd.to_datetime(acidentes_poa['data']) #passando para formato de data
    acidentes_poa['horario'] = pd.to_datetime(acidentes_poa['hora']).dt.time
    
    acidentes_poa['hora'] = pd.to_datetime(acidentes_poa['hora']).dt.hour
    
    acidentes_poa['ano'] = pd.DatetimeIndex(acidentes_poa['data']).year
    acidentes_poa['mes'] = pd.DatetimeIndex(acidentes_poa['data']).month
    
    acidentes_poa['log1'] = acidentes_poa['log1'].str.strip()
    
    acidentes_poa['log2'] = acidentes_poa['log2'].str.strip()

    acidentes_poa['cruzamento'] = acidentes_poa['log2'].notna()
    
    return acidentes_poa

acidentes_poa = load_data()

top10 = pd.concat([acidentes_poa['log1'], acidentes_poa['log2']]).value_counts().head(10)


ano = st.selectbox(
    'Selecione o ano', sorted(acidentes_poa['ano'].unique()))



df = acidentes_poa.copy()
df = df[(df['latitude']>-31)&(df['latitude']<-29)&(df['longitude']<0)&(df['ano']==ano)]

checkbox_cruzamentos = st.checkbox('Apenas cruzamentos')

if checkbox_cruzamentos:
    cruzamentos = acidentes_poa['cruzamento']>0
    df = df[cruzamentos]

fig = px.density_mapbox(df, lat = 'latitude', lon = 'longitude',
                        zoom = 9.5,
                        mapbox_style = 'open-street-map',
                        color_continuous_scale = 'turbo',
                        opacity = 0.6,
                        radius=5,
                        center=dict(lat=-30.085815797161448 , lon= -51.17306247847506),
                        height=600)


fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                                mapbox_accesstoken= 'pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw',
                               )
st.plotly_chart(fig)
top10
df
