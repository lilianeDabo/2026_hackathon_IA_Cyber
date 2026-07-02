import streamlit as st
import requests
import os

# Paramètre sécurisé injecté par Docker
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

st.set_page_config(page_title="TechCorp - IA", page_icon="📈")
st.title("Assistant Financier TechCorp")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Votre requête financière..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": "phi3.5-financial", # Nom temporaire, à adapter avec notre modèle financier
                    "messages": st.session_state.messages,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            reply = response.json()["message"]["content"]
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Erreur de communication avec le serveur d'inférence : {e}")
