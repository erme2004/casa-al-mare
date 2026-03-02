import streamlit as st
from datetime import date, timedelta

def gestisci_prenotazione(df, sheet):
    st.header("Aggiungi una prenotazione")
    col1, col2 = st.columns(2)

    # L'app sa già chi sei e che ruolo hai!
    nome_utente = st.session_state["nome_utente"]
    ruolo_utente = st.session_state["ruolo"]

    with col1:
        st.info(f"👤 Stai prenotando a nome di: **{nome_utente}**")
        
        oggi = date.today()
        domani = oggi + timedelta(days=1)
        data_limite_inizio = oggi + timedelta(days=31)
        
        date_selezionate = st.date_input("Seleziona Arrivo e Partenza", value=(oggi, domani), min_value=oggi, format="DD/MM/YYYY")

    with col2:
        note = st.text_area("Note (es. orario arrivo...)", max_chars=300)

    submit = st.button("Prenota")

    if submit:
        if len(date_selezionate) != 2:
            st.error("⚠️ Seleziona sia la data di arrivo che quella di partenza!")
        else:
            data_inizio, data_fine = date_selezionate
            
            if data_inizio >= data_fine:
                st.error("⚠️ La partenza deve essere dopo l'arrivo.")
            else:
                # --- LOGICA DELLO STATO ---
                stato_prenotazione = "Confermata"
                
                # Se NON è Admin e supera i 31 giorni -> Diventa "In attesa"
                if ruolo_utente != "Admin" and data_inizio > data_limite_inizio:
                    stato_prenotazione = "In attesa"
                    st.warning("⏳ Data oltre i 31 giorni. La prenotazione sarà 'In attesa' di conferma da un Admin.")

                sovrapposizione = False
                chi_ha_prenotato, stato_esistente = "", ""
                
                if not df.empty:
                    for _, row in df.iterrows():
                        if max(data_inizio, row['Data Inizio']) < min(data_fine, row['Data Fine']):
                            sovrapposizione = True
                            chi_ha_prenotato = row.get('Nome', 'Sconosciuto')
                            stato_esistente = row.get('Stato', 'Confermata')
                            break
                
                if sovrapposizione:
                    st.error(f"❌ Errore: Le date si sovrappongono con {chi_ha_prenotato} (Stato: {stato_esistente})!")
                else:
                    durata = (data_fine - data_inizio).days
                    costo = 0 if ruolo_utente == "Admin" else (durata + 1) * 10
                    
                    try:
                        # Salviamo la 7° colonna "Stato"
                        sheet.append_row([nome_utente, str(data_inizio), str(data_fine), costo, durata + 1, note, stato_prenotazione])
                        if stato_prenotazione == "Confermata":
                            st.success("✅ Prenotazione Confermata e salvata!")
                        else:
                            st.success("✅ Richiesta inviata! Ora è 'In attesa' di approvazione.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore: {e}")
