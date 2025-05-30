# %%TestChaange
import sqlite3 #package für SQL databank
import pandas as pd #panda für tabellennutzung# %%
# %%
# Load CSV files into pandas DataFrames i.e. einzelne Dateien in eine Datenbank schreiben
csv_Kunden = pd.read_csv("Kunden.csv", sep=";", encoding="utf-8") # pd.read befehl kommt aus panda packes
csv_Standort = pd.read_csv("Standorte.csv", sep=";", encoding="utf-8")
csv_Verkaufszahlen = pd.read_csv("Verkaufszahlen.csv", sep=";", encoding="utf-8")
csv_Produkte = pd.read_csv("Produkte.csv", sep=";", encoding="utf-8")
# %%
#  SQL Database verbindung wird hergestellt, wenn Name "store_verkaeufe" nicht existiert, wird es kreiert)
con = sqlite3.connect('store_verkaeufe.db') 

# %%
csv_Kunden.to_sql("Kunden", con, if_exists="replace", index=False)
csv_Standort.to_sql("Standorte", con, if_exists="replace", index=False)
csv_Verkaufszahlen.to_sql("Verkaufszahlen", con, if_exists="replace", index=False)
csv_Produkte.to_sql("Produkte", con, if_exists="replace", index=False)

# %%
# Query data back from the database

def get_data():
    con = sqlite3.connect('store_verkaeufe.db')

    Kunden = pd.read_sql_query("SELECT * FROM Kunden", con)
    Standorte = pd.read_sql_query("SELECT * FROM Standorte", con)
    Verkaufszahlen = pd.read_sql_query("SELECT * FROM Verkaufszahlen", con)
    Produkte = pd.read_sql_query("SELECT * FROM Produkte", con)

    con.close()

    return Kunden, Standorte, Verkaufszahlen, Produkte
# %%
con.close()

# %%
