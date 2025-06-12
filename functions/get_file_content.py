import os
from pathlib import Path
from functions.utils import is_scoped_path

def get_file_content(working_directory, file_path):
    try:
        # Validate file_path is in working directory
        if is_scoped_path(working_directory, file_path):
            path = os.path.join(working_directory, file_path)
        else:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Validate that the path points to a file
        if not os.path.isfile(path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        MAX_CHARS = 10000
        with open(path, "r") as f:
             content = f.read(MAX_CHARS)

        if len(content) == MAX_CHARS:
             content += f"[...File '{file_path}' truncated at 10000 characters]"

        return content
    
    # If any errors are raised by the standard library functions, catch them and instead return a string describing the error. Always prefix error strings with "Error:".
    except Exception as e:
        return f"Error: {e}"  