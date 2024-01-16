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

st.title('Traffic accidents in Porto Alegre, Brazil')

px.set_mapbox_access_token(st.secrets['MAPBOX_TOKEN'])
#############################################################################
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
#############################################################################


col1, col2 = st.columns([1,2])

#############################################################################
acidentes_poa = load_data()

with col1:
    ano = st.selectbox(
        'Selecione o ano', sorted(acidentes_poa['ano'].unique()))

df = acidentes_poa.copy()
df = df[(df['latitude']>-31)&(df['latitude']<-29)&(df['longitude']<0)&(df['ano']==ano)]
df['ups_string'] = df['ups'].astype(str)
#############################################################################



#############################################################################
with col1:
    container_filtros = st.container(border=True)
with container_filtros:
    checkbox_cruzamentos = st.toggle('Apenas cruzamentos', value=False)
    toggle_bicicleta = st.toggle('Apenas envolvendo bicicleta', value=False)
    
if toggle_bicicleta:
    bicicleta = acidentes_poa['bicicleta']>0
    df = df[bicicleta]


if checkbox_cruzamentos:
    cruzamentos = acidentes_poa['cruzamento']>0
    df = df[cruzamentos]

#############################################################################
with col2:
    tab_mapa_calor, tab_scatter = st.tabs(['Heatmap', 'Scattermap'])
    
with tab_mapa_calor:
    fig = px.density_mapbox(df, lat = 'latitude', lon = 'longitude',
                            zoom = 9.5,
                            mapbox_style = 'open-street-map',
                            color_continuous_scale = 'turbo',
                            #z='ups',
                            opacity = 0.6,
                            radius=5,
                            center=dict(lat=-30.085815797161448 , lon= -51.17306247847506),
                            height=600)
    
    
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', margin=go.layout.Margin(l=10, r=10, t=10, b=10),)
    st.plotly_chart(fig, use_container_width=True)

with tab_scatter:
    scatter_fig = px.scatter_mapbox(df.sort_values('ups'), lat = 'latitude', lon = 'longitude',
                                    zoom = 9.5,
                                    mapbox_style = 'light',
                                    color_discrete_sequence = ['forestgreen','khaki','darkred'],
                                    color = 'ups_string',
                                    size='ups',
                                    opacity = 0.6,
                                    center=dict(lat=-30.085815797161448 , lon= -51.17306247847506),
                                    hover_name="log1",
                                    hover_data= ['data','horario', 'tipo_acid', 'dia_sem'],
                                    title = 'Traffic Accidents by Standard Severity Unity',
                                    labels={'ups_string':'severidade'},
                                    height=600)
    
    
    scatter_fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', margin=go.layout.Margin(l=10, r=10, t=20, b=10),)
    st.plotly_chart(scatter_fig, use_container_width=True)
    

top10 = pd.pivot_table(data = df, index='log1', columns='ups', aggfunc='count', values='noite_dia').fillna(0)
top10['total'] = top10.sum(axis=1)
top10 = top10.sort_values('total', ascending=False).head(50)

with col1:
    top10
df

st.markdown('https://www.sinaldetransito.com.br/artigos/identificacao_de_locais_criticos_de_acidentes.pdf')
st.markdown('1 - Acidente somente Danos materiais; 5 - Acidente com Feridos; 13 - Acidente com Vítimas Fatais')
