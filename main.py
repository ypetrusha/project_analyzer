import os
import openai
import tkinter as tk
from tkinter import filedialog, messagebox

# Set up OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

# Initialize global conversation history
conversation_history = [
    {"role": "system",
     "content": "You are a helpful assistant that analyzes Python code and provides suggestions for improvements. "
                "I'm going to send my project files one by one including relative file path and EOF mark. "
                "Please, no comments about the code at all. Just confirm that you received EOF mark."},
]


def browse_directory():
    folder_path = filedialog.askdirectory()
    if folder_path:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, folder_path)


def send_file(file_path, file_content):
    global conversation_history

    messages = conversation_history + [
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

    conversation_history = messages
    return response.choices[0].message['content']


def send_project_files():
    project_folder = dir_entry.get()

    if not project_folder:
        messagebox.showerror("Error", "Please select a project folder")
        return

    output_text.delete(1.0, tk.END)
    send_files_to_chat(project_folder)


def send_files_to_chat(project_folder):
    global conversation_history

    project_folder = os.path.abspath(project_folder)

    for current_root, dirs, files in os.walk(project_folder):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(current_root, file)
                relative_path = os.path.relpath(file_path, project_folder)
                with open(file_path, "r") as f:
                    file_content = f.read()
                    confirmation = send_file(relative_path, file_content)
                    output_text.insert(tk.END, f"File: {relative_path}\nConfirmation: {confirmation}\n{'-' * 80}\n")
                    root.update_idletasks()


def send_specific_request():
    global conversation_history

    request_text = specific_request_text.get(1.0, tk.END).strip()

    if not request_text:
        messagebox.showerror("Error", "Please enter a specific suggestion request")
        return

    messages = conversation_history + [
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

    conversation_history = messages
    output_text.insert(tk.END,
                       f"Request: {request_text}\nResponse: {response.choices[0].message['content']}\n{'-' * 80}\n")


# Create the main window
root = tk.Tk()
root.title("Python Project Analyzer")

# Create directory selection UI
dir_label = tk.Label(root, text="Project Folder:")
dir_label.grid(row=0, column=0, sticky="e", padx=(10, 5), pady=10)

dir_entry = tk.Entry(root, width=60)
dir_entry.grid(row=0, column=1, padx=(0, 5), pady=10)

browse_button = tk.Button(root, text="Browse", command=browse_directory)
browse_button.grid(row=0, column=2, padx=(0, 10), pady=10)

# Create send project files button
send_files_button = tk.Button(root, text="Send Project Files", command=send_project_files)
send_files_button.grid(row=1, column=0, columnspan=3, pady=(0, 10))

# Create specific request input UI
specific_request_label = tk.Label(root, text="Specific Request:")
specific_request_label.grid(row=2, column=0, sticky="e", padx=(10, 5), pady=10)

specific_request_text = tk.Text(root, wrap=tk.WORD, width=60, height=5)
specific_request_text.grid(row=2, column=1, padx=(0, 5), pady=10)

send_request_button = tk.Button(root, text="Send", command=send_specific_request)
send_request_button.grid(row=2, column=2, padx=(0, 10), pady=10)

# Create output text area
output_label = tk.Label(root, text="Output:")
output_label.grid(row=4, column=0, sticky="nw", padx=(10, 5), pady=(0, 5))

output_text = tk.Text(root, wrap=tk.WORD, width=80, height=20)
output_text.grid(row=5, column=0, columnspan=3, padx=(10, 10), pady=(0, 10), sticky="nsew")

output_scrollbar = tk.Scrollbar(root, command=output_text.yview)
output_scrollbar.grid(row=5, column=3, sticky="ns", pady=(0, 10))
output_text["yscrollcommand"] = output_scrollbar.set

# Allow the main window to resize its columns and rows
root.columnconfigure(0, weight=1)
root.rowconfigure(5, weight=1)

# Run the main loop
root.mainloop()