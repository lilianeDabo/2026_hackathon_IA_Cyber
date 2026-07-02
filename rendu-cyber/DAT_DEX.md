# 🏗️ DAT / DEX : Architecture & Exploitation IA TechCorp

**Date :** 2 juillet 2026  
**Projet :** Déploiement Assistant Financier & R&D Médicale  
**Statut :** PRODUCTION READY

---

## 1. ARCHITECTURE GLOBALE
Pour répondre aux contraintes matérielles de la machine virtuelle (CPU uniquement, 8 Go de RAM), l'architecture s'oriente vers des solutions légères et conteneurisées.

*   **Abandon de NVIDIA Triton :** Le serveur Triton (`tritton_server/`) a été écarté car il est inadapté à une inférence sur CPU et génère des erreurs de type "Out-Of-Memory". 
*   **Adoption d'Ollama :** Remplacement par le moteur Ollama, nativement optimisé pour le CPU grâce à la bibliothèque `llama.cpp` et au support de la quantification.
*   **Conteneurisation (Docker) :** L'ensemble des services de production est encapsulé via `docker-compose.yml`, créant un réseau privé (`techcorp-ai-chat_default`) isolant le backend (Ollama) du frontend (Streamlit).

---

## 2. EXPLOITATION : IA FINANCE (PRODUCTION)

L'Assistant Financier est le livrable principal, destiné aux analystes de TechCorp.

### 2.1. Déploiement du Backend (Ollama)
Le modèle utilisé est `Phi-3.5-Financial`. Son comportement et ses sécurités (Stop Tokens, Templates) sont figés directement lors de la compilation via un `Modelfile`. 
*   **Port d'écoute interne :** `127.0.0.1:11434`
*   **Commande de compilation :** `ollama create phi3.5-financial -f /models/Modelfile`

### 2.2. Déploiement du Frontend (Streamlit)
L'interface utilisateur webui a été développée en Python (Streamlit). Elle inclut une gestion des états (`st.session_state`) pour l'historique et un système de capture d'erreurs HTTP (ex: `404`) pour avertir l'utilisateur si le serveur IA est indisponible.
*   **Port d'accès utilisateur :** `0.0.0.0:8501`
*   **Lancement global :** `docker compose up -d --build`

---

## 3. EXPLOITATION : IA MÉDICALE (R&D EXPÉRIMENTALE)

Ce pipeline est strictement réservé au pôle IA pour l'entraînement d'adaptateurs locaux. Il s'exécute hors Docker, directement sur la machine hôte via un environnement virtuel isolé.

### 3.1. Prérequis et Environnement
```bash
sudo apt install python3-venv -y
python3 -m venv .venv
source .venv/bin/activate
pip install datasets pandas torch transformers peft
```

### 3.2. Pipeline Data (ETL)
Extraction de la source officielle depuis HuggingFace (pour contourner les fichiers Git LFS locaux corrompus), nettoyage des données vides, formatage selon les tokens du modèle cible, et extraction d'un sous-ensemble de 500 paires d'entraînement.
*   **Commande :** `python3 prepare_data.py`
*   **Livrable :** `medical_finetune_clean.jsonl`

### 3.3. Entraînement LoRA (Fine-Tuning)
Entraînement par méthode d'Adaptation Bas-Rang (LoRA) sur le modèle de base `TinyLlama/TinyLlama-1.1B-Chat-v1.0`. Le script utilise le `Trainer` standard de la bibliothèque `transformers` pour une stabilité maximale. L'entraînement est configuré sur `max_steps=10` et `batch_size=1` pour garantir l'exécution sur CPU.
*   **Commande :** `python3 train_lora.py`
*   **Livrable :** Poids de l'adaptateur dans le répertoire `./medical_model_lora_final`
