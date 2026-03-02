import streamlit as st
import pandas as pd
from datetime import date, timedelta
import gspread
from google.oauth2.service_account import Credentials
from streamlit_calendar import calendar 

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Casa al Mare", page_icon="🏖️", layout="wide")
st.title("🏖️ Prenotazioni Casa al Mare")

# --- CONNESSIONE GOOGLE SHEETS ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def get_gsheet_client():
    try:
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
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
        return pd.DataFrame(columns=["Nome", "Data Inizio", "Data Fine", "Costo", "Durata Pernottamento", "Note"])
    
    df = pd.DataFrame(dati)
    df.columns = df.columns.str.strip()
    
    # Se la colonna Note non esiste ancora nel foglio, la creiamo nel DataFrame
    if "Note" not in df.columns:
        df["Note"] = ""
        
    df['Data Inizio'] = pd.to_datetime(df['Data Inizio']).dt.date
    df['Data Fine'] = pd.to_datetime(df['Data Fine']).dt.date
    return df

df = load_data()

# --- CALENDARIO VISIVO ---
st.subheader("📅 Disponibilità Casa")
col_vuota_sx, col_calendario, col_vuota_dx = st.columns([1.5, 2, 1.5])

with col_calendario:
    calendar_events = []
    for _, row in df.iterrows():
        inizio = row['Data Inizio']
        fine = row['Data Fine']
        
        # 1. Background Rosso
        durata_giorni = (fine - inizio).days
        for i in range(durata_giorni + 1):
            giorno_singolo = inizio + timedelta(days=i)
            calendar_events.append({
                "start": str(giorno_singolo),
                "end": str(giorno_singolo + timedelta(days=1)),
                "display": "background",
                "backgroundColor": "#d1435b"
            })
        
        # 2. Testo con Nome (e nota breve se presente)
        testo_evento = f"{row['Nome']}"
        calendar_events.append({
            "title": testo_evento,
            "start": str(inizio),
            "end": str(fine + timedelta(days=1)),
            "backgroundColor": "transparent",
            "borderColor": "black",
            "textColor": "black"
        })

    calendar_options = {
        "headerToolbar": {"left": "prev", "center": "title", "right": "next"},
        "initialView": "dayGridMonth",
        "locale": "it",
        "height": "auto",
        "showNonCurrentDates": True,
        "fixedWeekCount": False,
    }

    css_calendario = """
    .fc-toolbar-title { text-transform: capitalize !important; }
    .fc-daygrid-day { border: 1px solid white !important; }
    .fc-daygrid-day-frame { background-color: rgb(1, 167, 153) !important; }
    .fc-bg-event { opacity: 1 !important; }
    .fc-h-event { background-color: transparent !important; border: 2px solid black !important; border-radius: 4px !important; }
    .fc .fc-button-primary { background-color: white !important; border-color: white !important; color: black !important; }
    .fc-event-main { display: flex !important; justify-content: center !important; align-items: center !important; font-weight: bold !important; font-size: 15px !important; color: white !important; text-shadow: 1px 1px 4px black !important; }
    """
    calendar(events=calendar_events, options=calendar_options, custom_css=css_calendario)

# --- SEZIONE DI PRENOTAZIONE ---
st.header("Aggiungi una prenotazione")
col1, col2 = st.columns(2)

with col1:
    lista_nomi = ["Scegli un nome...", "Zia Terry", "Zio Vincy", "Mamma & Papà", "Aby", "Marco", "Luca", "Emy"]
    nome = st.selectbox("Chi prenota?", options=lista_nomi)
    
    oggi = date.today()
    domani = oggi + timedelta(days=1)
    date_selezionate = st.date_input("Seleziona Arrivo e Partenza", value=(oggi, domani), min_value=oggi, format="DD/MM/YYYY")

with col2:
    # AGGIUNTA: Campo Note con limite 300 caratteri
    note = st.text_area("Note (es. orario arrivo, ospiti extra...)", max_chars=300)

submit = st.button("Prenota")

if submit:
    if len(date_selezionate) != 2:
        st.error("⚠️ Seleziona sia la data di arrivo che quella di partenza!")
    else:
        data_inizio, data_fine = date_selezionate
        if nome == "Scegli un nome...":
            st.error("⚠️ Seleziona un nome!")
        elif data_inizio >= data_fine:
            st.error("⚠️ La partenza deve essere dopo l'arrivo.")
        else:
            sovrapposizione = False
            for _, row in df.iterrows():
                if max(data_inizio, row['Data Inizio']) < min(data_fine, row['Data Fine']):
                    sovrapposizione = True
                    chi_ha_prenotato = row['Nome']
                    break
            
            if sovrapposizione:
                st.error(f"❌ Errore: Sovrapposizione con {chi_ha_prenotato}!")
            else:
                durata = (data_fine - data_inizio).days
                costo = 0 if nome == "Zia Terry" else (durata + 1) * 10
                
                try:
                    # AGGIORNATO: Aggiungiamo la nota alla riga di Google Sheets
                    sheet.append_row([nome, str(data_inizio), str(data_fine), costo, durata + 1, note])
                    st.success("✅ Prenotazione aggiunta!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore caricamento: {e}")

# --- ZIONE TABELLA ---
st.header("Lista Prenotazioni")
if not df.empty:
    df_mostra = df.sort_values(by="Data Inizio").copy()
    
    # Formattazione per rendere la tabella bella da vedere
    mesi = ["", "Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]
    
    def formatta_data(d):
        d_obj = pd.to_datetime(d)
        return f"{d_obj.day} {mesi[d_obj.month]} {d_obj.year}"

    df_mostra["Data Inizio"] = df_mostra["Data Inizio"].apply(formatta_data)
    df_mostra["Data Fine"] = df_mostra["Data Fine"].apply(formatta_data)
    df_mostra["Costo"] = df_mostra["Costo"].apply(lambda x: f"{x} €")
    df_mostra["Durata Pernottamento"] = df_mostra["Durata Pernottamento"].apply(lambda x: f"{x} gg")
    
    # Gestione delle Note vuote per evitare che appaia "NaN"
    df_mostra["Note"] = df_mostra["Note"].fillna("").astype(str)
    
    # Mostra la tabella completa
    st.dataframe(df_mostra, use_container_width=True, hide_index=True)
else:
    st.info("Nessuna prenotazione al momento.")
