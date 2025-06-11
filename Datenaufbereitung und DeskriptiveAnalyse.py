#%%

import pandas as pd
from create_db_mode import get_data
import plotnine as p9

Kunden, Standorte, Verkaufszahlen, Produkte = get_data()

#%% Verkaufszahlen aggregiert nach Region, Produktgruppe und Monat
# Datumsformat normalisieren und Monat extrahieren

Verkaufszahlen["Tag"] = pd.to_datetime(Verkaufszahlen["Tag"])
Verkaufszahlen["Monat"] = Verkaufszahlen["Tag"].dt.to_period("M").astype(str)

# Tabellen mergen

df_merged = (
    Verkaufszahlen
    .merge(Produkte, on="ProduktID", how="left")
    .merge(Kunden, on="KundenID", how="left")
    .merge(Standorte, on="OrtID", how="left")
)

 

#%%Gruppierung nach Region, Produktgruppe und Monat

agg_RPM = (
    df_merged
    .groupby(["Region", "Produktgruppe", "Monat"], as_index=False)
    .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
)

# %%  Durchschnittliche Verkaufsmenge pro Produktgruppe (pro einzelnen Verkauf)

mw_Produktgruppe = (
    df_merged
    .groupby("Produktgruppe", as_index=False)
    .agg(Durchschnitt=("Verkaufsmenge", "mean"))
)

# %%Top 10 meistverkaufte Produkte (gesamt)

top_produkte = (
    df_merged
    .groupby(["ProduktID", "Marke", "Produktgruppe"], as_index=False)
    .agg(Gesamtverkäufe=("Verkaufsmenge", "sum"))
    .sort_values("Gesamtverkäufe", ascending=False)
    .head(10)
)

# %% Die 10 am wenigsten verkauften Produkte (gesamt) 

bottom_produkte = (
    df_merged
    .groupby(["ProduktID", "Marke", "Produktgruppe"], as_index=False)
    .agg(Gesamtverkäufe=("Verkaufsmenge", "sum"))
    .sort_values("Gesamtverkäufe", ascending=True)
    .head(10)
)
 

#%% . Verteilung der Verkäufe nach Geschlecht des Produkts

sales_Geschlecht = (
    df_merged
    .groupby("Geschlecht_x", as_index=False)  # Geschlecht aus Produkttabelle
    .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
    .rename(columns={"Geschlecht_x": "Produkt_Geschlecht"})
)

#%% Monatliche Gesamtverkäufe (Zeitreihe)

monatliche_sales = (
    df_merged
    .groupby("Monat", as_index=False)
    .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
    .sort_values("Monat")
)

# %% . Angeschaut was in den Tabellen steht

print(agg_RPM)
print(mw_Produktgruppe)
print(top_produkte)
print(bottom_produkte)
print(monatliche_sales)
print(sales_Geschlecht)

# %%. Deskriptive Analyse- Visualisierungen 

######1.Erstellen eines Balkendiagramm (Anteil Geschlecht an Verkauf)

plot_sales_Geschlecht= (
    p9.ggplot(sales_Geschlecht, p9.aes(x="Produkt_Geschlecht", y="Verkaufsmenge", fill="Produkt_Geschlecht")) +
    p9.geom_col(show_legend=False) +
    p9.ggtitle("Verkäufe nach Produkt-Geschlecht") +
    p9.theme(axis_text_x=p9.element_text(rotation=45, hjust=1))
)

plot_sales_Geschlecht.draw()
 

#%%

##### 2.Erstellen eines Liniendiagramms zu jeder Produktgruppe aufgeteilt nach Region an einer Zeitachse

agg_RPM["Monat"] = pd.to_datetime(agg_RPM["Monat"])
agg_RPM = agg_RPM.sort_values("Monat")

produktgruppen = agg_RPM["Produktgruppe"].unique()

for gruppe in produktgruppen:
    df_gruppe = agg_RPM[agg_RPM["Produktgruppe"] == gruppe]


    plot = (
        p9.ggplot(df_gruppe, p9.aes(x="Monat", y="Verkaufsmenge", color="Region")) +
        p9.geom_line(size=1.2) +
        p9.scale_x_datetime(
            breaks=agg_RPM["Monat"],
            date_labels="%b %Y"
        ) +
        p9.ggtitle(f"Monatliche Verkaufsmenge – {gruppe}") +
        p9.xlab("Monat") +
        p9.ylab("Verkaufsmenge") +
        p9.theme(
            axis_text_x=p9.element_text(rotation=45, hjust=1, size=9),
            axis_text_y=p9.element_text(size=9),
            panel_grid_major=p9.element_line(color="gray"),
            panel_grid_minor=p9.element_line(color="gray", linetype="dashed"),
            panel_background=p9.element_rect(fill="white"),
            figure_size=(11, 5)
        )
    )

dateiname=f"diagramm_{gruppe.replace('','_')}.pdf"
plot.save(dateiname)
plot.draw()


#%%

##### 3.Zeitreihendiagramm zu Monatlichen Sales


monatliche_sales["Monat"] = pd.to_datetime(monatliche_sales["Monat"])


plot_monate = (
    p9.ggplot(monatliche_sales, p9.aes(x="Monat", y="Verkaufsmenge")) +
    p9.geom_line(color="steelblue", size=1) +
    p9.geom_point(color="darkblue", size=2) +  
    p9.scale_x_datetime(
        date_labels="%Y-%m",  
        date_breaks="1 month"  
    ) +
    p9.ggtitle("Monatliche Gesamtverkäufe") +
    p9.xlab("Monat") +
    p9.ylab("Verkaufsmenge") +
    p9.theme(
        axis_text_x=p9.element_text(rotation=45, hjust=1),
        panel_grid_major=p9.element_line(color="gray", size=0.5),
        panel_grid_minor=p9.element_line(color="gray", size=0.3),
        panel_background=p9.element_rect(fill="white"),
        figure_size=(10, 5)
    )
)

plot_monate.draw()
 

#%%

## 4.Balkendiagramm Top 10 Produkte

plot_top = (
    p9.ggplot(top_produkte, p9.aes(x="reorder(ProduktID, Gesamtverkäufe)", y="Gesamtverkäufe", fill="Marke")) +
    p9.geom_col() +
    p9.geom_text(p9.aes(label="Gesamtverkäufe"), va="bottom", size=10) +
    p9.ggtitle("Top 10 meistverkaufte Produkte") +
    p9.xlab("ProduktID") +
    p9.ylab("Gesamtverkäufe") +
    p9.coord_cartesian(ylim=(3120,3205))+
    p9.theme(
        axis_text_x=p9.element_text(rotation=45, hjust=1),
        panel_grid_major=p9.element_line(color="gray", size=0.5),
        panel_background=p9.element_rect(fill="white")
    )
)
 

plot_top.draw()


#%%

## 5. Balkendiagramm: Die 10 am wenigsten verkauften Produkte

plot_bottom = (
    p9.ggplot(bottom_produkte, p9.aes(x="reorder(ProduktID, Gesamtverkäufe)", y="Gesamtverkäufe", fill="Marke")) +
    p9.geom_col() +
    p9.geom_text(p9.aes(label="Gesamtverkäufe"), va="bottom", size=10) +
    p9.ggtitle("Die 10 am wenigsten verkauften Produkte") +
    p9.xlab("ProduktID") +
    p9.ylab("Gesamtverkäufe") +
    p9.coord_cartesian(ylim=(2660,2860))+
    p9.theme(
        axis_text_x=p9.element_text(rotation=45, hjust=1),
        panel_grid_major=p9.element_line(color="gray", size=0.5),
        panel_background=p9.element_rect(fill="white")
    )
)
 

plot_bottom.draw()


#%%

## 6. Balkendiagramm: Durchschnittlicher Verkauf


mw_Produktgruppe["Durchschnitt2"] = round(pd.to_numeric(mw_Produktgruppe["Durchschnitt"]),2)
plot_mean = (
    p9.ggplot(mw_Produktgruppe, p9.aes(x="reorder(Produktgruppe, Durchschnitt)", y="Durchschnitt", fill="Produktgruppe")) +
    p9.geom_col(show_legend=False) +
    p9.geom_text(p9.aes(label="Durchschnitt2"), va="bottom", size=10) +
    p9.ggtitle("Durchschnittliche Verkaufsmenge pro Produktgruppe") +
    p9.xlab("Produktgruppe") +
    p9.ylab("Durchschnitt") +
    p9.coord_cartesian(ylim=(2.97,3.03))+
    p9.theme(
        axis_text_x=p9.element_text(rotation=45, hjust=1),
        panel_grid_major=p9.element_line(color="gray", size=0.5),
        panel_background=p9.element_rect(fill="white")
    )
)


plot_mean.draw()

# %%
