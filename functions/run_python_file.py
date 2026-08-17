import os
import subprocess

schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Executes a Python file with optional command-line arguments and returns its output",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the Python file to execute, relative to the working directory",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of string arguments to pass to the Python file",
                },
            },
            "required": ["file_path"],
        },
    },
}


def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        working_abs = os.path.abspath(working_directory)
        target = os.path.normpath(os.path.join(working_abs, file_path))
        if os.path.commonpath([working_abs, target]) != working_abs:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target]
        if args:
            command.extend(args)

        result = subprocess.run(
            command,
            cwd=working_abs,
            capture_output=True,
            text=True,
            timeout=30,
        )

        parts = []
        if result.stdout:
            parts.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            parts.append(f"STDERR:\n{result.stderr}")
        if result.returncode != 0:
            parts.append(f"Process exited with code {result.returncode}")
        if not result.stdout and not result.stderr:
            parts.append("No output produced")
        return "\n".join(parts)
    except Exception as e:
        return f"Error: executing Python file: {e}"
