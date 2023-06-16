import os
import openai
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # import ttk for the Combobox widget


class ProjectAnalyzer:

    def __init__(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        openai.api_key = self.api_key
        self.conversation_history = [
            {"role": "system",
            "content": "You will be provided with project files one by one including relative file path and EOF mark."
                       "In response reply exactly 'EOF received' or 'EOF not found'. Response size limited by 13 symbols."
                        }
        ]
        self.model = "gpt-3.5-turbo-16k"

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
        )

        self.conversation_history = messages
        print(response)
        return (f"Request: {request_text}\nResponse: {response.choices[0].message['content']}\n{'-' * 80}\n")


class ProjectAnalyzerUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Project Analyzer")
        self.analyzer = ProjectAnalyzer()

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

        self.model_combobox = ttk.Combobox(root, values=["gpt-3.5-turbo-16k", "text-davinci-003", "text-curie-003"], state='readonly')
        self.model_combobox.grid(row=1, column=1, padx=(0, 5), pady=10)
        self.model_combobox.set("gpt-3.5-turbo-16k")  # set the default value

        # Create send project files button
        send_files_button = tk.Button(root, text="Send Project Files", command=self.send_project_files)
        send_files_button.grid(row=2, column=0, columnspan=3, pady=(0, 10))

        # Create specific request input UI
        specific_request_label = tk.Label(root, text="Specific Request:")
        specific_request_label.grid(row=3, column=0, sticky="e", padx=(10, 5), pady=10)

        self.specific_request_text = tk.Text(root, wrap=tk.WORD, width=60, height=5)
        self.specific_request_text.grid(row=3, column=1, padx=(0, 5), pady=10)

        send_request_button = tk.Button(root, text="Send", command=self.send_specific_request)
        send_request_button.grid(row=3, column=2, padx=(0, 10), pady=10)

        # Create output text area
        output_label = tk.Label(root, text="Output:")
        output_label.grid(row=4, column=0, sticky="nw", padx=(10, 5), pady=(0, 5))

        self.output_text = tk.Text(root, wrap=tk.WORD, width=80, height=20)
        self.output_text.grid(row=5, column=0, columnspan=3, padx=(10, 10), pady=(0, 10), sticky="nsew")

        output_scrollbar = tk.Scrollbar(root, command=self.output_text.yview)
        output_scrollbar.grid(row=5, column=3, sticky="ns", pady=(0, 10))
        self.output_text["yscrollcommand"] = output_scrollbar.set

        # Allow the main window to resize its columns and rows
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)

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
            pass  # done processing files
            self.analyzer.conversation_history += [
                {"role": "system", "content":
                    "You are senior developer profound in python."
                    "You will be asked to refactor the code, add features and test coverage. "
                    "Answer providing full content for affected files."
                    "Provide your answers in the following form:"
                    "\n```\n\n---{path}---\n{file_content}\n---EOF---```\n"
                    "No other formatting."
                 }
            ]
        except Exception as e:
            messagebox.showerror("Error", str(e))  # show error message if any exceptions occur

    def send_specific_request(self):
        request_text = self.specific_request_text.get(1.0, tk.END).strip()

        if not request_text:
            messagebox.showerror("Error", "Please enter a specific suggestion request")
            return

        result_text = self.analyzer.send_specific_request(request_text)
        self.output_text.insert(tk.END, result_text)


if __name__ == "__main__":
    root = tk.Tk()
    ProjectAnalyzerUI(root)
    root.mainloop()