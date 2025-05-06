# Eren Jaeger LLM Fine-tuning Project

This project aims to create a fine-tuned language model that can generate dialogue and decision-making behavior characteristic of Eren Jaeger from Attack on Titan.

## Project Structure

```
eren-llm/
├── data/
│   ├── raw/                 # Raw dialogue and character data
│   ├── processed/           # Processed training data
│   └── evaluation/          # Evaluation datasets
├── src/
│   ├── data_processing/     # Data collection and preprocessing scripts
│   ├── model/              # Model architecture and training code
│   └── evaluation/         # Evaluation metrics and testing
├── config/                 # Configuration files
└── requirements.txt        # Project dependencies
```

## Key Components

1. **Data Collection**
   - Dialogue extraction from anime/manga
   - Character personality traits
   - Decision-making scenarios
   - Relationship mapping

2. **Model Architecture**
   - Base model: LLaMA-2 or similar
   - Fine-tuning approach: LoRA (Low-Rank Adaptation)
   - Training methodology: Supervised fine-tuning

3. **Evaluation**
   - Character consistency
   - Dialogue quality
   - Decision-making alignment
   - Relationship accuracy

## Requirements
- Python 3.8+
- PyTorch
- Transformers library
- PEFT (Parameter-Efficient Fine-Tuning)
- Other dependencies listed in requirements.txt 