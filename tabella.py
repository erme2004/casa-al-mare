import streamlit as st
import pandas as pd

def mostra_tabella(df, sheet_prenotazioni):
    st.header("📋 Lista Prenotazioni")
    
    ruolo = st.session_state.get("ruolo", "User")
    
    if not df.empty:
        # Assicuriamoci che esista la colonna per non far arrabbiare il codice
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
                        # Indice esatto della riga su Excel (i + 2)
                        riga_excel = i + 2 
                        testo = f"{row['Nome']} | Dal {row['Data Inizio']} al {row['Data Fine']}"
                        opzioni.append((riga_excel, testo))
                    
                    scelta = st.selectbox("Scegli la richiesta da gestire:", opzioni, format_func=lambda x: x[1])
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✅ Approva"):
                            # La colonna 7 è quella dello "Stato"
                            sheet_prenotazioni.update_cell(scelta[0], 7, "Confermata")
                            st.success("Approvata!")
                            st.rerun()
                                
                    with col_btn2:
                        if st.button("❌ Rifiuta (Elimina)"):
                            sheet_prenotazioni.delete_rows(scelta[0])
                            st.success("Eliminata!")
                            st.rerun()

        # --- VISUALIZZAZIONE NORMALE ---
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
