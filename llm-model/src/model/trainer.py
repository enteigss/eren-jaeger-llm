import os
import yaml
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training
)
from datasets import load_dataset
import wandb
from typing import Dict, Any

class ErenModelTrainer:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.trainer = None

    def setup_model(self):
        """Initialize the base model and tokenizer."""
        model_config = self.config['model']
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_config['base_model'],
            trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_config['base_model'],
            load_in_8bit=True,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Prepare model for LoRA training
        self.model = prepare_model_for_kbit_training(self.model)
        
        # Apply LoRA configuration
        lora_config = LoraConfig(
            r=self.config['lora']['r'],
            lora_alpha=self.config['lora']['alpha'],
            target_modules=self.config['lora']['target_modules'],
            lora_dropout=self.config['lora']['dropout'],
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()

    def prepare_dataset(self, data_path: str) -> Any:
        """Prepare the dataset for training."""
        dataset = load_dataset('csv', data_files=data_path)
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples['prompt'],
                padding="max_length",
                truncation=True,
                max_length=self.config['model']['max_length']
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset['train'].column_names
        )
        
        return tokenized_dataset

    def setup_training(self, train_dataset: Any, eval_dataset: Any = None):
        """Configure the training arguments and trainer."""
        training_config = self.config['training']
        
        training_args = TrainingArguments(
            output_dir="./eren_model",
            num_train_epochs=training_config['num_epochs'],
            per_device_train_batch_size=training_config['batch_size'],
            gradient_accumulation_steps=training_config['gradient_accumulation_steps'],
            learning_rate=training_config['learning_rate'],
            warmup_steps=training_config['warmup_steps'],
            max_grad_norm=training_config['max_grad_norm'],
            logging_steps=self.config['logging']['log_steps'],
            evaluation_strategy="steps" if eval_dataset else "no",
            eval_steps=self.config['logging']['eval_steps'] if eval_dataset else None,
            save_strategy="steps",
            save_steps=self.config['logging']['save_steps'],
            report_to="wandb" if self.config['logging']['wandb_project'] else None,
            load_best_model_at_end=True if eval_dataset else False
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator
        )

    def train(self):
        """Execute the training process."""
        if self.config['logging']['wandb_project']:
            wandb.init(project=self.config['logging']['wandb_project'])
        
        self.trainer.train()
        
        # Save the final model
        self.trainer.save_model("./eren_model/final")
        self.tokenizer.save_pretrained("./eren_model/final")

if __name__ == "__main__":
    # Example usage
    trainer = ErenModelTrainer("config/training_config.yaml")
    trainer.setup_model()
    
    # Prepare datasets
    train_dataset = trainer.prepare_dataset("data/processed/processed_dialogue.csv")
    eval_dataset = trainer.prepare_dataset("data/processed/processed_scenarios.csv")
    
    # Setup and start training
    trainer.setup_training(train_dataset, eval_dataset)
    trainer.train() 