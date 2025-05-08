from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer
from datasets import load_dataset
import torch

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

# Load model
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,
    device_map="auto",
    torch_dtype=torch.float16
)

# LoRA config
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=64,
    lora_alpha=16,
    lora_dropout=0.1,
    bias="none"
)

# Apply LoRA
model = get_peft_model(model, peft_config)

# Load dataset
dataset = load_dataset("json", data_files={"train": "../llm-training-data/training-data/jsons/train_processed.jsonl", "test": "../llm-training-data/training-data/jsons/test_processed.jsonl"})

# SFTTrainer args
training_args = TrainingArguments(
    output_dir="mistral-lora",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    logging_steps=10,
    save_strategy="epoch",
    eval_strategy="epoch",
    fp16=True,
    report_to="none"
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    args=training_args
)

trainer.train()



