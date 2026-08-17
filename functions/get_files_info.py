import os

schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}


def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        working_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_abs, directory))

        if directory == ".":
            header = "Result for current directory:"
        else:
            header = f"Result for '{directory}' directory:"

        if os.path.commonpath([working_abs, target_dir]) != working_abs:
            return (
                f"{header}\n"
                f'    Error: Cannot list "{directory}" as it is outside the permitted working directory'
            )

        if not os.path.isdir(target_dir):
            return f'{header}\n    Error: "{directory}" is not a directory'

        lines = [header]
        for name in os.listdir(target_dir):
            full_path = os.path.join(target_dir, name)
            size = os.path.getsize(full_path)
            is_dir = os.path.isdir(full_path)
            lines.append(f"- {name}: file_size={size} bytes, is_dir={is_dir}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"
