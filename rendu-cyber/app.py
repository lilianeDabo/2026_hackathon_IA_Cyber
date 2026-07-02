import streamlit as st
import requests

st.set_page_config(page_title="TechCorp Financial Assistant", page_icon="🤖")

OLLAMA_URL = "http://localhost:11434" # À remplacer par ton IP si les dévs sont à distance
MODEL_NAME = "phi3-financial"

# 1. Vérification de l'état de la connexion (Consigne)
try:
    response = requests.get(OLLAMA_URL)
    if response.status_code == 200:
        st.sidebar.success("🟢 Serveur Connecté")
        server_available = True
    else:
        st.sidebar.error("🔴 Erreur Serveur (Statut anormal)")
        server_available = False
except requests.exceptions.ConnectionError:
    st.sidebar.error("🔴 Serveur Déconnecté")
    server_available = False

st.title("🤖 Assistant Financier - TechCorp")

# Initialisation de l'historique dans la session Streamlit (Consigne)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie utilisateur
if prompt := st.chat_input("Posez votre question financière...", disabled=not server_available):
    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Appel à l'API d'Ollama
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Envoi de la requête à Ollama (endpoint de chat)
            res = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": MODEL_NAME,
                    "messages": st.session_state.messages,
                    "stream": False # On peut passer à True plus tard pour l'effet "streaming"
                }
            )
            if res.status_code == 200:
                full_response = res.json()["message"]["content"]
                message_placeholder.markdown(full_response)
                # Ajouter la réponse de l'assistant à l'historique
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error("Erreur lors de la génération de la réponse.")
        except Exception as e:
            st.error(f"Erreur de communication : {e}")