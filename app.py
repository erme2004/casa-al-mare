import streamlit as st

# Importiamo le funzioni dai nostri nuovi file
from database import connetti_google, carica_dati
from calendario import mostra_calendario
from prenotazione import gestisci_prenotazione
from tabella import mostra_tabella

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Casa al Mare", page_icon="🏖️", layout="wide")
st.title("🏖️ Prenotazioni Casa al Mare")

# 1. Ci connettiamo e scarichiamo i dati
sheet = connetti_google()
if sheet is None:
    st.error("⚠️ Impossibile connettersi a Google Sheets. Controlla i permessi o la connessione.")
    st.stop()

df = carica_dati(sheet)

# 2. Mostriamo il Calendario
mostra_calendario(df)

# 3. Mostriamo l'area per prenotare
gestisci_prenotazione(df, sheet)

# 4. Mostriamo la tabella in basso
mostra_tabella(df)