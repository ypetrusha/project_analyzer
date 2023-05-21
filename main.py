import os
import openai
import tkinter as tk
from tkinter import filedialog, messagebox


class ProjectAnalyzer:

    def __init__(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        openai.api_key = self.api_key
        self.conversation_history = [
            {"role": "system",
            "content": "You are a helpful assistant that analyzes Python code and provides suggestions for improvements. "
                        "I'm going to send my project files one by one including relative file path and EOF mark. "
                        "Please, no comments about the code at all. Just confirm that you received EOF mark."},
        ]

    def send_file(self, file_path, file_content):
        messages = self.conversation_history + [
            {"role": "user", "content": f"Here is the Python file {file_path}:\n\n{file_content}\n\nEOF"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
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

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5,
        )

        self.conversation_history = messages
        return (f"Request: {request_text}\nResponse: {response.choices[0].message['content']}\n{'-' * 80}\n")


class ProjectAnalyzerUI:

    def __init__(self, analyzer):
        self.analyzer = analyzer

        # Create the main window
        self.root = tk.Tk()
        self.root.title("Project Analyzer")

        self.create_ui()

    def create_ui(self):
        # Create directory selection UI
        self.dir_entry = self.create_directory_ui()

        # Create send project files button
        send_files_button = tk.Button(self.root, text="Send Project Files", command=self.send_project_files)
        send_files_button.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        # Create specific request input UI
        self.specific_request_text = self.create_specific_request_ui()

        # Create output text area
        self.output_text = self.create_output_text_area()

        # Allow the main window to resize its columns and rows
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)

        # Run the main loop
        self.root.mainloop()

    def create_directory_ui(self):
        dir_label = tk.Label(self.root, text="Project Folder:")
        dir_label.grid(row=0, column=0, sticky="e", padx=(10, 5), pady=10)

        dir_entry = tk.Entry(self.root, width=60)
        dir_entry.grid(row=0, column=1, padx=(0, 5), pady=10)

        browse_button = tk.Button(self.root, text="Browse", command=self.browse_directory)
        browse_button.grid(row=0, column=2, padx=(0, 10), pady=10)

        return dir_entry

    def create_specific_request_ui(self):
        specific_request_label = tk.Label(self.root, text="Specific Request:")
        specific_request_label.grid(row=2, column=0, sticky="e", padx=(10, 5), pady=10)

        specific_request_text = tk.Text(self.root, wrap=tk.WORD, width=60, height=5)
        specific_request_text.grid(row=2, column=1, padx=(0, 5), pady=10)

        send_request_button = tk.Button(self.root, text="Send", command=self.send_specific_request)
        send_request_button.grid(row=2, column=2, padx=(0, 10), pady=10)

        return specific_request_text

    def create_output_text_area(self):
        output_label = tk.Label(self.root, text="Output:")
        output_label.grid(row=4, column=0, sticky="nw", padx=(10, 5), pady=(0, 5))

        output_text = tk.Text(self.root, wrap=tk.WORD, width=80, height=20)
        output_text.grid(row=5, column=0, columnspan=3, padx=(10, 10), pady=(0, 10), sticky="nsew")

        output_scrollbar = tk.Scrollbar(self.root, command=output_text.yview)
        output_scrollbar.grid(row=5, column=3, sticky="ns", pady=(0, 10))
        output_text["yscrollcommand"] = output_scrollbar.set

        return output_text

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

        self.output_text.delete(1.0, tk.END)
        self.file_generator = self.analyzer.send_files_to_chat(project_folder)
        self.process_next_file()

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
    analyzer = ProjectAnalyzer()
    ui = ProjectAnalyzerUI(analyzer)