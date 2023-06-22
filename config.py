prompts = {
    "initial_prompt": "You will be provided with project files one by one including relative file path and EOF mark."
                      "In response reply exactly 'EOF received' or 'EOF not found'.",

    "analyzer_prompt": "You are software developer profound in python coding. "
                       "You will be asked to refactor the code, add features and test coverage."
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
                                "description": "Full content of the file"
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
        "description": "Git diff file with header according to user request that can be applied as patch to project files",
        "parameters": {
            "type": "object",
            "properties": {
                "patch": {
                    "type": "string",
                    "description": "Git patch file content. Includes header with changed file info and index. "
                                   "Example: diff --git a/config.py b/config.py\\nindex 769a7b0..edff3c7 100644\\n--- a/config.py\\n+++ b/config.py",
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
