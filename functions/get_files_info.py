import os

def get_files_info(working_directory, directory=None):
    try:
        # Handle "." as a special case - it represents the current directory
        if directory == ".":
            path = working_directory
        else:
            # If the directory argument is outside the working_directory, return a string with an error:
            if not directory in os.listdir(working_directory):
                return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
            path = os.path.join(working_directory, directory)

        # If the directory argument is not a directory, again, return an error string:
        if not os.path.isdir(path):
            return f'Error: "{directory}" is not a directory'

        # Build and return a string representing the contents of the directory. It should use this format:
        # - README.md: file_size=1032 bytes, is_dir=False
        # - src: file_size=128 bytes, is_dir=True
        # - package.json: file_size=1234 bytes, is_dir=False
        contents = os.listdir(path)
        return "\n".join([print_file_info(os.path.join(path, f)) for f in contents])
    
    # If any errors are raised by the standard library functions, catch them and instead return a string describing the error. Always prefix error strings with "Error:".
    except Exception as e:
        return f"Error: {e}"
    
def print_file_info(full_path):
        return f"- {os.path.basename(full_path)}: file_size={os.path.getsize(full_path)} bytes, is_dir={os.path.isdir(full_path)}"    

# Helpful functions:
# os.path.abspath(): Get an absolute path from a relative path
# os.path.join(): Join two paths together safely (handles slashes)
# .startswith(): Check if a string starts with a substring
# os.path.isdir(): Check if a path is a directory
# os.listdir(): List the contents of a directory
# os.path.getsize(): Get the size of a file
# os.path.isfile(): Check if a path is a file
# .join(): Join a list of strings together with a separator