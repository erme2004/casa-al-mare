import streamlit as st
from datetime import date, timedelta

def gestisci_prenotazione(df, sheet):
    st.header("Aggiungi una prenotazione")
    lista_nomi = ["Scegli un nome...", "Zia Terry", "Zio Vincy", "Mamma & Papà", "Aby", "Marco", "Luca", "Emy"]
    nome = st.selectbox("Chi prenota?", options=lista_nomi)

    oggi = date.today()
    domani = oggi + timedelta(days=1)

    date_selezionate = st.date_input(
        "Seleziona Arrivo e Partenza", 
        value=(oggi, domani), 
        min_value=oggi, 
        format="DD/MM/YYYY"
    )

    submit = st.button("Prenota")

    if submit:
        if not sheet:
            st.error("⚠️ Impossibile salvare: connessione a Google Sheets assente.")
            return

        if len(date_selezionate) != 2:
            st.error("⚠️ Clicca due volte sul calendario per selezionare sia l'arrivo che la partenza!")
        else:
            data_inizio = date_selezionate[0]
            data_fine = date_selezionate[1]
            
            if nome == "Scegli un nome...":
                st.error("⚠️ Devi selezionare un nome dalla lista!")
            elif data_inizio >= data_fine:
                st.error("⚠️ La data di partenza deve essere successiva a quella di arrivo.")
            else:
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
                        sheet.append_row([nome, inizio_str, fine_str, costo, durata + 1])
                        st.success(f"✅ Prenotazione per {nome} aggiunta!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore: {e}")
