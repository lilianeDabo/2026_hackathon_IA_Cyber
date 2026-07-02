import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model
import os
# On importe le Trainer standard et le DataCollator


print("[IA] 1. Initialisation de l'entraînement LoRA (Mode CPU Optimisé)...")

model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
dataset_path = "medical_finetune_clean.jsonl"

print(f"[IA] Chargement du modèle de base : {model_id}")
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token 

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cpu", 
    torch_dtype=torch.float32
)

print("[IA] 2. Configuration de l'adaptateur LoRA...")
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

print("[IA] 3. Préparation et Tokenisation du Dataset...")
dataset = load_dataset("json", data_files=dataset_path, split="train")

# ÉTAPE CLÉ : On "tokenise" (traduit en nombres) le texte nous-mêmes pour le Trainer standard
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=256)

tokenized_dataset = dataset.map(tokenize_function, batched=True)
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

print("[IA] 4. Lancement de l'entraînement (Méthode robuste)...")
training_args = TrainingArguments(
    output_dir="./medical_model_lora",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    max_steps=10, 
    learning_rate=2e-4,
    logging_steps=2,
    optim="adamw_torch",
    save_strategy="no"
)

# Utilisation du Trainer classique, impossible à faire planter par des mises à jour
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

trainer.train()

print("[SUCCESS] Sauvegarde du modèle médical expérimental (Poids LoRA)...")
trainer.model.save_pretrained("./medical_model_lora_final")
print("[IA] Mission R&D validée. L'adaptateur est généré.")
