import os
from pathlib import Path

def is_scoped_path(scoped_path, file_path):
    # Convert both paths to absolute paths
    scoped_abs = os.path.abspath(scoped_path)
    file_abs = os.path.abspath(os.path.join(scoped_path, file_path))
    
    # Check if the file path is within the scoped directory
    return file_abs.startswith(scoped_abs)