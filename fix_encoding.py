import os

def fix_file_encoding(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove any null bytes
        cleaned_content = content.replace('\0', '')
        
        # Write back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
            
        print(f'Fixed encoding for: {file_path}')
    except Exception as e:
        print(f'Error fixing {file_path}: {str(e)}')

# Process all Python files in the project
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            fix_file_encoding(path)
