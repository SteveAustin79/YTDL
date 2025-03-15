import tkinter as tk
from tkinter import ttk, Listbox, scrolledtext
from PIL import Image, ImageTk

# Function to update console output
def update_console(text):
    console_output.insert(tk.END, text + "\n")
    console_output.see(tk.END)

# Function to handle dropdown selection
def dropdown_selected(event):
    update_console(f"Selected: {dropdown_var.get()}")

# Function to handle listbox selection
def list_selected(event):
    selected_item = listbox.get(listbox.curselection())
    update_console(f"List Selected: {selected_item}")

# Function to display an image
def load_image():
    img = Image.open("example.jpg")  # Replace with your image path
    img = img.resize((200, 200))  # Resize to fit
    img_tk = ImageTk.PhotoImage(img)
    image_label.config(image=img_tk)
    image_label.image = img_tk  # Keep reference to avoid garbage collection

# Create main window
root = tk.Tk()
root.title("Python GUI Example")
root.geometry("600x400")

# Create image display area
image_label = tk.Label(root)
image_label.grid(row=0, column=0, padx=10, pady=10, rowspan=2)
load_image()

# Create dropdown menu
dropdown_var = tk.StringVar()
dropdown = ttk.Combobox(root, textvariable=dropdown_var, values=["Option 1", "Option 2", "Option 3"])
dropdown.grid(row=0, column=1, padx=10, pady=10)
dropdown.bind("<<ComboboxSelected>>", dropdown_selected)

# Create listbox
listbox = Listbox(root, height=5)
listbox.grid(row=1, column=1, padx=10, pady=10)
for item in ["Item 1", "Item 2", "Item 3", "Item 4"]:
    listbox.insert(tk.END, item)
listbox.bind("<<ListboxSelect>>", list_selected)

# Create console output area
console_output = scrolledtext.ScrolledText(root, width=50, height=10)
console_output.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Run the GUI
root.mainloop()
