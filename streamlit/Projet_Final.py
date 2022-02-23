# IMPORT

from IPython.core.display import HTML
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
from pymongo import MongoClient
import matplotlib.pyplot as plt
import plotly.express as px
from pathlib import Path
import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
import numpy as np
from bs4 import *
import datetime
import requests 
import pymongo
import os
import csv
import json

# DEF

@st.cache
def load_data_df():
    client = MongoClient('localhost',27017)
    db = client.scraping
    cards = db.cards.find()
    df = pd.DataFrame.from_records(cards)
    df = df.drop(["_id"], axis=1)
    return df

def load_data_list():
    client = MongoClient('localhost',27017)
    db = client.scraping
    cards = db.cards.find()
    cards = list(cards)
    return cards

st.set_page_config(
   page_title="Cards",
   layout="wide",
   initial_sidebar_state='collapsed'
)

df = load_data_df()
# print(df)
cards = load_data_list()

# PAGE

st.title("Cards")

if st.checkbox("Voir le DataFrame en entier", False):
   # st.dataframe(df[['Rang','Nom','Notation /100','Utilisation %','Victoire %']])
   st.dataframe(df)

if st.checkbox("Voir le DataFrame selon le slider", False):
   win = st.slider("Taux de victoire :", int(df["Victoire %"].min()), int(df["Victoire %"].max()))
   st.subheader("Taux de victoire de %i p. 100 à %i p. 100" % (int(df["Victoire %"].min()), win))
   df_slider = df[df["Victoire %"]  <= win]
   st.write(df_slider.sort_values(by='Victoire %',ascending=False))

if st.checkbox("Voir les données selon un input",False):
   st.subheader("Précision de la demande")
   st.markdown("Renseignez vos filtres")
   use= st.number_input("Choisir le pourcentage d'utilisation ", min_value=df['Utilisation %'].min(),max_value=df['Utilisation %'].max())
   note= st.number_input("Choisir une note ", min_value=df['Notation /100'].min(),max_value=df['Notation /100'].max())
   df_input = df[(df["Utilisation %"]  <= use) & (df['Notation /100'] <= note)]
   st.write('Votre recherche : ', df_input)

# if st.checkbox("Voir les données sans filtres avec image", False):
#    for item in cards:
#       st.image(f"{item['Image']}")
#       st.write(
#          "Nom des cartes : "f"{item['Nom']}"" | "
#          "Rang de popularité : "f"{item['Rang']}"" | "
#          "Note des Joueurs : "f"{item['Notation /100']} ""/ 100"" | "
#          "Taux d'utilisation : "f"{item['Utilisation %']}"" %"" | "
#          "Taux de victoire avec : "f"{item['Victoire %']}"" %"" | "
#       )

if st.checkbox("Voir les données sans filtres avec image",False):
   col1, col2 = st.columns(2)
   for item in cards:
      with col1:
         st.header(f"{item['Nom']}")
         st.image(f"{item['Image']}")
      with col2:
         st.markdown("\n")
         st.markdown("\n")
         st.markdown("\n")
         st.markdown("\n")
         st.markdown("\n")
         st.markdown("\n")
         st.markdown("Rang de popularité : "f"{item['Rang']}")
         st.markdown("Note des Joueurs : "f"{item['Notation /100']} ""/ 100")
         st.markdown("Taux d'utilisation : "f"{item['Utilisation %']}"" %")
         st.markdown("Taux de victoire avec : "f"{item['Victoire %']}"" %")
         st.markdown("\n")

# CHARTS

# # BAR

bar_col, pie_col,scatter_col = st.columns(3)

use = df['Utilisation %'].value_counts()

bar_col.subheader('Nombre de cartes utilisés par pourcentage')

bar_col.bar_chart(use)

# # PIE

note = df["Notation /100"].value_counts().to_frame()
note = note[note["Notation /100"] >= 3]

pie_col.subheader('Nombre de cartes ayant la même note (nb>=3)')

fig = px.pie(note, values='Notation /100')

fig.update_layout(showlegend=False,
   width=400,
   height=400,
   margin=dict(l=1,r=1,b=1,t=1),
   font=dict(color='#383635', size=15))

fig.update_traces(textposition='inside', textinfo='percent+label')

pie_col.write(fig)

# # 

use=df['Utilisation %']

# fig, ax = plt.subplots()
# ax.hist(use, bins=20)
# ax.set(xlabel='Taux d\'utilisation', 
#        ylabel='Count',
#        title='Distribution du taux d\'utilisations')
# st.pyplot(fig)

win=df['Victoire %']

# fig, ax = plt.subplots()
# ax.hist(win)
# ax.set(xlabel='Taux de victoire', 
#        ylabel='Count',
#        title='Distribution du taux de victoire')
# st.pyplot(fig)

scatter_col.subheader('Distribution du taux de victoire selon le taux d\'utilisation des cartes')

fig,ax = plt.subplots()
ax.scatter(win,use)
ax.set(xlabel='Taux de victoire', 
       ylabel='Taux d\'utilisation')
scatter_col.write(fig)
# st.pyplot(fig)