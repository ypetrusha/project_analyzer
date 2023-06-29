import os
import openai
import json

from config import *


class ProjectAnalyzer:

    def __init__(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        openai.api_key = self.api_key
        self.conversation_history = [
            {"role": "system", "content": prompts['initial_prompt']}
        ]
        self.model = "gpt-3.5-turbo-16k"
        self.function_response = None
        self.function_type = "none"
        self.project_folder = None

    def set_project_folder(self, project_folder):
        self.project_folder = project_folder

    def set_function_type(self, type):
        if type == FUNC_GET_UPDATED_FILES:
            self.function_type = {"name": FUNC_GET_UPDATED_FILES}
        elif type == FUNC_GET_GIT_PATCH:
            self.function_type = {"name": FUNC_GET_GIT_PATCH}
        else:
            self.function_type = "none"

    def get_updated_files(self, files):
        for file in files:
            path = file['path']
            action = file['action']
            content = file['content']

            if action == 'create':
                self.create_file(path, content)
            elif action == 'update':
                self.update_file(path, content)
            elif action == 'delete':
                self.delete_file(path)

    def create_file(self, path, content):
        file_path = os.path.join(self.project_folder, path)
        with open(file_path, 'w') as file:
            file.write(content)

    def update_file(self, path, content):
        file_path = os.path.join(self.project_folder, path)
        with open(file_path, 'w') as file:
            file.write(content)

    def delete_file(self, path):
        file_path = os.path.join(self.project_folder, path)
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_git_patch(self, patch):
        print("patch:")
        print(patch)
        file_path = os.path.join(self.project_folder, "patch.diff")
        with open(file_path, 'w') as file:
            file.write(patch)

    def process_function_response(self):
        if self.function_response:
            name = self.function_response.name
            print("function_name", self.function_response.name)
            function_args = json.loads(self.function_response.arguments)
            if name == FUNC_GET_UPDATED_FILES:
                self.get_updated_files(function_args["files"])
            else:
                self.get_git_patch(function_args["patch"])

    def send_file(self, file_path, file_content):
        messages = self.conversation_history + [
            {"role": "user", "content": f"{file_path}:\n\n{file_content}\n\n"}
        ]

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            max_tokens=1,
            n=1,
            stop=None,
            temperature=0,
        )

        self.conversation_history = messages
        return response.choices[0].message['content']

    def send_files_to_chat(self, project_folder):
        project_folder = os.path.abspath(project_folder)

        for current_root, dirs, files in os.walk(project_folder):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(current_root, file)
                    yield file_path  # yield absolute file path

    def send_specific_request(self, request_text):
        messages = self.conversation_history + [
            {"role": "user", "content": request_text}
        ]
        print(messages)
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            max_tokens=8000,
            n=1,
            stop=None,
            temperature=0,
            functions=functions,
            function_call=self.function_type
        )

        self.conversation_history = messages

        response_message = response["choices"][0]["message"]
        print(response)
        content = response_message['content']
        if response_message.get("function_call"):
            self.function_response = response.choices[0].message.function_call
            # self.process_function_response()
            content = self.list_response_content()
        else:
            print(content)

        return (f"Request: {request_text}\nResponse:\n{content}\n{'-' * 80}\n")

    def list_response_content(self):
        name = self.function_response.name
        function_args = json.loads(self.function_response.arguments)
        content = f"function: {name}\ncomment: {function_args.get('comment')}\n"
        if name == FUNC_GET_UPDATED_FILES:
            files = function_args["files"]
            for file in files:
                content += f"path: {file['path']}\naction: {file['action']}\n{'-' * 80}\n{file['content']}\n{'-' * 80}\n"
        else:
            content += f"{function_args['patch']}"

        return content
