import streamlit as st
import pandas as pd

from login import mostra_login
from database import connetti_google, carica_dati
from calendario import mostra_calendario
from prenotazione import gestisci_prenotazione
from tabella import mostra_tabella

st.set_page_config(page_title="Casa al Mare", page_icon="🏖️", layout="wide")

# 1. Connessione a Google (lo facciamo subito così possiamo leggere gli utenti)
sheet_prenotazioni, sheet_utenti = connetti_google()

if sheet_prenotazioni is None or sheet_utenti is None:
    st.error("⚠️ Impossibile connettersi a Google Sheets.")
    st.stop()

# Carichiamo i due database
df_prenotazioni = carica_dati(sheet_prenotazioni)
df_utenti = carica_dati(sheet_utenti)

# --- SISTEMA DI LOGIN ---
if "autenticato" not in st.session_state:
    st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
    # 🎯 ECCO LA RIGA CHE DAVA ERRORE: Ora passiamo il database utenti al login!
    mostra_login(df_utenti)
else:
    # Mostriamo a chi appartiene la sessione!
    ruolo = st.session_state["ruolo"]
    nome = st.session_state["nome_utente"]
    
    st.title(f"🏖️ Prenotazioni Casa al Mare")
    st.caption(f"👤 Accesso effettuato come: **{nome}** (Livello: {ruolo})")
    
    if st.sidebar.button("🚪 Esci / Logout"):
        st.session_state["autenticato"] = False
        st.rerun()

    # Formattiamo le date del database prenotazioni
    if not df_prenotazioni.empty:
        df_prenotazioni['Data Inizio'] = pd.to_datetime(df_prenotazioni['Data Inizio'], format="mixed", dayfirst=True).dt.date
        df_prenotazioni['Data Fine'] = pd.to_datetime(df_prenotazioni['Data Fine'], format="mixed", dayfirst=True).dt.date

    # 2. Mostriamo il Calendario
    mostra_calendario(df_prenotazioni)

    # 3. Mostriamo l'area per prenotare
    gestisci_prenotazione(df_prenotazioni, sheet_prenotazioni)

    # 4. Mostriamo la tabella in basso
    mostra_tabella(df_prenotazioni)
