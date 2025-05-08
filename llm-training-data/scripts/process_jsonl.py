import json

def process_jsonl_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            try:
                data = json.loads(line.strip())
                # Convert completion to string if it's a dict
                if isinstance(data['completion'], dict):
                    data['completion'] = json.dumps(data['completion'])
                # Write the processed line
                f_out.write(json.dumps(data) + '\n')
            except json.JSONDecodeError as e:
                print(f"Error processing line: {e}")
                continue

def main():
    # Process train.jsonl
    process_jsonl_file('training-data/jsons/train.jsonl', 'training-data/jsons/train_processed.jsonl')
    # Process test.jsonl
    process_jsonl_file('training-data/jsons/test.jsonl', 'training-data/jsons/test_processed.jsonl')

if __name__ == "__main__":
    main() 