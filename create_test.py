# Create a simple test file
with open('tests/test_simple.py', 'w', encoding='utf-8') as f:
    f.write('def test_simple():\n    assert 1 == 1\n')

print("Test file created successfully!")