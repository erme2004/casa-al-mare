import streamlit as st
import time

def mostra_login(df_utenti, sheet_utenti):
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🏡 Casa al Mare")
        
        # Creiamo le due linguette (Tabs) in alto
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
                        password_corretta = str(utente['Password'])
                        
                        if password_inserita == password_corretta:
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
                    # Controlli di sicurezza
                    if not nuovo_nome or not nuova_email or not nuova_password:
                        st.error("⚠️ Compila tutti i campi!")
                    elif nuova_password != conferma_password:
                        st.error("⚠️ Le password non combaciano!")
                    elif not df_utenti.empty and nuova_email in df_utenti['Email'].str.lower().values:
                        st.error("⚠️ Questa email è già registrata! Torna al Login.")
                    else:
                        # Tutto ok, scriviamo su Google Sheets!
                        try:
                            ruolo_base = "User" # Tutti nascono "User"
                            # Inseriamo i dati nell'ordine esatto delle colonne: Email, Nome, Ruolo, Password
                            sheet_utenti.append_row([nuova_email, nuovo_nome, ruolo_base, nuova_password])
                            st.success("✅ Registrazione completata con successo! Tra 3 secondi si aggiornerà la pagina.")
                            time.sleep(3) # Pausa per far leggere il messaggio
                            st.rerun() # Ricarica l'app
                        except Exception as e:
                            st.error(f"Errore durante il salvataggio: {e}")

