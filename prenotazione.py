import streamlit as st
from datetime import date, timedelta
import smtplib
from email.message import EmailMessage

# --- FUNZIONE PER INVIARE LA DOPPIA EMAIL ---
def invia_notifiche(nome, email_utente, inizio, fine, stato):
    try:
        mittente = st.secrets["email"]["mittente"]
        password = st.secrets["email"]["password"]
        email_admin = st.secrets["email"]["admin"]
        
        # 1. Email per l'Utente che ha prenotato
        msg_user = EmailMessage()
        msg_user['Subject'] = "🏖️ Riepilogo prenotazione Casa al Mare"
        msg_user['From'] = mittente
        msg_user['To'] = email_utente
        
        testo_user = f"Ciao {nome}!\n\nAbbiamo registrato la tua richiesta per la Casa al Mare.\n"
        testo_user += f"📅 Dal: {inizio}\n📅 Al: {fine}\n\n"
        if stato == "Confermata":
            testo_user += "✅ STATO: Confermata! Prepara le valigie.\n"
        else:
            testo_user += "⏳ STATO: In attesa. La tua richiesta supera i 31 giorni, ti avviseremo appena l'Admin la approverà!\n"
        msg_user.set_content(testo_user)
        
        # 2. Email per l'Admin (Sempre inviata!)
        msg_admin = EmailMessage()
        # Cambiamo l'oggetto in base allo stato per farlo saltare all'occhio
        prefisso = "✅ NUOVA PRENOTAZIONE" if stato == "Confermata" else "⚠️ RICHIESTA IN ATTESA"
        msg_admin['Subject'] = f"{prefisso} da {nome}"
        msg_admin['From'] = mittente
        msg_admin['To'] = email_admin
        
        testo_admin = f"Ciao Admin!\n\nC'è un nuovo movimento sul sito della Casa al Mare.\n\n"
        testo_admin += f"👤 Chi: {nome}\n"
        testo_admin += f"📅 Periodo: dal {inizio} al {fine}\n"
        testo_admin += f"📌 Stato: {stato}\n\n"
        
        if stato == "In attesa":
            testo_admin += "👉 Azione richiesta: Entra nell'app per approvarla o rifiutarla."
        else:
            testo_admin += "ℹ️ Questa prenotazione è stata confermata automaticamente dal sistema."
            
        msg_admin.set_content(testo_admin)
        
        # Invio effettivo
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(mittente, password)
            smtp.send_message(msg_user) # Manda all'utente
            
            # Manda all'admin sempre (a meno che l'utente non sia l'admin stesso, per non intasargli la posta)
            if email_utente != email_admin:
                smtp.send_message(msg_admin)
            
    except Exception as e:
        print(f"Errore email: {e}")

# --- FORM PRENOTAZIONE ---
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
                    st.warning("⏳ Data oltre i 31 giorni. La prenotazione sarà 'In attesa' di conferma.")

                sovrapposizione = False
                if not df.empty:
                    for _, row in df.iterrows():
                        if max(data_inizio, row['Data Inizio']) < min(data_fine, row['Data Fine']):
                            sovrapposizione = True
                            break
                
                if sovrapposizione:
                    st.error("❌ Errore: Le date si sovrappongono con una prenotazione esistente!")
                else:
                    durata = (data_fine - data_inizio).days
                    costo = 0 if ruolo_utente == "Admin" else (durata + 1) * 10
                    
                    try:
                        inizio_str = data_inizio.strftime("%Y-%m-%d")
                        fine_str = data_fine.strftime("%Y-%m-%d")
                        
                        sheet.append_row([nome_utente, inizio_str, fine_str, costo, durata + 1, note, stato_prenotazione])
                        
                        # INVIO NOTIFICHE (Ora l'Admin riceve tutto!)
                        invia_notifiche(nome_utente, email_utente, inizio_str, fine_str, stato_prenotazione)
                        
                        st.success(f"✅ Prenotazione {stato_prenotazione} salvata! Email inviata.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore: {e}")
