import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def connetti_google():
    try:
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        else:
            creds = Credentials.from_service_account_file("chiavi.json", scopes=scopes)
        
        client = gspread.authorize(creds)
        # ⚠️ INCOLLA QUI SOTTO IL LINK LUNGO DEL TUO FOGLIO GOOGLE!
        sheet = client.open_by_url("INCOLLA_QUI_IL_TUO_LINK_LUNGO").sheet1
        return sheet
    except Exception as e:
        return None

def carica_dati(sheet):
    if not sheet:
        return pd.DataFrame()
    dati = sheet.get_all_records()
    if not dati:
        return pd.DataFrame(columns=["Nome", "Data Inizio", "Data Fine", "Costo", "Durata Pernottamento"])
    df = pd.DataFrame(dati)
    df.columns = df.columns.str.strip()
    df['Data Inizio'] = pd.to_datetime(df['Data Inizio']).dt.date
    df['Data Fine'] = pd.to_datetime(df['Data Fine']).dt.date
    return df