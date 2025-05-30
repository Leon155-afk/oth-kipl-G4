# %%
import pandas as pd
import statsmodels.api as sm
from create_db_mode import get_data
from plotnine import ggplot, aes, geom_line, geom_point, labs, theme_minimal, ggtitle

# %%
# Daten aus SQLite-Datenbank laden
Kunden, Standorte, Verkaufszahlen, Produkte = get_data()

# %%
# Datum vorbereiten
Verkaufszahlen["Tag"] = pd.to_datetime(Verkaufszahlen["Tag"])
Verkaufszahlen["Monat"] = Verkaufszahlen["Tag"].dt.to_period("M").astype(str)

# %%
# Merge mit Produktdaten und Standortdaten, Gruppierung
df = (
    Verkaufszahlen
    .merge(Produkte, on="ProduktID", how="left")
    .merge(Standorte, on="OrtID", how="left")
    .groupby(["Region", "Produktgruppe", "Monat"], as_index=False)
    .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
)

# %%
# Alle gültigen Kombinationen (Region, Produktgruppe) ermitteln
valid_combinations = df[["Region", "Produktgruppe"]].drop_duplicates().reset_index(drop=True)

# %%
# Automatisch erste Kombination wählen
region = valid_combinations.loc[0, "Region"]
produktgruppe = valid_combinations.loc[0, "Produktgruppe"]
print(f"Ausgewählte Kombination für Prognose: Region = '{region}', Produktgruppe = '{produktgruppe}'")


# %%
# Daten für die ausgewählte Kombination filtern und sortieren
df_subset = df[(df["Region"] == region) & (df["Produktgruppe"] == produktgruppe)].copy()
df_subset = df_subset.sort_values("Monat").reset_index(drop=True)

# %%
# Lineare Zeitachse erstellen
df_subset["Monat_num"] = range(len(df_subset))

# %%
# Regression nur wenn genügend Daten vorhanden sind
if len(df_subset) < 2:
    print("Nicht genug Daten für Regression und Prognose.")
else:
    X = sm.add_constant(df_subset["Monat_num"])
    y = df_subset["Verkaufsmenge"]
    model = sm.OLS(y, X).fit()

# %%
# Prognose für nächste 6 Monate
    forecast_rows = []
    for i in range(1, 7):
        monat_num = len(df_subset) + i - 1
        y_pred = model.predict([1, monat_num])[0]
        forecast_rows.append({
            "Region": region,
            "Produktgruppe": produktgruppe,
            "Monat": f"Zukunft +{i}",
            "Monat_num": monat_num,
            "Verkaufsmenge": y_pred
        })

    df_forecast = pd.DataFrame(forecast_rows)

# %%
    # Kombinierte Daten für Plot
    df_combined = pd.concat([df_subset, df_forecast], ignore_index=True)

# %%
   # Plot erstellen
    plot = (
        ggplot(df_combined, aes(x="Monat_num", y="Verkaufsmenge")) +
        geom_line(color="blue") +
        geom_point(color="red") +
        labs(x="Monate", y="Verkaufsmenge") +
        ggtitle(f"Prognose für '{produktgruppe}' in Region '{region}'") +
        theme_minimal()
    )

    print(plot)
    # bis hier Prognose für Bluse in Region Nord




# %%
# Prognose Bluse in Region Ost
region = "Ost"
produktgruppe = "Bluse"

df_subset = df[(df["Region"] == region) & (df["Produktgruppe"] == produktgruppe)].copy()
df_subset = df_subset.sort_values("Monat").reset_index(drop=True)
df_subset["Monat_num"] = range(len(df_subset))

# %%
if len(df_subset) < 2:
    print(f"Nicht genug Daten für Prognose: Bluse in Region {region}")
else:
    X = sm.add_constant(df_subset["Monat_num"])
    y = df_subset["Verkaufsmenge"]
    model = sm.OLS(y, X).fit()

# %%
forecast_rows = []
for i in range(1, 7):  # 6 Monate Prognose
        monat_num = len(df_subset) + i - 1
        y_pred = model.predict([1, monat_num])[0]
        forecast_rows.append({
            "Region": region,
            "Produktgruppe": produktgruppe,
            "Monat": f"Zukunft +{i}",
            "Monat_num": monat_num,
            "Verkaufsmenge": y_pred
        })
df_forecast = pd.DataFrame(forecast_rows)
df_combined = pd.concat([df_subset, df_forecast], ignore_index=True)

# %%
plot = (
        ggplot(df_combined, aes(x="Monat_num", y="Verkaufsmenge")) +
        geom_line(color="blue") +
        geom_point(color="red") +
        labs(x="Monate", y="Verkaufsmenge") +
        ggtitle(f"Prognose Bluse in Region {region}") +
        theme_minimal()
)
print(plot)
# bis hier Prognose Bluse in Region Ost




# %%
# Daten aggregieren nach Marke und Monat
df_marke = (
    Verkaufszahlen
    .merge(Produkte, on="ProduktID", how="left")
    .groupby(["Marke", "Monat"], as_index=False)
    .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
)

marke = "Adidas"
df_subset = df_marke[df_marke["Marke"] == marke].copy()
df_subset = df_subset.sort_values("Monat").reset_index(drop=True)
df_subset["Monat_num"] = range(len(df_subset))

# %%
if len(df_subset) < 2:
    print(f"Nicht genug Daten für Prognose Marke {marke}")
else:
    X = sm.add_constant(df_subset["Monat_num"])
    y = df_subset["Verkaufsmenge"]
    model = sm.OLS(y, X).fit()

    forecast_rows = []
    for i in range(1, 7):  # 6 Monate Prognose
        monat_num = len(df_subset) + i - 1
        y_pred = model.predict([1, monat_num])[0]
        forecast_rows.append({
            "Marke": marke,
            "Monat": f"Zukunft +{i}",
            "Monat_num": monat_num,
            "Verkaufsmenge": y_pred
        })
    df_forecast = pd.DataFrame(forecast_rows)
    df_combined = pd.concat([df_subset, df_forecast], ignore_index=True)

# %%
    plot = (
        ggplot(df_combined, aes(x="Monat_num", y="Verkaufsmenge")) +
        geom_line(color="blue") +
        geom_point(color="red") +
        labs(x="Monate", y="Verkaufsmenge") +
        ggtitle(f"Prognose Verkaufszahlen Marke '{marke}'") +
        theme_minimal()
    )
    print(plot)

# bis hier Prognose Verkaufszahlen Marke Adidas



# %%
# Daten aggregieren nach Marke und Monat (nur Puma)
df_marke = (
    Verkaufszahlen
    .merge(Produkte, on="ProduktID", how="left")
    .groupby(["Marke", "Monat"], as_index=False)
    .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
)

# %%
marke = "Puma"
df_subset = df_marke[df_marke["Marke"] == marke].copy()
df_subset = df_subset.sort_values("Monat").reset_index(drop=True)
df_subset["Monat_num"] = range(len(df_subset))

if len(df_subset) < 2:
    print(f"Nicht genug Daten für Prognose Marke {marke}")
else:
    X = sm.add_constant(df_subset["Monat_num"])
    y = df_subset["Verkaufsmenge"]
    model = sm.OLS(y, X).fit()

    forecast_rows = []
    for i in range(1, 7):  # 6 Monate Prognose
        monat_num = len(df_subset) + i - 1
        y_pred = model.predict([1, monat_num])[0]
        forecast_rows.append({
            "Marke": marke,
            "Monat": f"Zukunft +{i}",
            "Monat_num": monat_num,
            "Verkaufsmenge": y_pred
        })
    df_forecast = pd.DataFrame(forecast_rows)
    df_combined = pd.concat([df_subset, df_forecast], ignore_index=True)

# %%
    plot = (
        ggplot(df_combined, aes(x="Monat_num", y="Verkaufsmenge")) +
        geom_line(color="blue") +
        geom_point(color="red") +
        labs(x="Monate", y="Verkaufsmenge") +
        ggtitle(f"Prognose Verkaufszahlen Marke '{marke}'") +
        theme_minimal()
    )
    print(plot)

# bis hier Prognose Verkaufszahlen Marke Puma





# %%
# Verkaufszahlen nach Geschlecht aggregieren - nur Männer auswählen
df_geschlecht = (
    Verkaufszahlen
    .merge(Produkte, on="ProduktID", how="left")
    .groupby(["Geschlecht", "Monat"], as_index=False)
    .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
)

geschlecht = "Männer"  # Nur Männer

df_subset = df_geschlecht[df_geschlecht["Geschlecht"] == geschlecht].copy()
df_subset = df_subset.sort_values("Monat").reset_index(drop=True)
df_subset["Monat_num"] = range(len(df_subset))

if len(df_subset) < 2:
    print(f"Nicht genug Daten für Prognose Geschlecht {geschlecht}")
else:
    X = sm.add_constant(df_subset["Monat_num"])
    y = df_subset["Verkaufsmenge"]
    model = sm.OLS(y, X).fit()

    forecast_rows = []
    for i in range(1, 7):  # 6 Monate Prognose
        monat_num = len(df_subset) + i - 1
        y_pred = model.predict([1, monat_num])[0]
        forecast_rows.append({
            "Geschlecht": geschlecht,
            "Monat": f"Zukunft +{i}",
            "Monat_num": monat_num,
            "Verkaufsmenge": y_pred
        })
    df_forecast = pd.DataFrame(forecast_rows)
    df_combined = pd.concat([df_subset, df_forecast], ignore_index=True)

# %%
    plot = (
        ggplot(df_combined, aes(x="Monat_num", y="Verkaufsmenge")) +
        geom_line(color="blue") +
        geom_point(color="red") +
        labs(x="Monate", y="Verkaufsmenge") +
        ggtitle(f"Prognose Verkaufszahlen für Männer") +
        theme_minimal()
    )
    print(plot)

# bis hier Prognose Verkaufszahlen für Männer




# %%
# Nur Produkt-Geschlecht = 'Frauen'
df_geschlecht = (
    Verkaufszahlen
    .merge(Produkte, on="ProduktID", how="left")
    .query("Geschlecht == 'Frauen'")
    .groupby(["Geschlecht", "Monat"], as_index=False)
    .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
)

df_subset = df_geschlecht.copy()
df_subset = df_subset.sort_values("Monat").reset_index(drop=True)
df_subset["Monat_num"] = range(len(df_subset))

if len(df_subset) < 2:
    print("Nicht genug Daten für Prognose Frauen")
else:
    X = sm.add_constant(df_subset["Monat_num"])
    y = df_subset["Verkaufsmenge"]
    model = sm.OLS(y, X).fit()

    forecast_rows = []
    for i in range(1, 7):  # 6 Monate Prognose
        monat_num = len(df_subset) + i - 1
        y_pred = model.predict([1, monat_num])[0]
        forecast_rows.append({
            "Geschlecht": "Frauen",
            "Monat": f"Zukunft +{i}",
            "Monat_num": monat_num,
            "Verkaufsmenge": y_pred
        })
    df_forecast = pd.DataFrame(forecast_rows)
    df_combined = pd.concat([df_subset, df_forecast], ignore_index=True)

# %%
    plot = (
        ggplot(df_combined, aes(x="Monat_num", y="Verkaufsmenge")) +
        geom_line(color="blue") +
        geom_point(color="red") +
        labs(x="Monate", y="Verkaufsmenge") +
        ggtitle(f"Prognose Verkaufszahlen für Frauen") +
        theme_minimal()
    )
    print(plot)

# bis hier Prognose Verkaufszahlen für Frauen





# %%
