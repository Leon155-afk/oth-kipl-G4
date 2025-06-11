#Importe
# %%
import streamlit as st
import pandas as pd
from create_db_mode import get_data
import plotnine as p9
import plotly.express as px
import statsmodels.api as sm
from plotnine import ggplot, aes, geom_line, geom_point, labs, theme_minimal, ggtitle, theme

#Seiteneinstellungen & Einleitung
# %%
st.set_page_config(page_title="Sho.py Dashboard", page_icon="🛍️", layout="wide")

st.title("Sho.py Dashboard 🛍️")
st.subheader("Ein datengetriebenes Analyse- und Prognosesystem für unsere Sho.py Filialen")
st.write ("""
          Unser fiktiver Shop **"Sho.py"** ist in den vier Regionen **Nord, Ost, Süd und West** aktiv.
          In dieser Anwendung analysieren wir Verkaufszahlen, Markenpräferenzen und weitere relevante Faktoren, um betriebswirtschaftliche Entscheidungen datenbasiert zu unterstützen.
          
          Neben deskriptiven Auswertungen bietet das Sho.py Dashboard auch **Prognosen**, z.B. zur Entwicklung der Verkaufszahlen.  
          
          Ziel ist es, datenbasierte Einblicke und Entscheidungsgrundlagen für Marketing, Einkauf und Planung bereitzustellen.
          """)
# %%
# Tabstruktur (Deskriptive Analyse | Prognosen)
tab1, tab3 = st.tabs(["**Deskriptive Analyse**", "**Prognosen**"])

#TAB1: Deskriptive Analyse
with tab1:
    col1, col2 = st.columns([3,1])
    with col1: 
        st.title("Deskriptive Analyse")
        #Daten laden | Mergen der Tabellen | Aggregation
        Kunden, Standorte, Verkaufszahlen, Produkte = get_data()
        Verkaufszahlen["Tag"] = pd.to_datetime(Verkaufszahlen["Tag"])
        Verkaufszahlen["Monat"] = Verkaufszahlen["Tag"].dt.to_period("M").astype(str)
    
        df_merged = (
         Verkaufszahlen
            .merge(Produkte, on="ProduktID", how="left")
            .merge(Kunden, on="KundenID", how="left")
            .merge(Standorte, on="OrtID", how="left")
            )
    
        monatliche_sales = (
        df_merged
            .groupby("Monat", as_index=False)
            .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
            .sort_values("Monat")
            )

#Gesamtverkäufe nach Monat (Jahr 2024)
        st.subheader("Gesamtverkäufe 2024")
        #Auswahlfilter: Monate
        selected_monate=st.multiselect(
            "Monate auswählen", 
            options=monatliche_sales["Monat"].unique().tolist(), 
            default=monatliche_sales["Monat"].unique().tolist()
            )

        filtered_sales = monatliche_sales[monatliche_sales["Monat"].isin(selected_monate)]

        # Plot mit Plotly
        plot_monate = px.line(filtered_sales, x="Monat", y="Verkaufsmenge", markers=True)
        plot_monate.update_layout(
            xaxis_title="Monat",
            xaxis_title_font=dict(size=20),
            xaxis=dict(tickfont=dict(size=18)),
            yaxis_title="Verkaufsmenge",
            yaxis_title_font=dict(size=20),
            yaxis=dict(tickfont=dict(size=18))
        )
        st.plotly_chart(plot_monate, use_container_width=True)
        
    with col2: 
    #Gesamtverkäufe im Überblick - Kennzahlen (Metriken rechts)
        st.title("")
        st.subheader ("im Überblick")
        
        st.metric(label="Gesamte Verkaufsmenge 2024", value=f"{monatliche_sales["Verkaufsmenge"].sum():,.0f}".replace(",","."), border=True)
        st.metric(label="Monatsdurchschnitt 2024", value=f"{monatliche_sales["Verkaufsmenge"].mean():,.0f}".replace(",","."), border=True)
        st.metric(label="Top Verkaufsmonat", value="25.916", delta="+ Januar 2024", border=True)
        st.metric(label="Flop Verkaufsmonat", value="23.534", delta="- Februar 2024", border=True)
    
    st.divider()
#Top 10 meistverkauftesten Produkte & am wenigsten verkaufte Produkte
    st.subheader("Top 10 meistverkauften Produkte & am wenigsten verkaufte Produkte")
    col1, col2 = st.columns(2)
    #Top 10
    with col1: 
        top_produkte = (
        df_merged
            .groupby(["ProduktID", "Marke", "Produktgruppe"], as_index=False)
            .agg(Gesamtverkäufe=("Verkaufsmenge", "sum"))
            .sort_values("Gesamtverkäufe", ascending=False)
            .head(10)
            )
        
        plot_top = (
            p9.ggplot(top_produkte, p9.aes(x="reorder(ProduktID, Gesamtverkäufe)", y="Gesamtverkäufe", fill="Marke")) +
            p9.geom_col() +
            p9.geom_text(p9.aes(label="Gesamtverkäufe"), va="bottom", size=7) +
            p9.ggtitle("Top 10") +
            p9.xlab("ProduktID") +
            p9.ylab("Gesamtverkäufe") +
            p9.coord_cartesian(ylim=(3000,3250))+
            p9.theme(
                plot_title=p9.element_text(size=8),
                axis_text_x=p9.element_text(size=6, rotation=45, hjust=1),
                axis_text_y=p9.element_text(size=6),
                axis_title_x=p9.element_text(size=8),
                axis_title_y=p9.element_text(size=8),
                legend_title=p9.element_text(size=10),
                legend_text=p9.element_text(size=8),
                panel_grid_major_y=p9.element_line(color="gray", size=0.5),
                panel_grid_major_x=p9.element_blank(),
                panel_background=p9.element_rect(fill="white"),
                figure_size=(11, 5))
            )


        fig=plot_top.draw(show=False)
        st.pyplot(fig)


#%%
    #Flop 10
    with col2:
        bottom_produkte = (
            df_merged
            .groupby(["ProduktID", "Marke", "Produktgruppe"], as_index=False)
            .agg(Gesamtverkäufe=("Verkaufsmenge", "sum"))
            .sort_values("Gesamtverkäufe", ascending=True)
            .head(10)
            )

        plot_bottom = (
            p9.ggplot(bottom_produkte, p9.aes(x="reorder(ProduktID, Gesamtverkäufe)", y="Gesamtverkäufe", fill="Marke")) +
            p9.geom_col() +
            p9.geom_text(p9.aes(label="Gesamtverkäufe"), va="bottom", size=7) +
            p9.ggtitle("Flop 10") +
            p9.xlab("ProduktID") +
            p9.ylab("Gesamtverkäufe") +
            p9.coord_cartesian(ylim=(2650,2900))+
            p9.theme(
                plot_title=p9.element_text(size=8),
                axis_text_x=p9.element_text(size=6, rotation=45, hjust=1),
                axis_text_y=p9.element_text(size=6),
                axis_title_x=p9.element_text(size=8),
                axis_title_y=p9.element_text(size=8),
                legend_title=p9.element_text(size=10),
                legend_text=p9.element_text(size=8),
                panel_grid_major_y=p9.element_line(color="gray", size=0.5),
                panel_grid_major_x=p9.element_blank(),
                panel_background=p9.element_rect(fill="white"),
                figure_size=(11, 5))
            )
        fig=plot_bottom.draw(show=False)
        st.pyplot(fig)

    st.divider()
#Liniendiagramm zu jeder Produktgruppe aufgeteilt nach Region
    st.subheader("Monatliche Verkaufsmenge nach Region & Produktgruppe")
    agg_RPM = (
        df_merged
        .groupby(["Region", "Produktgruppe", "Monat"], as_index=False)
        .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
        )
    agg_RPM["Monat"] = pd.to_datetime(agg_RPM["Monat"])
    agg_RPM = agg_RPM.sort_values("Monat")

    produktgruppen = agg_RPM["Produktgruppe"].unique().tolist()
    selected_gruppen = st.selectbox(
        "Produktgruppen auswählen:",
        options=produktgruppen
        )

    df_gruppe = agg_RPM[agg_RPM["Produktgruppe"] == selected_gruppen]

    plot = px.line(
        df_gruppe, 
        x="Monat", 
        y="Verkaufsmenge", 
        color="Region", 
        text="Verkaufsmenge"
        )
    
    plot.update_traces(
        texttemplate='%{text:.0f}', 
        textposition='top center',
        textfont_size=18
        )
    
    plot.update_layout(
        height=420,
        title=f"Verkaufsmenge – {selected_gruppen} nach Region",
        xaxis=dict(
            title=dict(
                text="Monat",
                font=dict(size=20)
            ),
            tickfont=dict(size=18)
        ),
        yaxis=dict(
            title=dict(
                text="Verkaufsmenge",
                font=dict(size=20)
            ),
            tickfont=dict(size=18)
        ),
        legend=dict(
            title=dict(font=dict(size=20)),
            font=dict(size=18)
        )
    )

    st.plotly_chart(plot, use_container_width=True)

    st.divider()
#Balkendiagramm (Verkäufe nach Produkt-Geschlecht)
    st.subheader("Verkaufsmenge nach Produkt-Geschlecht")
    
    sales_Geschlecht = (
        df_merged
            .groupby("Geschlecht_x", as_index=False)  # Geschlecht aus Produkttabelle
            .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
            .rename(columns={"Geschlecht_x": "Produkt_Geschlecht"})
        )

    plot_sales_Geschlecht= px.bar(sales_Geschlecht, x="Produkt_Geschlecht", y="Verkaufsmenge",color="Produkt_Geschlecht", text="Verkaufsmenge")

    plot_sales_Geschlecht.update_traces(
        texttemplate='%{text:.0f}', 
        textfont_size=18
        )
    plot_sales_Geschlecht.update_layout(
            xaxis_title="Produkt_Geschlecht",
            xaxis_title_font=dict(size=20),
            xaxis=dict(
                tickfont=dict(size=18)
            ),

            yaxis_title="Verkaufsmenge",
            yaxis_title_font=dict(size=20),
            yaxis=dict(
                tickfont=dict(size=18)
            ),
            legend=dict(
                title=dict(font=dict(size=20)),
                font=dict(size=18)
            )
        )
    st.plotly_chart(plot_sales_Geschlecht, use_container_width=True)

    st.divider()
#Balkendiagramm (Durchschnittliche Verkaufsmenge nach Produktgruppe)
    st.subheader("Durchschnittliche Verkaufsmenge nach Produktgruppe")
    mw_Produktgruppe = (
        df_merged
        .groupby("Produktgruppe", as_index=False)
        .agg(Durchschnitt=("Verkaufsmenge", "mean"))
        )
    plot_mean= px.bar(mw_Produktgruppe, x="Produktgruppe", y="Durchschnitt",color="Produktgruppe", text="Durchschnitt")
    plot_mean.update_yaxes(range=[2.96,3.04])
    plot_mean.update_traces(
        texttemplate='%{text:.3f}',
        textfont_size=18
        )
    plot_mean.update_layout(
            xaxis_title="Produktgruppe",
            xaxis_title_font=dict(size=20),
            xaxis=dict(
                tickfont=dict(size=18)
            ),

            yaxis_title="Durchschnitt",
            yaxis_title_font=dict(size=20),
            yaxis=dict(
                tickfont=dict(size=18)
            )
        )
    st.plotly_chart(plot_mean, use_container_width=True)

#%%
#TAB 2: Prognosen
with tab3:
    st.title("Prognosen")

    #Daten laden
    Kunden, Standorte, Verkaufszahlen, Produkte = get_data()
    Verkaufszahlen["Tag"] = pd.to_datetime(Verkaufszahlen["Tag"])
    Verkaufszahlen["Monat"] = Verkaufszahlen["Tag"].dt.to_period("M").astype(str)

    st.subheader("Prognosen-Auswahl")
    #4 Auswahlmöglichkeiten: Buttons nebeneinander
    col1,col2,col3,col4=st.columns(4)
    prognose_option=None #leere Variable

    with col1:
        if st.button("Bluse Nord"):
            prognose_option="Bluse in Region Nord"
    with col2:
        if st.button("Bluse Ost"):
            prognose_option="Bluse in Region Ost"
    with col3:
        if st.button("Marke Puma"):
            prognose_option="Verkaufsmenge Marke Puma"
    with col4:
        if st.button("Marke Adidas"):
            prognose_option="Verkaufsmenge Marke Adidas"

    #Bei Klick - Start der Prognose
    if prognose_option: 
        st.write (f"**Ausgewählte Prognose:** {prognose_option}")

        #1)Region & Produktgruppe
        if "Bluse" in prognose_option: 
            df = (
                Verkaufszahlen
                .merge(Produkte, on="ProduktID", how="left")
                .merge(Standorte, on="OrtID", how="left")
                .groupby(["Region", "Produktgruppe", "Monat"], as_index=False)
                .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
            )
            region = "Nord" if "Nord" in prognose_option else "Ost"
            produktgruppe = "Bluse"
            df_subset = df[(df["Region"] == region) & (df["Produktgruppe"] == produktgruppe)].copy()

        #2) Marke
        elif "Marke" in prognose_option:
            df_marke = (
                Verkaufszahlen
                .merge(Produkte, on="ProduktID", how="left")
                .groupby(["Marke", "Monat"], as_index=False)
                .agg(Verkaufsmenge=("Verkaufsmenge", "sum"))
            )
            marke= "Puma" if "Puma" in prognose_option else "Adidas"
            df_subset = df_marke[df_marke["Marke"] == marke].copy()
            
        #Vorverarbeitung für Regression
        df_subset = df_subset.sort_values("Monat").reset_index(drop=True)
        df_subset["Monat_num"] = range(len(df_subset))

        #Regression & Plot
        if len(df_subset) < 2:
            st.warning("Nicht genug Daten für Prognose")
        else:
            X = sm.add_constant(df_subset["Monat_num"])
            y = df_subset["Verkaufsmenge"]
            model = sm.OLS(y, X).fit()

            #Prognosen
            forecast_rows = []
            for i in range(1, 7): 
                monat_num = len(df_subset) + i - 1
                y_pred = model.predict([1, monat_num])[0]
            #1)Region & Produktgruppe
                if "Bluse" in prognose_option:
                    forecast_rows.append({
                        "Region": region,
                        "Produktgruppe": produktgruppe,
                        "Monat": f"Zukunft +{i}",
                        "Monat_num": monat_num,
                        "Verkaufsmenge": y_pred
                    })
            #2)Marke
                elif "Marke" in prognose_option:
                    forecast_rows.append({
                        "Marke": marke,
                        "Monat": f"Zukunft +{i}",
                        "Monat_num": monat_num,
                        "Verkaufsmenge": y_pred
                    })

            df_forecast = pd.DataFrame(forecast_rows)
            df_forecast["Monat_num"] = df_forecast["Monat_num"].astype(int)  # sicherstellen, dass Spalte existiert
            df_combined = pd.concat([df_subset, df_forecast], ignore_index=True) #Vergangenheit + Prognose

            #Plot mit plotnine
            title = f"Prognose für {prognose_option}"
            plot = (
                ggplot(df_combined, aes(x="Monat_num", y="Verkaufsmenge")) +
                geom_line(color="blue") +
                geom_point(color="blue") +
                geom_line(mapping=aes(x="Monat_num", y="Verkaufsmenge"), data=df_forecast, color="red", linetype="dashed") +
                geom_point(mapping=aes(x="Monat_num", y="Verkaufsmenge"), data=df_forecast, color="red") +
                ggtitle(title)+
                theme(
                    axis_title_x=p9.element_text(size=4),
                    axis_title_y=p9.element_text(size=4),
                    axis_text_x=p9.element_text(size=3),
                    axis_text_y=p9.element_text(size=3),
                    plot_title=p9.element_text(size=7)
                )
            )
            fig = plot.draw(show=False)
            fig.set_size_inches(5, 2)
            st.pyplot(fig)
            
            #Hinweis zur Intepretation
            st.info("🔴 Die rote Linie zeigt eine Prognose für die nächsten 6 Monate.\n\n🔵 Die blauen Werte zeigen die realen Verkaufsmengen aus dem Jahr 2024.")