import os
import openai
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # import ttk for the Combobox widget
import tkinter.messagebox as messagebox
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
            {"role": "user", "content": f"Here is the Python file {file_path}:\n\n{file_content}\n\nEOF"}
        ]

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            max_tokens=10,
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
            temperature=0.1,
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
            content = self.function_response
        else:
            print(content)
        return (f"Request: {request_text}\nResponse: {content}\n{'-' * 80}\n")


class ProjectAnalyzerUI:

    def __init__(self, root, analyzer):
        self.root = root
        self.root.title("Project Analyzer")
        self.analyzer = analyzer

        # Set initial window size
        self.root.geometry("960x960")

        # Create directory selection UI
        dir_label = tk.Label(root, text="Project Folder:")
        dir_label.grid(row=0, column=0, sticky="e", padx=(10, 5), pady=10)

        self.dir_entry = tk.Entry(root, width=60)
        self.dir_entry.grid(row=0, column=1, padx=(0, 5), pady=10)

        browse_button = tk.Button(root, text="Browse", command=self.browse_directory)
        browse_button.grid(row=0, column=2, padx=(0, 10), pady=10)

        # Create model selection UI
        model_label = tk.Label(root, text="Model:")
        model_label.grid(row=1, column=0, sticky="e", padx=(10, 5), pady=10)

        self.model_combobox = ttk.Combobox(root, values=["gpt-3.5-turbo-16k", "text-davinci-003", "text-curie-003"],
                                           state='readonly')
        self.model_combobox.grid(row=1, column=1, padx=(0, 5), pady=10)
        self.model_combobox.set("gpt-3.5-turbo-16k")  # set the default value

        # Create function type selection UI
        function_type_label = tk.Label(root, text="Function Type:")
        function_type_label.grid(row=2, column=0, sticky="e", padx=(10, 5), pady=10)

        self.function_type_var = tk.StringVar(value="none")
        function_type_none_radio = tk.Radiobutton(root, text="None", variable=self.function_type_var, value="none",
                                                 command=lambda: self.analyzer.set_function_type("none"))
        function_type_none_radio.grid(row=2, column=1, padx=(0, 5), pady=10)

        function_type_files_radio = tk.Radiobutton(root, text="Get Updated Files", variable=self.function_type_var,
                                                  value=FUNC_GET_UPDATED_FILES,
                                                  command=lambda: self.analyzer.set_function_type(FUNC_GET_UPDATED_FILES))
        function_type_files_radio.grid(row=2, column=2, padx=(0, 5), pady=10)

        function_type_patch_radio = tk.Radiobutton(root, text="Get Git Patch", variable=self.function_type_var,
                                                  value=FUNC_GET_GIT_PATCH,
                                                  command=lambda: self.analyzer.set_function_type(FUNC_GET_GIT_PATCH))
        function_type_patch_radio.grid(row=2, column=3, padx=(0, 10), pady=10)

        # Create send project files button
        send_files_button = tk.Button(root, text="Send Project Files", command=self.send_project_files)
        send_files_button.grid(row=3, column=0, columnspan=4, pady=(0, 10))

        # Create specific request input UI
        specific_request_label = tk.Label(root, text="Specific Request:")
        specific_request_label.grid(row=4, column=0, sticky="e", padx=(10, 5), pady=10)

        self.specific_request_text = tk.Text(root, wrap=tk.WORD, width=60, height=5)
        self.specific_request_text.grid(row=4, column=1, padx=(0, 5), pady=10)

        send_request_button = tk.Button(root, text="Send", command=self.send_specific_request)
        send_request_button.grid(row=4, column=2, padx=(0, 10), pady=10)

        # Create process function response button
        process_response_button = tk.Button(root, text="Process Function Response", command=self.process_function_response)
        process_response_button.grid(row=5, column=0, columnspan=4, pady=(0, 10))

        # Create output text area
        output_label = tk.Label(root, text="Output:")
        output_label.grid(row=6, column=0, sticky="nw", padx=(10, 5), pady=(0, 5))

        self.output_text = tk.Text(root, wrap=tk.WORD, width=80, height=20)
        self.output_text.grid(row=7, column=0, columnspan=4, padx=(10, 10), pady=(0, 10), sticky="nsew")

        output_scrollbar = tk.Scrollbar(root, command=self.output_text.yview)
        output_scrollbar.grid(row=7, column=4, sticky="ns", pady=(0, 10))
        self.output_text["yscrollcommand"] = output_scrollbar.set

        # Allow the main window to resize its columns and rows
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(7, weight=1)

    def browse_directory(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder_path)

    def send_project_files(self):
        project_folder = self.dir_entry.get()

        if not project_folder:
            messagebox.showerror("Error", "Please select a project folder")
            return

        self.analyzer.set_project_folder(project_folder)

        # Set the model
        self.analyzer.model = self.model_combobox.get()

        # Initialize the generator for the project files
        self.file_generator = self.analyzer.send_files_to_chat(project_folder)

        # Schedule the processing of the first file
        self.root.after(1, self.process_next_file)

    def process_next_file(self):
        try:
            file_path = next(self.file_generator)
            with open(file_path, "r") as f:
                file_content = f.read()
            relative_path = os.path.relpath(file_path, self.dir_entry.get())
            confirmation = self.analyzer.send_file(relative_path, file_content)
            result_text = f"File: {relative_path}\nConfirmation: {confirmation}\n{'-' * 80}\n"
            self.output_text.insert(tk.END, result_text)
            self.root.after(1, self.process_next_file)  # schedule the processing of the next file
        except StopIteration:
            self.analyzer.conversation_history += [{"role": "system", "content": prompts['analyzer_prompt']}]

    def send_specific_request(self):
        request_text = self.specific_request_text.get(1.0, tk.END).strip()
        if not request_text:
            messagebox.showerror("Error", "Please enter a specific request")
            return

        response = self.analyzer.send_specific_request(request_text)
        self.output_text.insert(tk.END, response)

    def process_function_response(self):
        # Display a confirmation dialog
        result = messagebox.askquestion("Confirmation", "This action will override project files. Are you sure you want to proceed?", icon="warning")
        if result == "yes":
            self.analyzer.process_function_response()
        else:
            messagebox.showinfo("Cancelled", "Action cancelled.")

def main():
    root = tk.Tk()
    analyzer = ProjectAnalyzer()
    ui = ProjectAnalyzerUI(root, analyzer)
    root.mainloop()


if __name__ == "__main__":
    main()