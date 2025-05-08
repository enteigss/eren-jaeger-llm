import json

input_file = "llm-training-data/training-data/training_data.jsonl"
output_file = "llm-training-data/training-data/training_data_updated.jsonl"

with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
    for line in f_in:
        data = json.loads(line.strip())
        old_completion = data['completion']
        new_completion = {
            "utterance": old_completion,
            "conversation_end": "N/A"
        }
        data['completion'] = new_completion
        f_out.write(json.dumps(data, ensure_ascii=False) + '\n') 