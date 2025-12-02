import ast
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import numpy as np

# --------- Ajuste o caminho se for diferente no seu PC ---------
CSV_PATH = r"C:\Users\Evita\Downloads\Atividade3\storytelling-dados-grupo7\data\raw\netflix_clean.csv"
# ----------------------------------------------------------------

# Carregar dataset (com fallback de erro claro)
try:
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Ficheiro não encontrado: {CSV_PATH}. Verifique o caminho.")

# ---------- LIMPEZA / NORMALIZAÇÃO RÁPIDA ----------
# Garantir release_year numérico
if "release_year" in df.columns:
    # forçar números, substituir erros por NaN e depois preencher com -1
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
    df["release_year"] = df["release_year"].fillna(-1).astype(int)
else:
    df["release_year"] = -1

# Função segura para converter strings que representam listas em listas reais
def safe_list(x):
    if isinstance(x, list):
        return x
    if pd.isna(x):
        return ["Unknown"]
    try:
        parsed = ast.literal_eval(x)
        if isinstance(parsed, (list, tuple, set)):
            # garantir lista e strip dos valores
            return [str(i).strip() for i in list(parsed)]
        # se não for iterável, devolve como string única
        return [str(parsed).strip()]
    except Exception:
        # se não for possível converter, tenta dividir por vírgula como fallback
        try:
            return [s.strip() for s in str(x).split(",") if s.strip() != ""]
        except:
            return ["Unknown"]

# Aplicar a conversão segura
if "listed_in" in df.columns:
    df["listed_in"] = df["listed_in"].apply(safe_list)
else:
    df["listed_in"] = [["Unknown"] for _ in range(len(df))]

# Garantir colunas básicas existirem
for col in ["type", "title", "country"]:
    if col not in df.columns:
        df[col] = "Unknown"

# Criar listas/valores para filtros
genres = sorted({g for sublist in df["listed_in"] for g in sublist})
types = sorted(df["type"].fillna("Unknown").unique())

# Definir intervalo de anos válidos (ignorar -1)
valid_years = df.loc[df["release_year"] >= 0, "release_year"]
if not valid_years.empty:
    year_min = int(valid_years.min())
    year_max = int(valid_years.max())
else:
    year_min, year_max = 1900, 2025

# Criar marcas do slider (a cada 5 ou 10 anos dependendo do range)
def make_marks(start, end, step=5):
    marks = {}
    for y in range(start, end + 1, step):
        marks[y] = str(y)
    marks[start] = str(start)
    marks[end] = str(end)
    return marks

year_marks = make_marks(year_min, year_max, step=5 if (year_max - year_min) > 20 else 1)

# ---------- FUNÇÃO PRINCIPAL QUE CRIA O LAYOUT E CALLBACKS ----------
def create_dashboard(app):

    app.layout = html.Div([

        html.H1("Dashboard Netflix", className="title"),

        html.Div([

            # GÊNERO
            html.Div([
                html.Label("Gênero"),
                dcc.Dropdown(
                    id="genre_filter",
                    options=[{"label": g, "value": g} for g in genres],
                    placeholder="Escolha um género",
                    multi=False
                )
            ], className="filter-box"),

            # TIPO
            html.Div([
                html.Label("Tipo"),
                dcc.Dropdown(
                    id="type_filter",
                    options=[{"label": t, "value": t} for t in types],
                    value=None,
                    placeholder="Movie ou TV Show",
                    multi=False
                )
            ], className="filter-box"),

            # ANO
            html.Div([
                html.Label("Ano de lançamento"),
                dcc.RangeSlider(
                    id="year_filter",
                    min=year_min,
                    max=year_max,
                    value=[year_min, year_max],
                    marks=year_marks,
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ], className="filter-box"),

        ], className="filters-container"),

        html.Br(),

        # KPIs
        html.Div([
            html.Div(id="kpi_total", className="kpi-card"),
            html.Div(id="kpi_movies", className="kpi-card"),
            html.Div(id="kpi_tvshows", className="kpi-card"),
        ], className="kpi-container"),

        html.Br(),

        # GRÁFICOS
        html.Div([
            dcc.Graph(id="graph_year", className="graph-box"),
            dcc.Graph(id="graph_genres", className="graph-box"),
            dcc.Graph(id="graph_type_pie", className="graph-box"),
        ], className="graphs-container"),

        html.Br(),

        # TABELA
        html.H2("Títulos Filtrados"),
        dash_table.DataTable(
            id="table_results",
            columns=[{"name": i, "id": i} for i in ["title", "type", "release_year", "country"]],
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
        ),

        html.Br(),

        # INSIGHTS
        html.Div(id="insights_box", className="insights")

    ], className="main-container")


    # ======================
    #   FUNÇÃO DE FILTRO
    # ======================
    def filter_data(selected_genre, selected_type, year_range):
        filtered = df.copy()

        # Género
        if selected_genre:
            filtered = filtered[filtered["listed_in"].apply(lambda x: selected_genre in x)]

        # Tipo
        if selected_type:
            filtered = filtered[filtered["type"] == selected_type]

        # Ano (trata -1 como desconhecido)
        if year_range and len(year_range) == 2:
            filtered = filtered[
                (filtered["release_year"] >= year_range[0]) &
                (filtered["release_year"] <= year_range[1])
            ]

        return filtered


    # ======================
    #        KPI’S
    # ======================
    @app.callback(
        Output("kpi_total", "children"),
        Output("kpi_movies", "children"),
        Output("kpi_tvshows", "children"),
        Input("genre_filter", "value"),
        Input("type_filter", "value"),
        Input("year_filter", "value"),
    )
    def update_kpis(selected_genre, selected_type, year_range):
        f = filter_data(selected_genre, selected_type, year_range)

        total = len(f)
        movies = len(f[f["type"] == "Movie"])
        tvshows = len(f[f["type"] == "TV Show"])

        return (
            html.Div([html.H4("Total de títulos"), html.P(f"{total}")]),
            html.Div([html.H4("Filmes"), html.P(f"{movies}")]),
            html.Div([html.H4("Séries"), html.P(f"{tvshows}")])
        )


    # ======================
    # GRÁFICO: Títulos por ano
    # ======================
    @app.callback(
        Output("graph_year", "figure"),
        Input("genre_filter", "value"),
        Input("type_filter", "value"),
        Input("year_filter", "value"),
    )
    def update_graph_year(selected_genre, selected_type, year_range):
        f = filter_data(selected_genre, selected_type, year_range)

        if f.empty:
            return px.histogram(title="Títulos por ano (sem dados)")

        # Remover anos inválidos (-1)
        valid = f[f["release_year"] >= 0]

        if valid.empty:
            return px.histogram(title="Títulos por ano (sem dados válidos)")

        fig = px.histogram(
            valid, x="release_year",
            title="Títulos por ano",
            nbins=40,
            labels={"release_year": "Ano"}
        )

        fig.update_layout(margin=dict(l=40, r=20, t=50, b=50))
        return fig


    # ======================
    # GRÁFICO: Distribuição dos géneros
    # ======================
    @app.callback(
        Output("graph_genres", "figure"),
        Input("genre_filter", "value"),
        Input("type_filter", "value"),
        Input("year_filter", "value"),
    )
    def update_genre_distribution(selected_genre, selected_type, year_range):
        f = filter_data(selected_genre, selected_type, year_range)

        # Se o dataframe estiver vazio, retorna gráfico vazio
        if f.empty:
            return px.bar(title="Distribuição dos Géneros (sem dados)")

        # Explodir géneros com segurança
        try:
            exploded = f.explode("listed_in")
        except Exception as e:
            return px.bar(title=f"Erro ao processar géneros")

        # Contagem
        counts = exploded["listed_in"].value_counts().reset_index()
        counts.columns = ["Género", "Quantidade"]

        if counts.empty:
            return px.bar(title="Distribuição dos Géneros (nenhum género encontrado)")

        fig = px.bar(
            counts,
            x="Género",
            y="Quantidade",
            title="Distribuição dos Géneros",
            labels={"Quantidade": "Quantidade", "Género": "Género"}
        )

        fig.update_layout(
            xaxis_tickangle=45,
            height=500,
            margin=dict(l=40, r=40, t=50, b=120)
        )

        return fig


    # ======================
    # GRÁFICO: Movie vs TV Show (pizza)
    # ======================
    @app.callback(
        Output("graph_type_pie", "figure"),
        Input("genre_filter", "value"),
        Input("type_filter", "value"),
        Input("year_filter", "value"),
    )
    def update_pie(selected_genre, selected_type, year_range):
        f = filter_data(selected_genre, selected_type, year_range)

        if f.empty:
            return px.pie(title="Distribuição: Filmes vs Séries (sem dados)")

        # Contagem por tipo
        type_counts = f["type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]

        if type_counts.empty:
            return px.pie(title="Distribuição: Filmes vs Séries (nenhum dado)")

        fig = px.pie(
            type_counts, names="type", values="count",
            title="Distribuição: Filmes vs Séries"
        )
        return fig


    # ======================
    # TABELA
    # ======================
    @app.callback(
        Output("table_results", "data"),
        Input("genre_filter", "value"),
        Input("type_filter", "value"),
        Input("year_filter", "value"),
    )
    def update_table(selected_genre, selected_type, year_range):
        f = filter_data(selected_genre, selected_type, year_range)
        # Garantir colunas em string simples e preencher NaN
        table_df = f[["title", "type", "release_year", "country"]].fillna("Unknown")
        return table_df.to_dict("records")


    # ======================
    # INSIGHTS AUTOMÁTICOS
    # ======================
    @app.callback(
        Output("insights_box", "children"),
        Input("genre_filter", "value"),
        Input("type_filter", "value"),
        Input("year_filter", "value"),
    )
    def update_insights(selected_genre, selected_type, year_range):
        f = filter_data(selected_genre, selected_type, year_range)

        if len(f) == 0:
            return html.Div([html.H3("Insights"), html.P("Nenhum título encontrado com os filtros selecionados.")])

        top_country = f["country"].mode()[0] if "country" in f.columns and not f["country"].mode().empty else "N/A"
        top_year = int(f.loc[f["release_year"] >= 0, "release_year"].mode()[0]) if not f.loc[f["release_year"] >= 0, "release_year"].mode().empty else "N/A"

        return html.Div([
            html.H3("Insights"),
            html.P(f"País com mais títulos no filtro: {top_country}"),
            html.P(f"Ano mais comum: {top_year}"),
            html.P(f"Número total de títulos: {len(f)}")
        ])
