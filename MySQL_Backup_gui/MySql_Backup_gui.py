# [START OF SCRIPT_MySQL_Backup_GUI_backup]
# Script created on 2024-07-01 17:30 UTC+3
# SCRIPT DETAILS: MySQL_Backup_GUI_backup_20240701_1730.py

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import datetime
import shutil
#pip install -v mysql-connector-python
import mysql.connector  # Import mysql.connector for MySQL operations

class MySQL_Backup_GUI:
    """GUI for performing MySQL backup and handling files using ttk widgets."""

    def __init__(self, root):
        """
        Initializes the MySQL_Backup_GUI class, setting up the user interface elements.
        
        Args:
            root (tk.Tk): The main tkinter root window.
        """
        self.root = root
        self.root.title("Boilerplate MySQL Backup GUI")

        # Set default directory to current working directory
        self.default_dir = os.getcwd()
        
        # Create and configure styles for the scrollbars
        self.style = ttk.Style()
        self.style.configure("Vertical.TScrollbar", gripcount=0, 
                             background="lightblue", troughcolor="lightgray", 
                             arrowcolor="blue", width=20)  # Customize vertical scrollbar
        self.style.configure("Horizontal.TScrollbar", gripcount=0, 
                             background="lightblue", troughcolor="lightgray", 
                             arrowcolor="blue", height=20)  # Customize horizontal scrollbar

        # Create a canvas for scrolling with vertical and horizontal scrollbars
        self.canvas = tk.Canvas(self.root)
        self.v_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview, style="Vertical.TScrollbar")
        self.h_scrollbar = ttk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview, style="Horizontal.TScrollbar")
        
        # Pack scrollbars on right (vertical) and bottom (horizontal)
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a frame inside the canvas
        self.frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # Bind the frame's resizing to update the scroll region
        self.frame.bind("<Configure>", self.on_frame_configure)

        # Create and configure the GUI elements
        self.create_widgets()

    def on_frame_configure(self, event):
        """Adjust scroll region to the size of the frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_widgets(self):
        """Creates and arranges the widgets in the GUI."""
        # MySQL credentials inputs with default user 'root'
        ttk.Label(self.frame, text="MySQL User:").grid(row=0, column=0, padx=5, pady=5)
        self.mysql_user = ttk.Entry(self.frame)
        self.mysql_user.insert(0, "root")  # Default MySQL username
        self.mysql_user.grid(row=0, column=1, padx=5, pady=5)

        # FocusIn event to clear default 'root' text when the user clicks the entry
        self.mysql_user.bind("<FocusIn>", lambda e: self.mysql_user.delete(0, 'end'))

        ttk.Label(self.frame, text="MySQL Password:").grid(row=1, column=0, padx=5, pady=5)
        self.mysql_pass = ttk.Entry(self.frame, show="*")
        self.mysql_pass.grid(row=1, column=1, padx=5, pady=5)

        # Test Connection button
        self.test_button = ttk.Button(self.frame, text="Test Connection", command=self.test_connection)
        self.test_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Directory selection for backup
        self.backup_dir_button = ttk.Button(self.frame, text="Select Backup Directory", command=self.select_backup_directory)
        self.backup_dir_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Perform Backup button
        self.backup_button = ttk.Button(self.frame, text="Perform Backup", command=self.perform_backup)
        self.backup_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

        # Scheduled Task checkbox
        self.schedule_task_var = tk.BooleanVar()
        self.schedule_task_checkbox = ttk.Checkbutton(self.frame, text="Schedule Backup", variable=self.schedule_task_var, command=self.toggle_schedule_options)
        self.schedule_task_checkbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Scheduling options (hidden until checkbox is checked)
        self.schedule_options = ttk.Frame(self.frame)
        self.schedule_options.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        self.schedule_options.grid_remove()  # Initially hidden

        ttk.Label(self.schedule_options, text="Frequency:").grid(row=0, column=0, padx=5, pady=5)
        self.main_option = ttk.Combobox(self.schedule_options, values=["Hourly", "Daily", "Weekly"])
        self.main_option.grid(row=0, column=1, padx=5, pady=5)
        self.main_option.bind("<<ComboboxSelected>>", self.update_time_options)

        self.time_label = ttk.Label(self.schedule_options, text="Time:")
        self.time_label.grid(row=1, column=0, padx=5, pady=5)
        self.time_entry = ttk.Entry(self.schedule_options)
        self.time_entry.grid(row=1, column=1, padx=5, pady=5)

        # Console output for logging
        self.console_output = tk.Text(self.frame, height=10, wrap="word")
        self.console_output.grid(row=7, column=0, columnspan=2, padx=5, pady=10)

    def test_connection(self):
        """Tests the MySQL connection with the provided credentials."""
        mysql_user = self.mysql_user.get()
        mysql_pass = self.mysql_pass.get()

        try:
            # Establish the MySQL connection
            connection = mysql.connector.connect(user=mysql_user, password=mysql_pass)
            connection.close()  # Close the connection if successful
            self.console_output.insert(tk.END, "Connection successful!\n")
        except mysql.connector.Error as err:
            self.console_output.insert(tk.END, f"Connection failed: {err}\n")

    def toggle_schedule_options(self):
        """Show or hide the scheduling options based on the checkbox."""
        if self.schedule_task_var.get():
            self.schedule_options.grid()
        else:
            self.schedule_options.grid_remove()

    def update_time_options(self, event):
        """Update time selection input based on the selected frequency."""
        selected_option = self.main_option.get()
        if selected_option == "Hourly":
            self.time_label.config(text="Time (in minutes):")
        elif selected_option == "Daily":
            self.time_label.config(text="Time (HH:MM 24hr):")
        elif selected_option == "Weekly":
            self.time_label.config(text="Day and Time (e.g., Mon 14:00):")
    
    def select_backup_directory(self):
        """Opens a dialog to select a directory for backup."""
        backup_dir = filedialog.askdirectory(title="Select Backup Directory", initialdir=self.default_dir)
        if backup_dir:
            self.backup_dir = backup_dir
            self.console_output.insert(tk.END, f"Selected backup directory: {backup_dir}\n")
        else:
            self.console_output.insert(tk.END, "No directory selected.\n")

    def perform_backup(self):
        """Performs MySQL database backup."""
        mysql_user = self.mysql_user.get()
        mysql_pass = self.mysql_pass.get()

        if not hasattr(self, 'backup_dir'):
            messagebox.showwarning("Backup Error", "Please select a backup directory.")
            return
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(self.backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_folder, exist_ok=True)
        
        self.console_output.insert(tk.END, f"Creating backup folder: {backup_folder}\n")
        
        # MySQL Dump command
        dump_command = f'mysqldump -u{mysql_user} -p{mysql_pass} --all-databases > {backup_folder}/backup.sql'
        
        try:
            subprocess.run(dump_command, shell=True, check=True)
            self.console_output.insert(tk.END, "Backup completed successfully.\n")
        except subprocess.CalledProcessError as e:
            self.console_output.insert(tk.END, f"Backup failed: {e}\n")

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = MySQL_Backup_GUI(root)
    root.mainloop()

# [END OF SCRIPT_MySQL_Backup_GUI_backup]
