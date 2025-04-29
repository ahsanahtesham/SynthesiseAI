import os

# Essential directories
directories = [
    'app',
    'client',
    'client/static',
    'client/templates',
    'tests'
]

# Essential files
files = [
    'app/__init__.py',
    'app/main.py',
    'app/models.py',
    'app/schemas.py',
    'app/database.py',
    'app/crud.py',
    'app/auth.py',
    'app/queue.py',
    'app/external_api.py',
    'app/notifications.py',
    'app/config.py',
    'client/client.py',
    'client/static/styles.css',
    'client/static/script.js',
    '.env',
    'requirements.txt',
    'setup.py',
    'run.py'
]

print('Checking project structure...\n')

# Create directories
for directory in directories:
    if not os.path.exists(directory):
        print(f'Creating directory: {directory}')
        os.makedirs(directory, exist_ok=True)
    else:
        print(f'Directory exists: {directory}')

# Check files
missing_files = []
for file in files:
    if not os.path.exists(file):
        missing_files.append(file)
        print(f'MISSING: {file}')
    else:
        print(f'File exists: {file}')

print('\nSummary:')
if missing_files:
    print(f'Missing {len(missing_files)} files:')
    for file in missing_files:
        print(f'  - {file}')
    print('\nPlease create these files before running the application.')
else:
    print('All required files exist.')
