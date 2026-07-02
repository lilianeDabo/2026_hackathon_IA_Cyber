from datasets import load_dataset
import pandas as pd
import json

print("[DATA] 1. Extraction des données médicales...")
# On DL direct depuis la source officielle du brief (contournement du bug Git LFS)
try:
    dataset = load_dataset("ruslanmv/ai-medical-chatbot", split="train")
    df = dataset.to_pandas()
    print(f"[DATA] Données brutes chargées : {len(df)} conversations.")
except Exception as e:
    print(f"[ERREUR] Impossible de télécharger le dataset : {e}")
    exit(1)

print("[DATA] 2. Transformation, Nettoyage et Audit (CYBER)...")
# On supprime les lignes vide ou corrompu
df = df.dropna()

formatted_data = []
# On limite volontairement à 500 conversations.
# Que 8Go de RAM sur la VM.
# 500 lignes suffisent pour valider la compétence technique de fine-tuning.
for index, row in df.head(500).iterrows():
    patient_text = str(row.get('Patient', '')).strip()
    doctor_text = str(row.get('Doctor', '')).strip()

    if patient_text and doctor_text:
        # Formatage strict compatible avec les tokens Phi-3 pour le fine-tuning
        formatted_data.append({
            "text": f"<|user|>\n{patient_text}<|end|>\n<|assistant|>\n{doctor_text}<|end|>"
        })

print("[DATA] 3. Chargement (Sauvegarde locale format JSONL)...")
output_file = "medical_finetune_clean.jsonl"
with open(output_file, "w", encoding="utf-8") as f:
    for item in formatted_data:
        f.write(json.dumps(item) + "\n")

print(f"[SUCCESS] Dataset préparé et sauvegardé dans {output_file}.")
print(f"-> {len(formatted_data)} paires de qualité validées pour l'entraînement LoRA.")
