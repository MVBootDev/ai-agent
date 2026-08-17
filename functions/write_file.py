import os


def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        working_abs = os.path.abspath(working_directory)
        target = os.path.normpath(os.path.join(working_abs, file_path))
        if os.path.commonpath([working_abs, target]) != working_abs:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        if os.path.isdir(target):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(target, "w") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error: {e}"
