import pandas as pd

def clean_data(df):
    df = df.drop_duplicates()
    df["release_year"] = df["release_year"].astype(int)
    df["listed_in"] = df["listed_in"].apply(lambda x: x.split(","))
    return df

if __name__ == "__main__":
    raw = pd.read_csv(r"C:\Users\Evita\Downloads\Atividade3\storytelling-dados-grupo7\data\raw\netflix_titles.csv")
    cleaned = clean_data(raw)
    cleaned.to_csv(r"C:\Users\Evita\Downloads\Atividade3\storytelling-dados-grupo7\data\processed\netflix_clean.csv", index=False)
