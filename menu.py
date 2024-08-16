import os
import sys
import tkinter as tk
from tkinter import ttk
import webbrowser

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

def format_group_name(folder_name):
    """Convert folder_name like 'password_recovery' to 'Password Recovery'."""
    return folder_name.replace('_', ' ').title()

def load_exclusions():
    """Load excluded files from the exclude.cfg file."""
    exclusion_file = os.path.join(base_path, "exclude.cfg")
    if os.path.exists(exclusion_file):
        with open(exclusion_file, "r") as f:
            exclusions = f.read().splitlines()
        return [ex.lower() for ex in exclusions]
    return []

def scan_apps_directory():
    """Scan the 'apps' directory for executable files and return a list of applications."""
    app_list = []
    exclusions = load_exclusions()
    apps_path = os.path.join(base_path, "apps")
    
    for group_name in os.listdir(apps_path):
        group_path = os.path.join(apps_path, group_name)
        if os.path.isdir(group_path):
            formatted_group_name = format_group_name(group_name)
            for app_name in os.listdir(group_path):
                app_folder = os.path.join(group_path, app_name)
                if os.path.isdir(app_folder):
                    for file_name in os.listdir(app_folder):
                        if file_name.endswith(".exe") and file_name.lower() not in exclusions:
                            app_path = os.path.join(app_folder, file_name)
                            app_list.append({"Group": formatted_group_name, "Name": file_name.replace(".exe", ""), "Path": app_path})

    # Manually added entry for PowerShell
    app_list.append({"Group": "Local", "Name": "PowerShell", "Path": "powershell"})
    
    app_list.sort(key=lambda x: (x["Group"], x["Name"]))
    return app_list

app_list = scan_apps_directory()

def update_list(search_text):
    """Update the application list based on the search text."""
    for item in list_view.get_children():
        list_view.delete(item)
    
    for app in app_list:
        if search_text.lower() in app["Name"].lower() or search_text.lower() in app["Group"].lower():
            list_view.insert("", "end", values=(app["Group"], app["Name"]))

def launch_app(event):
    """Launch the selected application."""
    selected_item = list_view.selection()[0]
    app_name = list_view.item(selected_item, "values")[1]
    
    for app in app_list:
        if app["Name"] == app_name:
            try:
                if app["Name"] == "PowerShell":
                    # Change directory to /apps/ and launch PowerShell
                    apps_folder = os.path.join(base_path, "apps")
                    os.system(f'start powershell -NoExit -Command "cd \'{apps_folder}\'"')
                else:
                    os.startfile(app["Path"])  # Launch regular application
            except OSError as e:
                if e.winerror == 1223:
                    print(f"Operation cancelled by the user for {app['Path']}")
                else:
                    raise

def open_github(event):
    """Open the GitHub repository in the default web browser."""
    webbrowser.open_new("https://github.com/h0ek/SysPwn")

root = tk.Tk()
root.title("SysPwn")
root.geometry("300x450")
root.minsize(300, 300)

icon_path = resource_path("tools.ico")
root.iconbitmap(icon_path)

root.resizable(width=False, height=True)

search_var = tk.StringVar()
search_var.trace("w", lambda name, index, mode: update_list(search_var.get()))
search_entry = tk.Entry(root, textvariable=search_var, width=40)
search_entry.pack(pady=10)

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

columns = ("Group", "Application")
list_view = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=scrollbar_y.set)
list_view.heading("Group", text="Group")
list_view.heading("Application", text="Application")

list_view.column("Group", width=120)
list_view.column("Application", width=160)

list_view.pack(fill=tk.BOTH, expand=True)
scrollbar_y.config(command=list_view.yview)

list_view.bind("<Double-1>", launch_app)

github_label = tk.Label(root, text="Source", fg="blue", cursor="hand2", anchor="w")
github_label.pack(pady=10, anchor="w", side="left", padx=10)
github_label.bind("<Button-1>", open_github)

update_list("")
root.mainloop()
