# 🎬 Dashboard Netflix: Storytelling com Dados

Dashboard interativo que analisa as **8 800+ produções** do catálogo da Netflix (dataset público do Kaggle) para responder a perguntas de negócio sobre a evolução da plataforma.

> Projeto de grupo, desenvolvido na formação em Análise de Dados (IEFP Porto).
> Autores: **Maria Vita**, Caroline Costa e André Costa.

<!-- Adicionar aqui uma captura do dashboard: ![Dashboard](docs/dashboard.png) -->

## ❓ Perguntas de análise

1. Quantos títulos foram lançados ao longo dos anos?
2. Há mais filmes ou mais séries, e em que proporção?
3. Quais são os géneros mais populares?
4. Como variam os géneros e os tipos de conteúdo ao longo do tempo?
5. Que países produzem mais títulos?

## 💡 Principais conclusões

| Conclusão | Detalhe |
|---|---|
| **Os filmes dominam o catálogo** | ~70% filmes vs ~30% séries |
| **O crescimento acelera a partir de 2015** | 2018 e 2019 são os anos com mais lançamentos, em linha com a expansão global da Netflix |
| **Os conteúdos internacionais e a comédia têm grande peso** | O top 5 de géneros é: Documentários, Stand-Up Comedy, Dramas, International TV Shows e Comédias |

A análise completa está em [`docs/storytelling.md`](docs/storytelling.md).

## 📊 Funcionalidades do dashboard

- **Filtros:** género, tipo (filme/série) e intervalo de anos
- **KPIs:** total de títulos, número de filmes e número de séries
- **Gráficos:** títulos por ano, distribuição de géneros e filmes vs séries
- **Tabela** interativa com pesquisa
- **Painel de insights** que se atualiza com os filtros

## 🛠 Tecnologias

Python · pandas · NumPy · Plotly · Dash · Dash Bootstrap Components · Git/GitHub

## 🗂 Estrutura

```
├── app.py               # Ponto de entrada da aplicação
├── src/
│   ├── cleaning.py      # Limpeza e tratamento dos dados
│   ├── analysis.py      # Cálculos e agregações
│   └── dashboard.py     # Layout e interatividade (callbacks)
├── data/
│   ├── raw/             # Dados originais (Kaggle)
│   └── processed/       # Dados tratados
├── assets/style.css     # Estilos do dashboard
└── docs/storytelling.md # Narrativa e conclusões
```

## ▶️ Como executar

```bash
pip install -r requirements.txt
python app.py
```

Depois, abra `http://127.0.0.1:8050` no navegador.

## 📁 Fonte dos dados

[Netflix Movies and TV Shows (Kaggle)](https://www.kaggle.com/datasets/shivamb/netflix-shows)
