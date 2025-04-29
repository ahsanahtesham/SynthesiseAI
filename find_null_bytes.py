import os

def check_for_null_bytes(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            if b'\x00' in content:
                print(f'Null bytes found in: {file_path}')
                return True
    except Exception as e:
        print(f'Error checking {file_path}: {str(e)}')
    return False

# Check all Python files in the app directory
null_files = []
for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            if check_for_null_bytes(file_path):
                null_files.append(file_path)

if null_files:
    print(f'\nFound {len(null_files)} files with null bytes:')
    for file in null_files:
        print(f'  - {file}')
else:
    print('No files with null bytes found in the app directory.')
