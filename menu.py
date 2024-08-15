import os
import sys
import tkinter as tk
from tkinter import ttk
import webbrowser

# Function to get the absolute path to the resource
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Set the base path to the location of the executable or script
base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

def format_group_name(folder_name):
    """Convert folder_name like 'password_recovery' to 'Password Recovery'."""
    return folder_name.replace('_', ' ').title()

def scan_apps_directory():
    app_list = []
    apps_path = os.path.join(base_path, "apps")
    
    for group_name in os.listdir(apps_path):
        group_path = os.path.join(apps_path, group_name)
        if os.path.isdir(group_path):
            # Apply formatting to the group name
            formatted_group_name = format_group_name(group_name)
            for app_name in os.listdir(group_path):
                app_folder = os.path.join(group_path, app_name)
                if os.path.isdir(app_folder):
                    for file_name in os.listdir(app_folder):
                        # Exclude 'peview.exe' from being added to the app list
                        if file_name.endswith(".exe") and file_name.lower() != "peview.exe":
                            app_path = os.path.join(app_folder, file_name)
                            app_list.append({"Group": formatted_group_name, "Name": file_name.replace(".exe", ""), "Path": app_path})
    
    # Sort the list alphabetically by group name
    app_list.sort(key=lambda x: (x["Group"], x["Name"]))
    return app_list

# Get the dynamic list of applications
app_list = scan_apps_directory()

def update_list(search_text):
    # Clear the current list contents
    for item in list_view.get_children():
        list_view.delete(item)
    
    # Add items to the list based on the search query
    for app in app_list:
        if search_text.lower() in app["Name"].lower() or search_text.lower() in app["Group"].lower():
            list_view.insert("", "end", values=(app["Group"], app["Name"]))

def launch_app(event):
    selected_item = list_view.selection()[0]
    app_name = list_view.item(selected_item, "values")[1]
    
    for app in app_list:
        if app["Name"] == app_name:
            try:
                os.startfile(app["Path"])
            except OSError as e:
                # Ignore the specific error when the user cancels the operation
                if e.winerror == 1223:
                    print(f"Operation cancelled by the user for {app['Path']}")
                else:
                    # If it's another error, re-raise it
                    raise

def open_github(event):
    webbrowser.open_new("https://github.com/h0ek/SysPwn")

# Create the main window
root = tk.Tk()
root.title("SysPwn")
root.geometry("300x450")  # Setting the initial window size

# Minimum window size limitation
root.minsize(300, 300)

# Set the custom icon
icon_path = resource_path("tools.ico")
root.iconbitmap(icon_path)

# Restrict resizing to vertical only
root.resizable(width=False, height=True)

# Search entry
search_var = tk.StringVar()
search_var.trace("w", lambda name, index, mode: update_list(search_var.get()))
search_entry = tk.Entry(root, textvariable=search_var, width=40)
search_entry.pack(pady=10)

# Frame to hold the Treeview and vertical scrollbar
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Vertical scrollbar
scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

# Application list (Treeview)
columns = ("Group", "Application")
list_view = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=scrollbar_y.set)
list_view.heading("Group", text="Group")
list_view.heading("Application", text="Application")

# Set the column widths
list_view.column("Group", width=120)  # Narrowing the "Group" column
list_view.column("Application", width=160)  # Adjusting the "Application" column width

list_view.pack(fill=tk.BOTH, expand=True)

# Link the vertical scrollbar to the list_view
scrollbar_y.config(command=list_view.yview)

# Handle double-click to launch the application
list_view.bind("<Double-1>", launch_app)

# Label for GitHub link
github_label = tk.Label(root, text="Source", fg="blue", cursor="hand2", anchor="w")
github_label.pack(pady=10, anchor="w", side="left", padx=10)
github_label.bind("<Button-1>", open_github)

# Initial load of the application list
update_list("")

# Start the main application loop
root.mainloop()
