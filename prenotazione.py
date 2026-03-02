import streamlit as st
from datetime import date, timedelta
import smtplib
from email.message import EmailMessage

# --- FUNZIONE PER INVIARE LE NOTIFICHE (FILTRO TOTALE ADMIN) ---
def invia_notifiche(nome, email_utente, inizio, fine, stato):
    try:
        mittente = st.secrets["email"]["mittente"]
        password = st.secrets["email"]["password"]
        email_admin = st.secrets["email"]["admin"]
        
        # Connessione al server di Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(mittente, password)

            # 1. EMAIL PER L'UTENTE (La riceve sempre come ricevuta)
            msg_user = EmailMessage()
            msg_user['Subject'] = "🏖️ Riepilogo prenotazione Casa al Mare"
            msg_user['From'] = mittente
            msg_user['To'] = email_utente
            
            testo_user = f"Ciao {nome}!\n\nAbbiamo registrato la tua richiesta.\n"
            testo_user += f"📅 Dal: {inizio}\n📅 Al: {fine}\n"
            
            if stato == "Confermata":
                testo_user += "✅ STATO: Confermata! Prepara le valigie.\n"
            else:
                testo_user += "⏳ STATO: In attesa. La tua richiesta supera i 31 giorni, ti avviseremo appena l'Admin la approverà!\n"
            
            msg_user.set_content(testo_user)
            smtp.send_message(msg_user)

            # 2. EMAIL PER L'ADMIN (Solo se stato è 'In attesa')
            # Aggiungiamo un controllo extra: l'admin riceve la mail SOLO se 
            # lo stato NON è 'Confermata'
            if stato != "Confermata":
                # Verifichiamo anche che chi prenota non sia l'admin stesso
                if email_utente.lower() != email_admin.lower():
                    msg_admin = EmailMessage()
                    msg_admin['Subject'] = f"⚠️ AZIONE RICHIESTA: Prenotazione da confermare ({nome})"
                    msg_admin['From'] = mittente
                    msg_admin['To'] = email_admin
                    
                    testo_admin = f"Ciao Admin!\n\nC'è una nuova prenotazione che richiede la tua approvazione manuale.\n\n"
                    testo_admin += f"👤 Utente: {nome}\n"
                    testo_admin += f"📅 Periodo: dal {inizio} al {fine}\n"
                    testo_admin += f"📌 Stato attuale: In attesa\n\n"
                    testo_admin += "👉 Vai nel Pannello di Controllo dell'app per gestirla."
                    
                    msg_admin.set_content(testo_admin)
                    smtp.send_message(msg_admin)
            
    except Exception as e:
        # Stampiamo l'errore nei log di Streamlit se qualcosa va storto
        print(f"Errore invio email: {e}")

# --- RESTO DEL CODICE (INVARIATO) ---
def gestisci_prenotazione(df, sheet):
    st.header("Aggiungi una prenotazione")
    col1, col2 = st.columns(2)

    nome_utente = st.session_state["nome_utente"]
    ruolo_utente = st.session_state["ruolo"]
    email_utente = st.session_state["email_utente"]

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
                stato_prenotazione = "Confermata"
                if ruolo_utente != "Admin" and data_inizio > data_limite_inizio:
                    stato_prenotazione = "In attesa"
                    st.warning("⏳ Data oltre i 31 giorni. La prenotazione sarà 'In attesa'.")

                sovrapposizione = False
                if not df.empty:
                    for _, row in df.iterrows():
                        if max(data_inizio, row['Data Inizio']) < min(data_fine, row['Data Fine']):
                            sovrapposizione = True
                            break
                
                if sovrapposizione:
                    st.error("❌ Errore: Le date si sovrappongono!")
                else:
                    durata = (data_fine - data_inizio).days
                    costo = 0 if ruolo_utente == "Admin" else (durata + 1) * 10
                    try:
                        inizio_str = data_inizio.strftime("%Y-%m-%d")
                        fine_str = data_fine.strftime("%Y-%m-%d")
                        sheet.append_row([nome_utente, inizio_str, fine_str, costo, durata + 1, note, stato_prenotazione])
                        
                        # Chiamata alla funzione email
                        invia_notifiche(nome_utente, email_utente, inizio_str, fine_str, stato_prenotazione)
                        
                        st.success(f"✅ Operazione completata!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore: {e}")
