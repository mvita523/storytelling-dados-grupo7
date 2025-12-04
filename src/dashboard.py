import ast
import pandas as pd
import numpy as np
import plotly.express as px
from dash import dcc, html, Input, Output, dash_table

# --------------------- Ajuste do caminho do CSV ---------------------
CSV_PATH = r"data/processed/netflix_clean.csv"

try:
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Ficheiro não encontrado: {CSV_PATH}. Verifique o caminho.")

# --------------------- Limpeza / Normalização ---------------------
if "release_year" in df.columns:
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce").fillna(-1).astype(int)
else:
    df["release_year"] = -1

def safe_list(x):
    if isinstance(x, list):
        return x
    if pd.isna(x):
        return ["Unknown"]
    try:
        parsed = ast.literal_eval(x)
        if isinstance(parsed, (list, tuple, set)):
            return [str(i).strip() for i in list(parsed)]
        return [str(parsed).strip()]
    except:
        try:
            return [s.strip() for s in str(x).split(",") if s.strip() != ""]
        except:
            return ["Unknown"]

if "listed_in" in df.columns:
    df["listed_in"] = df["listed_in"].apply(safe_list)
else:
    df["listed_in"] = [["Unknown"] for _ in range(len(df))]

for col in ["type", "title", "country"]:
    if col not in df.columns:
        df[col] = "Unknown"

genres = sorted({g for sublist in df["listed_in"] for g in sublist})
types = sorted(df["type"].fillna("Unknown").unique())

valid_years = df.loc[df["release_year"] >= 0, "release_year"]
year_min = int(valid_years.min()) if not valid_years.empty else 1900
year_max = int(valid_years.max()) if not valid_years.empty else 2025

def make_marks(start, end, step=5):
    marks = {y: str(y) for y in range(start, end + 1, step)}
    marks[start] = str(start)
    marks[end] = str(end)
    return marks

year_marks = make_marks(year_min, year_max, step=5 if (year_max - year_min) > 20 else 1)

# --------------------- Função principal ---------------------
def create_dashboard(app):

    app.layout = html.Div(
        className="main-container",
        children=[
            # --------------------- Logo e Grupo ---------------------
            html.Div(
                style={"textAlign": "center", "marginBottom": "20px"},
                children=[
                    html.Img(src="https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
                             style={"height": "60px"}),
                    html.H5("Grupo 7", style={"color": "#E50914", "marginTop": "5px"})
                ]
            ),

            html.H1("Dashboard Netflix", className="title", style={"textAlign": "center"}),

            # --------------------- Card com Gênero, Tipo e Ano ---------------------
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "gap": "20px", "marginBottom": "20px"},
                children=[
                    html.Div(
                        style={"flex": "1", "backgroundColor": "#2A2A2A", "padding": "20px", "borderRadius": "10px"},
                        children=[
                            html.Div(
                                style={"display": "flex", "gap": "20px"},
                                children=[
                                    html.Div([
                                        html.Label("Gênero"),
                                        dcc.Dropdown(
                                            id="genre_filter",
                                            options=[{"label": g, "value": g} for g in genres],
                                            placeholder="Escolha um gênero",
                                            multi=False
                                        )
                                    ], style={"flex": "1"}),

                                    html.Div([
                                        html.Label("Tipo"),
                                        dcc.Dropdown(
                                            id="type_filter",
                                            options=[{"label": t, "value": t} for t in types],
                                            placeholder="Movie ou TV Show",
                                            multi=False
                                        )
                                    ], style={"flex": "1"}),
                                ]
                            ),
                            html.Div([
                                html.Label("Ano de lançamento"),
                                dcc.RangeSlider(
                                    id="year_filter",
                                    min=year_min,
                                    max=year_max,
                                    value=[year_min, year_max],
                                    marks=year_marks,
                                    tooltip={"placement": "bottom", "always_visible": True}
                                )
                            ], style={"marginTop": "20px"})
                        ]
                    )
                ]
            ),

            # --------------------- KPIs ---------------------
            html.Div(
                className="kpi-container",
                style={"display": "flex", "justifyContent": "space-around", "gap": "20px", "marginBottom": "20px"},
                children=[
                    html.Div(id="kpi_total", className="kpi-card", style={"flex": "1", "textAlign": "center",
                                                                          "backgroundColor": "#2A2A2A",
                                                                          "padding": "20px", "borderRadius": "10px"}),
                    html.Div(id="kpi_movies", className="kpi-card", style={"flex": "1", "textAlign": "center",
                                                                           "backgroundColor": "#2A2A2A",
                                                                           "padding": "20px", "borderRadius": "10px"}),
                    html.Div(id="kpi_tvshows", className="kpi-card", style={"flex": "1", "textAlign": "center",
                                                                            "backgroundColor": "#2A2A2A",
                                                                            "padding": "20px", "borderRadius": "10px"}),
                ]
            ),

            # --------------------- Gráficos ---------------------
            html.Div(
                className="graphs-container",
                style={"display": "flex", "flexWrap": "wrap", "gap": "20px"},
                children=[
                    dcc.Graph(id="graph_year", className="graph-box", style={"flex": "1", "minWidth": "300px"}),
                    dcc.Graph(id="graph_genres", className="graph-box", style={"flex": "1", "minWidth": "300px"}),
                    dcc.Graph(id="graph_type_pie", className="graph-box", style={"flex": "1", "minWidth": "300px"}),
                ]
            ),

            html.Br(),

            # --------------------- Tabela ---------------------
            html.H2("Títulos Filtrados"),
            dash_table.DataTable(
                id="table_results",
                columns=[{"name": i, "id": i} for i in ["title", "type", "release_year", "country"]],
                page_size=10,
                style_table={
                    "width": "100%",
                    "overflowX": "auto",
                    "border": "1px solid #ccc",
                    "border-radius": "5px"
                },
                style_cell={
                    "textAlign": "left",
                    "padding": "5px",
                    "whiteSpace": "normal",
                    "height": "auto",
                    "color": "#ffffff",
                    "backgroundColor": "#1E1E1E"
                },
                style_header={
                    "fontWeight": "bold",
                    "backgroundColor": "#2A2A2A",
                    "color": "#E50914"
                }
            ),

            html.Br(),

            # --------------------- Insights em quadradinhos ---------------------
            html.Div(id="insights_box", className="insights",
                     style={"display": "flex", "gap": "20px", "flexWrap": "wrap"})
        ]
    )

    # --------------------- Função de filtro ---------------------
    def filter_data(selected_genre, selected_type, year_range):
        filtered = df.copy()
        if selected_genre:
            filtered = filtered[filtered["listed_in"].apply(lambda x: selected_genre in x)]
        if selected_type:
            filtered = filtered[filtered["type"] == selected_type]
        if year_range and len(year_range) == 2:
            filtered = filtered[
                (filtered["release_year"] >= year_range[0]) &
                (filtered["release_year"] <= year_range[1])
            ]
        return filtered

    # --------------------- Callbacks ---------------------
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
            html.Div([html.H4("Total de títulos"), html.H2(f"{total}")]),
            html.Div([html.H4("Filmes"), html.H2(f"{movies}")]),
            html.Div([html.H4("Séries"), html.H2(f"{tvshows}")])
        )

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
        valid = f[f["release_year"] >= 0]
        fig = px.histogram(valid, x="release_year", nbins=40, title="Títulos por ano",
                           color_discrete_sequence=["#B0B0B0"])
        fig.update_layout(
            paper_bgcolor='#121212',
            plot_bgcolor='#1E1E1E',
            font=dict(color='#E50914'),
            title_font=dict(color='#E50914'),
            xaxis=dict(color='#E50914', gridcolor='#2A2A2A'),
            yaxis=dict(color='#E50914', gridcolor='#2A2A2A')
        )
        return fig

    @app.callback(
        Output("graph_genres", "figure"),
        Input("genre_filter", "value"),
        Input("type_filter", "value"),
        Input("year_filter", "value"),
    )
    def update_graph_genres(selected_genre, selected_type, year_range):
        f = filter_data(selected_genre, selected_type, year_range)
        exploded = f.explode("listed_in")
        counts = exploded["listed_in"].value_counts().reset_index()
        counts.columns = ["Género", "Quantidade"]
        fig = px.bar(counts, x="Género", y="Quantidade", title="Distribuição dos Géneros",
                     color_discrete_sequence=["#B0B0B0"])
        fig.update_layout(
            paper_bgcolor='#121212',
            plot_bgcolor='#1E1E1E',
            font=dict(color='#E50914'),
            title_font=dict(color='#E50914'),
            xaxis=dict(color='#E50914', gridcolor='#2A2A2A'),
            yaxis=dict(color='#E50914', gridcolor='#2A2A2A'),
            xaxis_tickangle=45,
            height=500
        )
        return fig

    @app.callback(
        Output("graph_type_pie", "figure"),
        Input("genre_filter", "value"),
        Input("type_filter", "value"),
        Input("year_filter", "value"),
    )
    def update_pie(selected_genre, selected_type, year_range):
        f = filter_data(selected_genre, selected_type, year_range)
        type_counts = f["type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        colors = ["#B0B0B0" if t.lower() == "movie" else "#E50914" for t in type_counts["type"]]
        fig = px.pie(type_counts, names="type", values="count", title="Distribuição: Filmes vs Séries",
                     color_discrete_sequence=colors)
        fig.update_layout(
            paper_bgcolor='#121212',
            plot_bgcolor='#1E1E1E',
            font=dict(color='#E50914'),
            title_font=dict(color='#E50914')
        )
        return fig

    @app.callback(
        Output("table_results", "data"),
        Input("genre_filter", "value"),
        Input("type_filter", "value"),
        Input("year_filter", "value"),
    )
    def update_table(selected_genre, selected_type, year_range):
        f = filter_data(selected_genre, selected_type, year_range)
        table_df = f[["title", "type", "release_year", "country"]].fillna("Unknown")
        return table_df.to_dict("records")

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
        
        top_country = f["country"].mode()[0] if not f["country"].mode().empty else "N/A"
        top_year = int(f.loc[f["release_year"] >= 0, "release_year"].mode()[0]) \
            if not f.loc[f["release_year"] >= 0, "release_year"].mode().empty else "N/A"
        total_titles = len(f)

        # Quadradinhos de insights
        return [
            html.Div([html.H4("País com mais títulos"), html.H3(f"{top_country}")],
                     style={"flex": "1", "backgroundColor": "#2A2A2A", "padding": "15px", "borderRadius": "10px", "textAlign": "center"}),
            html.Div([html.H4("Ano mais comum"), html.H3(f"{top_year}")],
                     style={"flex": "1", "backgroundColor": "#2A2A2A", "padding": "15px", "borderRadius": "10px", "textAlign": "center"}),
            html.Div([html.H4("Número total de títulos"), html.H3(f"{total_titles}")],
                     style={"flex": "1", "backgroundColor": "#2A2A2A", "padding": "15px", "borderRadius": "10px", "textAlign": "center"})
        ]
