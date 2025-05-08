import os

def update_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the comment block marker
    marker = "<commentblockmarker>###</commentblockmarker>"
    if marker in content:
        # Add the current stage line after the marker
        new_content = content.replace(marker, f"{marker}\nCurrent stage: current stage")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file_path}")
    else:
        print(f"No marker found in {file_path}")

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                update_template(file_path)

# Process all template directories
template_dirs = ['prompt-templates/v1', 'prompt-templates/v2', 'prompt-templates/v3_ChatGPT']
for dir in template_dirs:
    if os.path.exists(dir):
        process_directory(dir)
    else:
        print(f"Directory {dir} not found") 