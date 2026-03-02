import streamlit as st
import pandas as pd

from login import mostra_login
from database import connetti_google, carica_dati
from calendario import mostra_calendario
from prenotazione import gestisci_prenotazione
from tabella import mostra_tabella

st.set_page_config(page_title="Casa al Mare", page_icon="🏖️", layout="wide")

sheet_prenotazioni, sheet_utenti = connetti_google()

if sheet_prenotazioni is None or sheet_utenti is None:
    st.error("⚠️ Impossibile connettersi a Google Sheets.")
    st.stop()

df_prenotazioni = carica_dati(sheet_prenotazioni)
df_utenti = carica_dati(sheet_utenti)

if "autenticato" not in st.session_state:
    st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
    mostra_login(df_utenti, sheet_utenti)
else:
    ruolo = st.session_state["ruolo"]
    nome = st.session_state["nome_utente"]
    
    st.title(f"🏖️ Prenotazioni Casa al Mare")
    st.caption(f"👤 Accesso effettuato come: **{nome}** (Livello: {ruolo})")
    
    if st.sidebar.button("🚪 Esci / Logout"):
        st.session_state["autenticato"] = False
        st.rerun()

    if not df_prenotazioni.empty:
        df_prenotazioni['Data Inizio'] = pd.to_datetime(df_prenotazioni['Data Inizio'], format="mixed", dayfirst=True).dt.date
        df_prenotazioni['Data Fine'] = pd.to_datetime(df_prenotazioni['Data Fine'], format="mixed", dayfirst=True).dt.date

    mostra_calendario(df_prenotazioni)
    gestisci_prenotazione(df_prenotazioni, sheet_prenotazioni)
    
    # MODIFICA: Ora passiamo anche df_utenti alla tabella per fargli trovare l'email!
    mostra_tabella(df_prenotazioni, sheet_prenotazioni, df_utenti)
