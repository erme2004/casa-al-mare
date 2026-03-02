import streamlit as st

# Importiamo le funzioni dai nostri file, incluso il nuovo login!
from login import mostra_login
from database import connetti_google, carica_dati
from calendario import mostra_calendario
from prenotazione import gestisci_prenotazione
from tabella import mostra_tabella

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Casa al Mare", page_icon="🏖️", layout="wide")

# --- SISTEMA DI LOGIN (Il Buttafuori) ---
# Se è la prima volta che l'utente apre il sito, impostiamo che non è autenticato
if "autenticato" not in st.session_state:
    st.session_state["autenticato"] = False

# Se NON è autenticato, mostriamo SOLO la pagina di login
if not st.session_state["autenticato"]:
    mostra_login()

# Se È autenticato, mostriamo tutto il resto del sito!
else:
    st.title("🏖️ Prenotazioni Casa al Mare")
    
    # (Opzionale) Un bottoncino nella barra laterale per fare il Log-Out
    if st.sidebar.button("🚪 Esci / Logout"):
        st.session_state["autenticato"] = False
        st.rerun()

    # 1. Ci connettiamo e scarichiamo i dati
    sheet = connetti_google()
    if sheet is None:
        st.error("⚠️ Impossibile connettersi a Google Sheets.")
        st.stop()
    df = carica_dati(sheet)

    # 2. Mostriamo il Calendario
    mostra_calendario(df)

    # 3. Mostriamo l'area per prenotare
    gestisci_prenotazione(df, sheet)

    # 4. Mostriamo la tabella in basso
    mostra_tabella(df)
