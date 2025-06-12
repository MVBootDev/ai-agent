import os
import subprocess
from functions.utils import is_scoped_path

def run_python_file(working_directory, file_path):
    try:
        if not is_scoped_path(working_directory, file_path):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.exists(os.path.join(working_directory, file_path)):
            return f'Error: File "{file_path}" not found.'
        
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file.'
        
        try:
            # Run the Python file using subprocess.run:
            # - capture_output=True captures both stdout and stderr
            # - text=True returns strings instead of bytes
            # - timeout=30 prevents infinite execution
            # - cwd sets the working directory for the subprocess
            result = subprocess.run(
                ['python3', file_path],  # Use file_path directly since cwd is set
                capture_output=True,
                text=True, 
                timeout=30,
                cwd=working_directory
            )
            
            # Format and return the execution results
            output_parts = []
            
            if result.stdout:
                output_parts.append(f"STDOUT: {result.stdout}")
            if result.stderr:
                output_parts.append(f"STDERR: {result.stderr}")
            if result.returncode != 0:
                output_parts.append(f"Process exited with code {result.returncode}")
                
            if not output_parts:
                return "No output produced."
                
            return "\n".join(output_parts)
            
        except subprocess.TimeoutExpired:
            return "Error: Execution timed out after 30 seconds"

    except Exception as e:
        return f"Error: executing Python file: {e}"