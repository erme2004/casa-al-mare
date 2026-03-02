import streamlit as st

def mostra_login(df_utenti):
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔒 Accesso Riservato")
        st.write("Inserisci le tue credenziali per accedere.")

        with st.form("login_form"):
            email_inserita = st.text_input("Email (tutta minuscola)").strip().lower()
            # 1. Abbiamo aggiunto il campo per la password segreta!
            password_inserita = st.text_input("Password", type="password") 
            submit = st.form_submit_button("Entra")

            if submit:
                if df_utenti.empty:
                    st.error("⚠️ Nessun utente nel database!")
                # 2. Controlliamo se l'email inserita esiste nella colonna Email
                elif email_inserita in df_utenti['Email'].str.lower().values:
                    # Troviamo la riga esatta di quell'utente nel foglio Excel
                    utente = df_utenti[df_utenti['Email'].str.lower() == email_inserita].iloc[0]
                    
                    # 3. Controlliamo se la password inserita è uguale a quella nel foglio!
                    # (Usiamo str() per sicurezza, nel caso mettessi password fatte solo di numeri)
                    password_corretta = str(utente['Password'])
                    
                    if password_inserita == password_corretta:
                        # Tutto perfetto! Salviamo i dati nella memoria
                        st.session_state["autenticato"] = True
                        st.session_state["email_utente"] = utente['Email']
                        st.session_state["nome_utente"] = utente['Nome']
                        st.session_state["ruolo"] = utente['Ruolo']
                        
                        st.success(f"Benvenuto/a {utente['Nome']}! Caricamento...")
                        st.rerun()
                    else:
                        st.error("❌ Password errata!")
                else:
                    st.error("❌ Email non trovata. Sicuro di averla scritta bene?")
