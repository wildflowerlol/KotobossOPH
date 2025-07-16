import json
import tkinter as tk
from tkinter import messagebox, filedialog

def save_dict_to_file(data, filename):
    """Saves a dictionary to a file in JSON format."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def load_dict_from_file(filename):
    """Loads a dictionary from a file in JSON format."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def add_entry():
    key = key_entry.get().strip()
    value = value_entry.get().strip()
    
    if key and value:
        if len(user_data) != 10:
            user_data[key] = value
            update_display()
            key_entry.delete(0, tk.END)
            value_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Limit Reached", "You can only 10 entries.")
    else:
        messagebox.showwarning("Input Error", "Both key and value must be provided.")

def delete_last_entry():
    """Removes the last added key-value pair from user_data."""
    if user_data:
        last_key = list(user_data.keys())[-1]  # Get the last key added
        del user_data[last_key]  # Remove it
        update_display()
    else:
        messagebox.showwarning("No Entries", "There are no entries to delete.")

def update_display():
    """Updates the display box with the latest dictionary content."""
    display_box.config(state=tk.NORMAL)  # Enable text editing
    display_box.delete(1.0, tk.END)
    for key, value in user_data.items():
        display_box.insert(tk.END, f"{key}: {value}\n")
    display_box.config(state=tk.DISABLED)  # Make text box read-only

def save_to_file():
    filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if filename:
        save_dict_to_file(user_data, filename)
        messagebox.showinfo("Success", "Data saved successfully.")

def load_from_file():
    filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if filename:
        global user_data
        user_data = load_dict_from_file(filename)
        update_display()

def clear_data():
    """Clears all stored data."""
    global user_data
    user_data = {}
    update_display()
    
# Initialize the GUI window
root = tk.Tk()
root.resizable(width=False, height=False)
root.title("KotoBoss' List Manager")

user_data = {}

# Input Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Word :").grid(row=0, column=0, padx=5)
key_entry = tk.Entry(input_frame, width=20)
key_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Meaning :").grid(row=1, column=0, padx=5)
value_entry = tk.Entry(input_frame, width=20)
value_entry.grid(row=1, column=1, padx=5)

add_button = tk.Button(input_frame, text="+", command=add_entry)
add_button.grid(row=2, column=0, columnspan=2, pady=5)

# Display Box (Now Read-Only)
display_box = tk.Text(root, width=40, height=10, wrap=tk.WORD, state=tk.DISABLED)
display_box.pack(pady=10)

# Action Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

save_button = tk.Button(button_frame, text="Save to File", command=save_to_file)
save_button.grid(row=0, column=0, padx=5)

load_button = tk.Button(button_frame, text="Load from File", command=load_from_file)
load_button.grid(row=0, column=1, padx=5)

clear_button = tk.Button(button_frame, text="Clear Data", command=clear_data)
clear_button.grid(row=0, column=2, padx=5)

delete_button = tk.Button(button_frame, text="Delete Last Entry", command=delete_last_entry)
delete_button.grid(row=0, column=3, padx=5)

# Run the application
root.mainloop()