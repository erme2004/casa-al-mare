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
        
        # ⚠️ RIMETTI QUI IL TUO LINK LUNGO!
        file_google = client.open_by_url("https://docs.google.com/spreadsheets/d/1EmvOi4YGiwAJuBh2z9jMvEAsljsFY46-PWbkrFfQyWY/edit?gid=1075214251#gid=1075214251")
        
        # Ora prendiamo entrambi i fogli!
        sheet_prenotazioni = file_google.worksheet("Foglio1") # Cambia "Foglio1" se il tuo foglio principale ha un altro nome
        sheet_utenti = file_google.worksheet("Utenti")
        
        return sheet_prenotazioni, sheet_utenti
    except Exception as e:
        return None, None

def carica_dati(sheet):
    if not sheet:
        return pd.DataFrame()
    dati = sheet.get_all_records()
    if not dati:
        return pd.DataFrame()
    df = pd.DataFrame(dati)
    df.columns = df.columns.str.strip()
    return df

