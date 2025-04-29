import os
import sys

def fix_null_bytes(file_path):
    try:
        # Read the file as binary
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Remove null bytes
        fixed_content = content.replace(b'\x00', b'')
        
        # Write back the fixed content
        with open(file_path, 'wb') as f:
            f.write(fixed_content)
            
        print(f'Fixed null bytes in: {file_path}')
        return True
    except Exception as e:
        print(f'Error fixing {file_path}: {str(e)}')
        return False

# Fix a specific file if provided as an argument
if len(sys.argv) > 1:
    file_to_fix = sys.argv[1]
    if os.path.exists(file_to_fix):
        fix_null_bytes(file_to_fix)
    else:
        print(f'File not found: {file_to_fix}')
else:
    # Fix all Python files in the app directory
    fixed_files = []
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_null_bytes(file_path):
                    fixed_files.append(file_path)

    if fixed_files:
        print(f'\nFixed {len(fixed_files)} files:')
        for file in fixed_files:
            print(f'  - {file}')
    else:
        print('No files needed fixing.')
