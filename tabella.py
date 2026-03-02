import streamlit as st
import pandas as pd

def mostra_tabella(df):
    st.header("Lista Prenotazioni")
    if not df.empty:
        df_mostra = df.sort_values(by="Data Inizio").copy()
        mesi = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
        
        def formatta_data(d):
            try:
                d_obj = pd.to_datetime(d)
                return f"{d_obj.day} {mesi[d_obj.month]} {d_obj.year}"
            except: 
                return d

        df_mostra["Data Inizio"] = df_mostra["Data Inizio"].apply(formatta_data)
        df_mostra["Data Fine"] = df_mostra["Data Fine"].apply(formatta_data)
        
        if "Costo" in df_mostra.columns:
            df_mostra["Costo"] = df_mostra["Costo"].apply(lambda x: f"{x} €")
        if "Durata Pernottamento" in df_mostra.columns:
            df_mostra["Durata Pernottamento"] = df_mostra["Durata Pernottamento"].apply(lambda x: f"{x} Giorni")
        
        st.dataframe(df_mostra, use_container_width=True, hide_index=True)
    else:
        st.info("Nessuna prenotazione al momento.")