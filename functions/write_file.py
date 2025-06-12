import os
from pathlib import Path
from functions.utils import is_scoped_path

def write_file(working_directory, file_path, content):
    try:
        # Validate file_path is in working directory
        if is_scoped_path(working_directory, file_path):
            path = os.path.join(working_directory, file_path)
        else:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Write the content to the file
        with open(path, "w") as f:
            f.write(content)
        
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        
    
    except Exception as e:
        return f"Error: {e}"  