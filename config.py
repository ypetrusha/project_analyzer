prompts = {
    "initial_prompt": "You will be provided with project files one by one including relative file path."
                      "Format:{file_path}:\\n\\n{file_content}\\n\\n",

    "analyzer_prompt": "You are software developer profound in python coding. "
                       "You will be asked to refactor the code, add features and test coverage. "
}

FUNC_GET_UPDATED_FILES = "get_updated_files"
FUNC_GET_GIT_PATCH = "get_git_patch"

functions = [
    {
        "name": FUNC_GET_UPDATED_FILES,
        "description": "Project files created/updated/deleted according to user request",
        "parameters": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Relative path of the file"
                            },
                            "action": {
                                "type": "string",
                                "enum": ["create", "update", "delete"],
                                "description": "action performed on file"
                            },
                            "content": {
                                "type": "string",
                                "description": "1. Full content of the file. "
                                               "Do not omit any code. Example: in created file do not put '# Rest of the code...' comment, list all code instead. "
                                               "2. Escape new line symbols in single or double quotes. "
                                               "Example: f'Here is the Python file {file_path}:\\\n\\\n{file_content}\\\n\\\nEOF' "
                                               "3. Do not add empty lines"
                            },
                        },
                    },
                    "description": "Array of files affected as result of user request",
                },
                "comment": {
                    "type": "string",
                    "description": "Assistant comment"
                }
            },
            "required": ["files"],
        },
    },

    {
        "name": FUNC_GET_GIT_PATCH,
        "description": "Git diff file with all the changes according to user request",
        "parameters": {
            "type": "object",
            "properties": {
                "patch": {
                    "type": "string",
                    "description": "Git patch file content. It can contain changes to multiple files. "
                                   "Includes headers with changed files info and index. "
                                   "Example:\\n\\ndiff --git a/config.py b/config.py\\nindex 769a7b0..edff3c7 100644"
                                   "\\n--- a/config.py\\n+++ b/config.py\\n{changes to config.py}\\n"
                                   "diff --git a/ui.py b/ui.py\\nindex 7698ab0..edf3c7c7 100644"
                                   "\\n--- a/ui.py\\n+++ b/ui.py\\n{changes to ui.py}\\n\\n",
                },
                "comment": {
                    "type": "string",
                    "description": "Assistant comment"
                }
            },
            "required": ["patch", "comment"],
        },
    }
]
