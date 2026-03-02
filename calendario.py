import streamlit as st
from datetime import timedelta
from streamlit_calendar import calendar

def mostra_calendario(df):
    st.subheader("📅 Disponibilità Casa")
    col_vuota_sx, col_calendario, col_vuota_dx = st.columns([1.5, 2, 1.5])
    
    with col_calendario:
        calendar_events = []
        if not df.empty:
            for _, row in df.iterrows():
                inizio = row['Data Inizio']
                fine = row['Data Fine']
                durata = (fine - inizio).days
                
                # Sfondo diviso per mantenere i bordi
                for i in range(durata + 1):
                    giorno = inizio + timedelta(days=i)
                    calendar_events.append({
                        "start": str(giorno),
                        "end": str(giorno + timedelta(days=1)),
                        "display": "background",
                        "backgroundColor": "#d1435b"
                    })
                
                # Testo centrato
                calendar_events.append({
                    "title": str(row['Nome']), 
                    "start": str(inizio),
                    "end": str(fine + timedelta(days=1)),
                    "backgroundColor": "transparent",
                    "borderColor": "black",
                    "textColor": "black"
                })

        calendar_options = {
            "headerToolbar": {"left": "prev", "center": "title", "right": "next"},
            "initialView": "dayGridMonth",
            "selectable": False,
            "locale": "it",
            "height": "auto",
            "aspectRatio": 1.5,
            "contentHeight": 300,
            "showNonCurrentDates": True,
            "fixedWeekCount": False,
        }

        css_calendario = """
        .fc-toolbar-title { text-transform: capitalize !important; }
        .fc-daygrid-day { border: 1px solid white !important; }
        .fc-daygrid-day-frame { background-color: rgb(1, 167, 153) !important; }
        .fc-bg-event { opacity: 1 !important; }
        .fc-h-event {
            background-color: transparent !important;
            border: 2px solid black !important;
            border-radius: 4px !important;
        }
        .fc .fc-button-primary {
            background-color: white !important;
            border-color: white !important;
            color: black !important;
        }
        .fc-event-main {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            font-weight: bold !important;
            font-size: 15px !important;
            color: white !important;
            text-shadow: 1px 1px 4px black !important;
        }
        """
        calendar(events=calendar_events, options=calendar_options, custom_css=css_calendario)