import streamlit as st
import pandas as pd
from datetime import date, timedelta
import gspread
from google.oauth2.service_account import Credentials
from streamlit_calendar import calendar  # <--- Nuova libreria

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Casa al Mare", page_icon="🏖️", layout="wide")
st.title("🏖️ Prenotazioni Casa al Mare")
st.markdown("""
    <style>
    /* 1. Sfondo VERDE di default per tutti i giorni del mese */
    ...
    </style>
    """, unsafe_allow_html=True)
# --- CONNESSIONE GOOGLE SHEETS ---
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gsheet_client():
    try:
        # Se siamo online, usa la cassaforte segreta di Streamlit
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        # Se siamo sul tuo PC, usa il file locale
        else:
            creds = Credentials.from_service_account_file("chiavi.json", scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        return None

client = get_gsheet_client()
if client:
    sheet = client.open("Prenotazioni Casa Mare").sheet1
else:
    st.error("⚠️ Errore di connessione a Google Sheets.")
    st.stop()

# --- FUNZIONI PER I DATI ---
def load_data():
    dati = sheet.get_all_records()
    if not dati:
        return pd.DataFrame(columns=["Nome", "Data Inizio", "Data Fine", "Costo", "Durata Pernottamento"])
    df = pd.DataFrame(dati)
    df.columns = df.columns.str.strip()
    df['Data Inizio'] = pd.to_datetime(df['Data Inizio']).dt.date
    df['Data Fine'] = pd.to_datetime(df['Data Fine']).dt.date
    return df

df = load_data()

# --- CALENDARIO VISIVO (Nuova Sezione) ---
# --- CALENDARIO VISIVO (RIMPICCIOLITO) ---
# --- CALENDARIO VISIVO (COMPATTO MESE PER MESE) ---
# --- CALENDARIO VISIVO (COMPATTO CON RIGHE COMPLETATE) ---
# --- CALENDARIO VISIVO (CELLA INTERAMENTE ROSSA) ---
st.subheader("📅 Disponibilità Casa")

col_vuota_sx, col_calendario, col_vuota_dx = st.columns([1.5, 2, 1.5])

with col_calendario:
    calendar_events = []
    for _, row in df.iterrows():
        inizio = row['Data Inizio']
        fine = row['Data Fine']
        
        # -- 1. EVENTO SFONDO (Diviso giorno per giorno per mantenere i bordi!) --
        durata = (fine - inizio).days
        for i in range(durata + 1):
            giorno_singolo = inizio + timedelta(days=i)
            calendar_events.append({
                "start": str(giorno_singolo),
                "end": str(giorno_singolo + timedelta(days=1)),
                "display": "background",
                "backgroundColor": "#d1435b"  # Rosso acceso
            })
        
        # -- 2. EVENTO TESTO (Unito, così il nome si centra su tutti i giorni) --
        calendar_events.append({
            "title": str(row['Nome']), 
            "start": str(inizio),
            "end": str(fine + timedelta(days=1)),
            "backgroundColor": "transparent", # Usa il trasparente al posto dell'azzurro
            "borderColor": "black",           # Imposta il colore del bordo
            "textColor": "black"
        })

    calendar_options = {
        "headerToolbar": {
            "left": "prev",
            "center": "title",
            "right": "next"
        },
        "initialView": "dayGridMonth",
        "selectable": False,
        "locale": "it",
        "height": "auto",
        "aspectRatio": 1.5,
        "contentHeight": 300,
        "showNonCurrentDates": True,  # <--- RIMESSO A TRUE PER MOSTRARE I NUMERI!
        "fixedWeekCount": False,
    }

    # --- IL TRUCCO MAGICO: Il CSS direttamente nel calendario! ---
    css_calendario = """
    /* --- NOVITÀ: Titolo del mese con la prima lettera Maiuscola --- */
    .fc-toolbar-title {
        text-transform: capitalize !important; 
    }

    /* Bordi netti bianchi tra una casella e l'altra */
    .fc-daygrid-day {
        border: 1px solid white !important; 
    }

    /* Colora di VERDE la base di tutte le caselle */
    .fc-daygrid-day-frame {
        background-color: rgb(1, 167, 153) !important; 
    }

    /* Rende il ROSSO bello acceso */
    .fc-bg-event {
        opacity: 1 !important;
    }
    
    /* --- NOVITÀ: Il bordo nero attorno al nome (addio azzurro!) --- */
    .fc-h-event {
        background-color: transparent !important; /* Rende invisibile lo sfondo azzurro */
        border: 2px solid black !important;       /* Disegna il bordo nero spesso 2 pixel */
        border-radius: 4px !important;            /* Arrotonda leggermente gli angoli del bordo */
    }
    
    /* --- NOVITÀ: Colore dei pulsanti in alto (Frecce mese) --- */
    .fc .fc-button-primary {
        background-color: white !important; /* Sfondo del bottone (nero) */
        border-color: white !important;     /* Bordo del bottone (nero) */
        color: black !important;            /* Colore della freccina dentro (bianca) */
    }

    /* Centra perfettamente i nomi e li rende super leggibili */
    .fc-event-main {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-weight: bold !important;
        font-size: 15px !important;
        color: white !important;
        text-shadow: 1px 1px 4px black !important; /* Ombra nera sotto la scritta per farla risaltare */
    }
    """

    # Avviamo il calendario passandogli le opzioni E ANCHE il nostro CSS!
    calendar(events=calendar_events, options=calendar_options, custom_css=css_calendario)

# --- SEZIONE DI PRENOTAZIONE (Stile Skyscanner!) ---
st.header("Aggiungi una prenotazione")
lista_nomi = ["Scegli un nome...", "Zia Terry", "Zio Vincy", "Mamma & Papà", "Aby", "Marco", "Luca", "Emy"]

nome = st.selectbox("Chi prenota?", options=lista_nomi)

# Prepariamo le date di base
oggi = date.today()
domani = oggi + timedelta(days=1)

# IL TRUCCO: Passando (oggi, domani), il calendario diventa un selettore di periodo!
date_selezionate = st.date_input(
    "Seleziona Arrivo e Partenza", 
    value=(oggi, domani), 
    min_value=oggi, 
    format="DD/MM/YYYY"
)

submit = st.button("Prenota")

if submit:
    # Siccome l'utente deve cliccare due volte, controlliamo che abbia effettivamente scelto due date
    if len(date_selezionate) != 2:
        st.error("⚠️ Clicca due volte sul calendario per selezionare sia l'arrivo che la partenza!")
    else:
        # Estraiamo le due date selezionate
        data_inizio = date_selezionate[0]
        data_fine = date_selezionate[1]
        
        if nome == "Scegli un nome...":
            st.error("⚠️ Devi selezionare un nome dalla lista!")
        elif data_inizio >= data_fine:
            st.error("⚠️ La data di partenza deve essere successiva a quella di arrivo.")
        else:
            sovrapposizione = False
            if not df.empty:
                for _, row in df.iterrows():
                    if max(data_inizio, row['Data Inizio']) < min(data_fine, row['Data Fine']):
                        sovrapposizione = True
                        chi_ha_prenotato = row['Nome']
                        break
            
            if sovrapposizione:
                st.error(f"❌ Errore: Sovrapposizione con {chi_ha_prenotato}!")
            else:
                durata = (data_fine - data_inizio).days
                if nome == "Zia Terry":
                    costo = 0
                else:
                    costo = (durata + 1) * 10
                
                inizio_str = data_inizio.strftime("%Y-%m-%d")
                fine_str = data_fine.strftime("%Y-%m-%d")

                try:
                    sheet.append_row([nome, inizio_str, fine_str, costo, durata + 1])
                    st.success(f"✅ Prenotazione per {nome} aggiunta!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")

# --- VISUALIZZAZIONE TABELLA ---
st.header("Lista Prenotazioni")
if not df.empty:
    df_mostra = df.sort_values(by="Data Inizio").copy()
    mesi = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
            "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
    
    def formatta_data(d):
        try:
            d_obj = pd.to_datetime(d)
            return f"{d_obj.day} {mesi[d_obj.month]} {d_obj.year}"
        except: return d

    df_mostra["Data Inizio"] = df_mostra["Data Inizio"].apply(formatta_data)
    df_mostra["Data Fine"] = df_mostra["Data Fine"].apply(formatta_data)
    
    if "Costo" in df_mostra.columns:
        df_mostra["Costo"] = df_mostra["Costo"].apply(lambda x: f"{x} €")
    if "Durata Pernottamento" in df_mostra.columns:
        df_mostra["Durata Pernottamento"] = df_mostra["Durata Pernottamento"].apply(lambda x: f"{x} Giorni")
    
    st.dataframe(df_mostra, use_container_width=True, hide_index=True)
else:
    st.info("Nessuna prenotazione al momento.")