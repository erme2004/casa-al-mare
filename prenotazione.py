import streamlit as st
from datetime import date, timedelta

def gestisci_prenotazione(df, sheet):
    st.header("Aggiungi una prenotazione")
    
    # Dividiamo in due colonne come hai impostato tu
    col1, col2 = st.columns(2)

    with col1:
        lista_nomi = ["Scegli un nome...", "Zia Terry", "Zio Vincy", "Mamma & Papà", "Aby", "Marco", "Luca", "Emy"]
        nome = st.selectbox("Chi prenota?", options=lista_nomi)
        
        oggi = date.today()
        domani = oggi + timedelta(days=1)
        
        # Calcoliamo la data limite per i "comuni mortali" (31 giorni da oggi)
        data_limite_inizio = oggi + timedelta(days=31)
        
        date_selezionate = st.date_input(
            "Seleziona Arrivo e Partenza", 
            value=(oggi, domani), 
            min_value=oggi, 
            format="DD/MM/YYYY"
        )

    with col2:
        note = st.text_area("Note (es. orario arrivo, ospiti extra...)", max_chars=300)

    submit = st.button("Prenota")

    if submit:
        # Controllo di sicurezza se manca la connessione
        if not sheet:
            st.error("⚠️ Impossibile salvare: connessione a Google Sheets assente.")
            return

        if len(date_selezionate) != 2:
            st.error("⚠️ Seleziona sia la data di arrivo che quella di partenza!")
        else:
            data_inizio = date_selezionate[0]
            data_fine = date_selezionate[1]
            
            # --- LOGICA DI CONTROLLO DATE ---
            errore_regola = False
            
            if nome == "Scegli un nome...":
                st.error("⚠️ Seleziona un nome!")
                errore_regola = True
            
            elif data_inizio >= data_fine:
                st.error("⚠️ La partenza deve essere dopo l'arrivo.")
                errore_regola = True
                
            # NUOVA REGOLA: Se non è Zia Terry, l'inizio non può essere oltre i 31 giorni da oggi
            elif nome != "Zia Terry" and data_inizio > data_limite_inizio:
                st.error(f"⚠️ Prenotazione negata: Solo Zia Terry può prenotare con più di 31 giorni di anticipo. Per te, la data di inizio massima consentita è il {data_limite_inizio.strftime('%d/%m/%Y')}.")
                errore_regola = True

            # Se i controlli base e la regola dei 31 giorni sono passati, controlliamo le sovrapposizioni
            if not errore_regola:
                sovrapposizione = False
                chi_ha_prenotato = ""
                
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
                    costo = 0 if nome == "Zia Terry" else (durata + 1) * 10
                    
                    inizio_str = data_inizio.strftime("%Y-%m-%d")
                    fine_str = data_fine.strftime("%Y-%m-%d")
                    
                    try:
                        # Salviamo tutti e 6 i dati (incluse le Note) sul foglio Google!
                        sheet.append_row([nome, inizio_str, fine_str, costo, durata + 1, note])
                        st.success(f"✅ Prenotazione per {nome} aggiunta con successo!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore caricamento: {e}")
