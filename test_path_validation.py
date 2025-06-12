from functions.utils import is_scoped_path
import os

# Example working directory
working_dir = "/Users/example/project"

# Test cases
test_cases = [
    # Valid cases (should return True)
    ("project/file.txt", "Simple file in root"),
    ("src/main.py", "File in subdirectory"),
    ("src/utils/helper.py", "File in nested directory"),
    ("./config.json", "File with ./ prefix"),
    ("../project/file.txt", "File with ../ prefix but still in project"),
    
    # Invalid cases (should return False)
    ("/etc/passwd", "Absolute path outside project"),
    ("../../../etc/passwd", "Path trying to escape with multiple ../"),
    ("/Users/other/file.txt", "Path in different user directory"),
    ("/bin/bash", "System file"),
]

print("Testing is_scoped_path function:")
print("-" * 50)

for file_path, description in test_cases:
    result = is_scoped_path(working_dir, file_path)
    print(f"\nTest: {description}")
    print(f"File path: {file_path}")
    print(f"Working dir: {working_dir}")
    print(f"Result: {result}")
    print(f"Full resolved path: {os.path.abspath(os.path.join(working_dir, file_path))}")
    print("-" * 50) 