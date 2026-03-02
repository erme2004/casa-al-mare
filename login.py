import streamlit as st
import time
import hashlib # Il nostro "tritacarne" per criptare le password!

# --- FUNZIONE PER CRIPTARE ---
def cripta_password(password):
    # Trasforma la password in una stringa illeggibile di 64 caratteri
    return hashlib.sha256(password.encode()).hexdigest()

def mostra_login(df_utenti, sheet_utenti):
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🏡 Casa al Mare")
        
        tab_login, tab_registrazione = st.tabs(["🔑 Login", "📝 Registrati"])
        
        # --- SCHEDA LOGIN ---
        with tab_login:
            st.write("Hai già un account? Entra qui.")
            with st.form("login_form"):
                email_inserita = st.text_input("Email").strip().lower()
                password_inserita = st.text_input("Password", type="password") 
                submit_login = st.form_submit_button("Entra")

                if submit_login:
                    if df_utenti.empty:
                        st.error("⚠️ Nessun utente nel database! Registrati prima.")
                    elif email_inserita in df_utenti['Email'].str.lower().values:
                        utente = df_utenti[df_utenti['Email'].str.lower() == email_inserita].iloc[0]
                        
                        # Prendiamo la password criptata salvata sul foglio
                        password_salvata_criptata = str(utente['Password'])
                        
                        # Criptiamo la password appena digitata per vedere se sono uguali!
                        password_inserita_criptata = cripta_password(password_inserita)
                        
                        if password_inserita_criptata == password_salvata_criptata:
                            st.session_state["autenticato"] = True
                            st.session_state["email_utente"] = utente['Email']
                            st.session_state["nome_utente"] = utente['Nome']
                            st.session_state["ruolo"] = utente['Ruolo']
                            
                            st.success(f"Benvenuto/a {utente['Nome']}! Caricamento...")
                            st.rerun()
                        else:
                            st.error("❌ Password errata!")
                    else:
                        st.error("❌ Email non trovata. Vai sulla scheda 'Registrati'!")

        # --- SCHEDA REGISTRAZIONE ---
        with tab_registrazione:
            st.write("Crea un nuovo account per la famiglia.")
            with st.form("register_form"):
                nuovo_nome = st.text_input("Come ti chiami?")
                nuova_email = st.text_input("La tua Email").strip().lower()
                nuova_password = st.text_input("Scegli una Password", type="password")
                conferma_password = st.text_input("Conferma la Password", type="password")
                
                submit_registrazione = st.form_submit_button("Crea Account")
                
                if submit_registrazione:
                    if not nuovo_nome or not nuova_email or not nuova_password:
                        st.error("⚠️ Compila tutti i campi!")
                    elif nuova_password != conferma_password:
                        st.error("⚠️ Le password non combaciano!")
                    elif not df_utenti.empty and nuova_email in df_utenti['Email'].str.lower().values:
                        st.error("⚠️ Questa email è già registrata! Torna al Login.")
                    else:
                        try:
                            ruolo_base = "User" 
                            
                            # ---> LA MAGIA: Criptiamo la password prima di inviarla a Google Sheets! <---
                            password_sicura = cripta_password(nuova_password)
                            
                            # Salviamo sul foglio la versione illeggibile
                            sheet_utenti.append_row([nuova_email, nuovo_nome, ruolo_base, password_sicura])
                            
                            st.session_state["autenticato"] = True
                            st.session_state["email_utente"] = nuova_email
                            st.session_state["nome_utente"] = nuovo_nome
                            st.session_state["ruolo"] = ruolo_base
                            
                            st.success("✅ Registrazione completata in modo sicuro! Accesso in corso...")
                            time.sleep(2) 
                            st.rerun() 
                        except Exception as e:
                            st.error(f"Errore durante il salvataggio: {e}")
