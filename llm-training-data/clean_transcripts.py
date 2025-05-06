import os

def clean_file(file_path):
    """Remove lines between 'Character List:' and 'Do not ask for permission' (inclusive)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip_lines = False
    
    for line in lines:
        if 'Character List:' in line:
            skip_lines = True
            continue
            
        if skip_lines and 'Do not ask for permission' in line:
            skip_lines = False
            continue
            
        if not skip_lines:
            new_lines.append(line)
    
    # Write back to the same file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def main():
    transcript_dir = "episode-transcripts/transcript-txts"
    
    # Process all txt files
    for filename in os.listdir(transcript_dir):
        if filename.endswith('.txt'):
            print(f"Processing {filename}...")
            file_path = os.path.join(transcript_dir, filename)
            clean_file(file_path)
            print(f"Completed {filename}")

if __name__ == "__main__":
    main() 