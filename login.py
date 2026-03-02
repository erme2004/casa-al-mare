import streamlit as st

def mostra_login():
    # Centriamo tutto per renderlo più carino
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔒 Accesso Riservato")
        st.write("Inserisci la password di famiglia per accedere al calendario.")

        # Creiamo un form per il login
        with st.form("login_form"):
            # L'opzione type="password" nasconde i caratteri con i pallini neri!
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Entra")

            if submit:
                # CAMBIA "mare2026" CON LA PASSWORD CHE VUOI TU!
                if password == "mare2026": 
                    # Il buttafuori ti fa passare!
                    st.session_state["autenticato"] = True
                    st.success("Accesso consentito! Caricamento...")
                    st.rerun() # Riavvia l'app per mostrare il calendario
                else:
                    st.error("❌ Password errata!")