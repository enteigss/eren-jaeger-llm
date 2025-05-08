import json
import random

input_file = "llm-training-data/training-data/training_data_updated.jsonl"
train_file = "llm-training-data/training-data/train.jsonl"
test_file = "llm-training-data/training-data/test.jsonl"

# Read all lines from the input file
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Shuffle the lines randomly
random.shuffle(lines)

# Calculate split point (70% for training)
split_point = int(len(lines) * 0.7)

# Split into training and testing sets
train_lines = lines[:split_point]
test_lines = lines[split_point:]

# Write training data
with open(train_file, 'w', encoding='utf-8') as f:
    f.writelines(train_lines)

# Write testing data
with open(test_file, 'w', encoding='utf-8') as f:
    f.writelines(test_lines)

print(f"Total lines: {len(lines)}")
print(f"Training lines: {len(train_lines)} ({len(train_lines)/len(lines)*100:.1f}%)")
print(f"Testing lines: {len(test_lines)} ({len(test_lines)/len(lines)*100:.1f}%)") 