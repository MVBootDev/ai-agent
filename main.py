import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.write_file import write_file
from functions.run_python import run_python_file

# Define function schemas
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Retrieves the contents of a file, with a maximum of 10000 characters. Returns an error if the file is outside the working directory or doesn't exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file, creating parent directories if they don't exist. Returns an error if the file would be outside the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path where to write the file, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file and returns its output. Times out after 30 seconds. Returns an error if the file is outside the working directory, doesn't exist, or isn't a Python file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
        },
    ),
)

# Define available functions
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file
    ]
)

robot_prompt='Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'

system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

# Map function names to their implementations
function_map = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "write_file": write_file,
    "run_python_file": run_python_file
}

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_name = function_call_part.name
    args = function_call_part.args
    args["working_directory"] = "./calculator"
    
    # Check if function exists in our map
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    # Function exists, call it and return the result
    res = function_map[function_name](**args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": res},
            )
        ],
    )

def main():
    args = sys.argv
    verbose = False

    # Check for prompt
    if len(args) == 1:
        print("Please provide a prompt")
        return
    # Optional --verbose check
    if len(args) > 2:
        verbose = True if sys.argv[2] == "--verbose" else False

    user_prompt = args[1]
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # Define the config for the LLM
    config = types.GenerateContentConfig(
        tools=[available_functions], 
        system_instruction=system_prompt
    )

    # Start conversation loop
    max_iterations = 20
    for iteration in range(max_iterations):
        if verbose:
            print(f"\nIteration {iteration + 1}/{max_iterations}")
        
        # Get response from LLM
        res = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=messages,
            config=config
        )
        
        # Add model's response to conversation
        if res.candidates:
            for candidate in res.candidates:
                if candidate.content:
                    messages.append(candidate.content)
        
        # Handle function calls
        if res.function_calls:
            for f in res.function_calls:
                if verbose:
                    print(f" - Calling function: {f.name}")
                value = call_function(f)
                messages.append(value)  # Add function result to conversation
        else:
            # No more function calls, we're done
            if hasattr(res, 'text') and res.text:
                print("\nFinal response:")
                print(res.text)
            break
    
    if verbose:
        print(f"\nUser prompt: {user_prompt}")    
        print(f"Prompt tokens: {res.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {res.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
    main()