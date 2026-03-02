import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage

# --- FUNZIONE EMAIL APPROVAZIONE ADMIN ---
def invia_conferma_admin(email_utente, nome, inizio, fine):
    try:
        mittente = st.secrets["email"]["mittente"]
        password = st.secrets["email"]["password"]
        
        msg = EmailMessage()
        msg['Subject'] = "🎉 Prenotazione Casa al Mare CONFERMATA!"
        msg['From'] = mittente
        msg['To'] = email_utente
        
        testo = f"Ottime notizie {nome}!\n\nLa tua prenotazione in attesa per la Casa al Mare è stata appena APPROVATA dall'Admin.\n\n"
        testo += f"📅 Dal: {inizio}\n📅 Al: {fine}\n\nIl calendario è aggiornato. Prepara le valigie! 🏖️"
        msg.set_content(testo)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(mittente, password)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Errore email approvazione: {e}")

# --- TABELLA E PANNELLO ADMIN ---
def mostra_tabella(df, sheet_prenotazioni, df_utenti):
    st.header("📋 Lista Prenotazioni")
    
    ruolo = st.session_state.get("ruolo", "User")
    
    if not df.empty:
        if 'Stato' not in df.columns:
            df['Stato'] = "Confermata"
            
        # --- SEZIONE ADMIN: PANNELLO DI APPROVAZIONE ---
        if ruolo == "Admin":
            df_attesa = df[df['Stato'] == "In attesa"]
            if not df_attesa.empty:
                st.warning(f"🔔 Hai {len(df_attesa)} prenotazioni in attesa di approvazione!")
                
                with st.expander("🛠️ Pannello di Approvazione Admin", expanded=True):
                    opzioni = []
                    for i, row in df_attesa.iterrows():
                        riga_excel = i + 2 
                        testo = f"{row['Nome']} | Dal {row['Data Inizio']} al {row['Data Fine']}"
                        # Salviamo tutti i dati utili nella scelta per usarli dopo
                        opzioni.append((riga_excel, testo, row['Nome'], row['Data Inizio'], row['Data Fine']))
                    
                    scelta = st.selectbox("Scegli la richiesta da gestire:", opzioni, format_func=lambda x: x[1])
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✅ Approva"):
                            # 1. Aggiorna lo stato sul foglio Google
                            sheet_prenotazioni.update_cell(scelta[0], 7, "Confermata")
                            
                            # 2. Cerca l'email dell'utente nel database
                            nome_da_cercare = scelta[2]
                            email_trovata = ""
                            if not df_utenti.empty and nome_da_cercare in df_utenti['Nome'].values:
                                email_trovata = df_utenti[df_utenti['Nome'] == nome_da_cercare].iloc[0]['Email']
                            
                            # 3. Manda l'email di buona notizia!
                            if email_trovata:
                                invia_conferma_admin(email_trovata, nome_da_cercare, scelta[3], scelta[4])
                                
                            st.success("Approvata e notifica email inviata all'utente!")
                            st.rerun()
                                
                    with col_btn2:
                        if st.button("❌ Rifiuta (Elimina)"):
                            sheet_prenotazioni.delete_rows(scelta[0])
                            st.success("Prenotazione eliminata!")
                            st.rerun()

        # --- VISUALIZZAZIONE NORMALE TABELLA ---
        df_mostra = df.sort_values(by="Data Inizio").copy()
        mesi = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
        
        def formatta_data(d):
            try:
                d_obj = pd.to_datetime(d)
                return f"{d_obj.day} {mesi[d_obj.month]} {d_obj.year}"
            except: 
                return d

        df_mostra["Data Inizio"] = df_mostra["Data Inizio"].apply(formatta_data)
        df_mostra["Data Fine"] = df_mostra["Data Fine"].apply(formatta_data)
        
        st.dataframe(df_mostra, use_container_width=True, hide_index=True)
    else:
        st.info("Nessuna prenotazione al momento.")
