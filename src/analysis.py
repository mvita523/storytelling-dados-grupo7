import pandas as pd
import plotly.express as px

df = pd.read_csv(r"C:\Users\carol\Documents\GitHub\storytelling-dados-grupo7\data\processed\netflix_clean.csv")


# Filmes vs Séries
px.bar(df["type"].value_counts())

# Títulos por ano
px.line(df.groupby("release_year").size())
