
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import re
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

#[SCRIPT_CREATED ON 2024-04-05 10:00 UTC+3]
# SCRIPT_DETAILS: UnusedAssetsManager_202405051000.py
# This script finds unused asset files in a project and moves them to a timestamped backup location while generating restore scripts.

class UnusedAssetsManager:
    """Manages the identification and movement of unused asset files in a project."""

    def __init__(self, root):
        """
        Initializes the main class, setting up the user interface (UI) elements.
        
        Args:
            root (tk.Tk): The main tkinter root window.
        """
        self.root = root
        self.root.title("Unused Assets Manager_V13")

        # Initialize variables
        self.project_path = ""  # Variable to store project directory
        self.backup_path = ""  # Variable to store backup directory
        self.used_files = set()  # Set to hold the list of used assets
        self.unused_files = set()  # Set to hold unused assets
        self.all_extensions = set()  # Set of all unique file extensions in the project
        self.asset_extensions = set()  # Set of user-selected extensions to check for assets
        self.is_running = False  # Flag to control running status

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
        # Create a vertical scrollbar tied to root and linked to the canvas
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

        # Percentage Label for Progress
        self.progress_percentage_label = ttk.Label(self.frame, text="0%")
        self.progress_percentage_label.pack(pady=5)  # Add percentage label below the progress bar

    def on_frame_configure(self, event):
        """Updates the scroll region of the canvas when the frame is resized."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_widgets(self):
        """
        Creates and layouts the user interface (UI) elements using ttk widgets.
        """
        # Project Directory Frame
        project_frame = ttk.Frame(self.frame)
        project_frame.pack(pady=10)
        ttk.Label(project_frame, text="Select Project Directory:").pack(pady=5)
        self.project_entry = ttk.Entry(project_frame, width=50)
        self.project_entry.pack(pady=5)
        ttk.Button(project_frame, text="Browse", command=self.browse_project).pack(pady=5)

        # Backup Directory Frame
        backup_frame = ttk.Frame(self.frame)
        backup_frame.pack(pady=10)
        ttk.Label(backup_frame, text="Select Backup Directory:").pack(pady=5)
        self.backup_entry = ttk.Entry(backup_frame, width=50)
        self.backup_entry.pack(pady=5)
        ttk.Button(backup_frame, text="Browse", command=self.browse_backup).pack(pady=5)

        # Extension Frame
        self.extension_frame = ttk.Frame(self.frame)
        self.extension_frame.pack(pady=10)
        ttk.Label(self.extension_frame, text="Select Asset Extensions:").pack(pady=5)

        # Scrollable listbox with a vertical scrollbar (styled tk.Listbox)
        self.extension_listbox = tk.Listbox(self.extension_frame, selectmode=tk.MULTIPLE, width=50, height=10)
        self.extension_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = ttk.Scrollbar(self.extension_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.extension_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.extension_listbox.yview)

        # Button Frame
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Select All", command=self.select_all_extensions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Find Extensions", command=self.find_extensions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Find Unused Assets", command=self.start_find_unused_assets_thread).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Move Selected Files", command=self.move_selected_files).pack(side=tk.LEFT, padx=5)

        # Progress Bar
        self.progress = ttk.Progressbar(self.frame, length=400, mode='determinate')
        self.progress.pack(pady=10)

        # Output Text Frame
        self.output_text = scrolledtext.ScrolledText(self.frame, width=100, height=20, wrap=tk.NONE)
        self.output_text.pack(pady=10)

    def select_all_extensions(self):
        """
        Selects or deselects all extensions in the listbox.
        """
        if self.extension_listbox.size() == 0:
            return
        
        # Toggle selection based on current state
        if self.extension_listbox.curselection():
            self.extension_listbox.selection_clear(0, tk.END)  # Deselect all if any are selected
        else:
            self.extension_listbox.selection_set(0, tk.END)  # Select all if none are selected

    def browse_project(self):
        """
        Opens a file dialog for selecting the project directory.
        Updates the project path in the entry field.
        """
        self.project_path = filedialog.askdirectory(title="Select Project Directory", initialdir=os.getcwd())
        self.project_entry.delete(0, tk.END)
        self.project_entry.insert(0, self.project_path)

    def browse_backup(self):
        """
        Opens a file dialog for selecting the backup directory.
        Updates the backup path in the entry field.
        """
        # Set initialdir to project_path, if it is set; otherwise, fallback to current working directory
        initial_directory = self.project_path if hasattr(self, 'project_path') and self.project_path else os.getcwd()
        
        self.backup_path = filedialog.askdirectory(title="Select Backup Directory", initialdir=initial_directory)
        self.backup_entry.delete(0, tk.END)
        self.backup_entry.insert(0, self.backup_path)    
        

    def find_extensions(self):
        """
        Scans the project directory for all file extensions and displays them in a selectable listbox.
        """
        if not self.project_path:
            messagebox.showerror("Error", "Please select the project directory first.")
            return

        self.all_extensions.clear()  # Reset the set of extensions
        self.extension_listbox.delete(0, tk.END)  # Clear the listbox

        # Walk through the project and collect file extensions
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                _, extension = os.path.splitext(file)
                if extension:  # Only add non-empty extensions
                    self.all_extensions.add(extension)

        # Populate the listbox with found extensions
        for ext in sorted(self.all_extensions):
            self.extension_listbox.insert(tk.END, ext)

    def start_find_unused_assets_thread(self):
        """
        Starts the unused assets search in a separate thread.
        """
        if self.is_running:
            messagebox.showwarning("Warning", "The search is already running.")
            return
        
        self.is_running = True
        self.progress.start()  # Start the progress bar animation
        self.output_text.delete(1.0, tk.END)  # Clear output text
        self.thread = threading.Thread(target=self.find_unused_assets)
        self.thread.start()  # Start the thread

    def find_unused_assets(self):
        """
        Identifies unused assets by comparing files in the project directory with those referenced in project files.
        The user-selected extensions are considered for the asset search.
        """
        if not self.project_path or not self.backup_path:
            messagebox.showerror("Error", "Please select both project and backup directories.")
            self.is_running = False
            self.progress.stop()  # Stop the progress bar
            return

        selected_indices = self.extension_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select at least one asset extension.")
            self.is_running = False
            self.progress.stop()  # Stop the progress bar
            return
        
        self.asset_extensions = {self.extension_listbox.get(i) for i in selected_indices}  # Set of selected extensions
        self.unused_files.clear()  # Clear previous unused files

        # Find all asset files with the selected extensions
        all_files = []
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in self.asset_extensions:
                    all_files.append(os.path.join(root, file))

        total_files = len(all_files)  # Count total files found
        self.output_text.insert(tk.END, f"Total files found: {total_files}\n")  # Display total files found

        # Identify used files by running search_refs_in_php in parallel
        self.search_refs_in_php_parallel(all_files)

        # Identify unused files
        for file in all_files:
            if file not in self.used_files:
                self.unused_files.add(file)

        # Display results in the output text area
        self.output_text.insert(tk.END, "Unused Files Found:\n\n")
        for i, file in enumerate(sorted(self.unused_files)):
            self.output_text.insert(tk.END, f"{i + 1}. {file}\n")

        # Notify completion and stop the progress bar
        self.is_running = False
        self.progress.stop()
        messagebox.showinfo("Success", f"Identified {len(self.unused_files)} unused files.")

    def search_refs_in_php_parallel(self, all_files):
        """
        Uses a thread pool to search for references to asset files within PHP files concurrently.

        Args:
            all_files (list): List of all asset files to check for references.
        """
        total_php_files = sum(len(files) for _, _, files in os.walk(self.project_path) if any(file.endswith(".php") for file in files))
        php_files = []

        # Gather all PHP files in the project directory
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".php"):
                    php_files.append(os.path.join(root, file))

        # Define a worker function to search for references in each PHP file
        def worker(php_file_path):
            try:
                with open(php_file_path, "r", encoding="utf-8", errors="ignore") as php_file:
                    php_content = php_file.read()
                    for asset_file in all_files:
                        if re.search(r'\b' + re.escape(os.path.basename(asset_file)) + r'\b', php_content):
                            self.used_files.add(asset_file)  # Add the asset to used files

                    # Update progress for each processed PHP file
                    with threading.Lock():  # Ensure thread-safe access to GUI components
                        processed_php_files = len(self.used_files)  # Update processed file count
                        remaining_php_files = total_php_files - processed_php_files  # Calculate remaining PHP files
                        remaining_percentage = (processed_php_files / total_php_files) * 100 if total_php_files > 0 else 0  # Calculate percentage
                        self.progress["value"] = processed_php_files
                        self.progress_percentage_label.config(text=f"{int(remaining_percentage)}%")  # Update percentage label
                        # Display the processing status with total files
                        self.output_text.insert(tk.END, f"Processing {processed_php_files} of {total_php_files}: {os.path.basename(php_file_path)} Remaining {remaining_php_files} {int(remaining_percentage)}%\n")
                        self.output_text.see(tk.END)  # Scroll to the end of the text area
                        self.root.update()  # Update the GUI

            except Exception as e:
                print(f"Error reading file {php_file_path}: {repr(e)}")  # Error handling for file read

        # Use ThreadPoolExecutor to run the worker function on each PHP file
        with ThreadPoolExecutor() as executor:
            executor.map(worker, php_files)
    def create_backup_directory(self):
        """
        Creates a timestamped backup directory for storing unused asset files named as the project folder. 
        
        Returns:
            str: The path to the created backup directory.
        """
        # Get the current timestamp for the backup directory name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
        # Check if self.backup_path is set; otherwise, raise an error
        if not hasattr(self, 'backup_path') or not self.backup_path:
            raise ValueError("Backup path is not set. Please select a backup directory.")
    
        # Extract the last part of the project path (the folder name)
        folder_name = os.path.basename(self.project_path) if hasattr(self, 'project_path') else 'backup'
    
        # Create the backup directory path using the backup path and folder name
        backup_dir = os.path.join(self.backup_path, f"{folder_name}_unused_assets_backup_{timestamp}")
    
        # Create the backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True) 
    
        return backup_dir
    
    


    def move_selected_files(self):
        """
        Moves the identified unused files to a timestamped backup folder while preserving the original directory structure.
        Creates restore scripts in Python, PowerShell, and Batch format inside the backup folder.
        """
        if not self.unused_files:
            messagebox.showinfo("Info", "No unused files to move.")
            return

        # Create a timestamped backup directory
        timestamped_backup_dir = self.create_backup_directory()

        # Create a restore scripts directory
        restore_scripts_dir = os.path.join(timestamped_backup_dir, "restore_scripts")
        os.makedirs(restore_scripts_dir, exist_ok=True)

        # Move unused files and preserve directory structure
        for file in self.unused_files:
            relative_path = os.path.relpath(file, self.project_path)  # Get the relative path of the unused file
            backup_file_path = os.path.join(timestamped_backup_dir, relative_path)
            backup_file_dir = os.path.dirname(backup_file_path)
            os.makedirs(backup_file_dir, exist_ok=True)  # Create directories if they don't exist
            shutil.move(file, backup_file_path)  # Move the file to the backup location

        # Generate restore scripts
        self.generate_restore_scripts(restore_scripts_dir, timestamped_backup_dir)

        # Display a success message
        messagebox.showinfo("Success", f"Moved {len(self.unused_files)} unused files to {timestamped_backup_dir}")

    def generate_restore_scripts(self, restore_scripts_dir, backup_dir):
        """
        Generates restore scripts in Python, PowerShell, and Batch format to restore the moved files.

        Args:
            restore_scripts_dir (str): The directory to save restore scripts.
            backup_dir (str): The directory from which to restore files.
        """
        # Python restore script
        python_script = os.path.join(restore_scripts_dir, "restore_files.py")
        with open(python_script, "w") as f:
            f.write("# Restore script generated to restore unused assets\n")
            f.write(f"import shutil\nimport os\n\n")
            f.write(f"backup_dir = r'{backup_dir}'\n")
            f.write(f"original_project_dir = r'{self.project_path}'\n\n")
            f.write("for root, dirs, files in os.walk(backup_dir):\n")
            f.write("    for file in files:\n")
            f.write("        backup_file = os.path.join(root, file)\n")
            f.write("        relative_path = os.path.relpath(backup_file, backup_dir)\n")
            f.write("        original_file_path = os.path.join(original_project_dir, relative_path)\n")
            f.write("        shutil.move(backup_file, original_file_path)\n")
            f.write("print('Files restored successfully!')\n")

        # PowerShell restore script
        powershell_script = os.path.join(restore_scripts_dir, "restore_files.ps1")
        with open(powershell_script, "w") as f:
            f.write("# Restore script generated to restore unused assets\n")
            f.write(f"$backup_dir = '{backup_dir}'\n")
            f.write(f"$original_project_dir = '{self.project_path}'\n\n")
            f.write("Get-ChildItem -Path $backup_dir -Recurse | ForEach-Object {\n")
            f.write("    $relativePath = $_.FullName.Substring($backup_dir.Length + 1)\n")
            f.write("    $originalPath = Join-Path -Path $original_project_dir -ChildPath $relativePath\n")
            f.write("    Move-Item -Path $_.FullName -Destination $originalPath\n")
            f.write("}\n")
            f.write("Write-Host 'Files restored successfully!'\n")

        # Batch restore script
        batch_script = os.path.join(restore_scripts_dir, "restore_files.bat")
        with open(batch_script, "w") as f:
            f.write("@echo off\n")
            f.write(f"set backup_dir={backup_dir}\n")
            f.write(f"set original_project_dir={self.project_path}\n\n")
            f.write("for /r \"%backup_dir%\" %%F in (*) do (\n")
            f.write("    setlocal enabledelayedexpansion\n")
            f.write("    set relative_path=%%~pnxF\n")
            f.write("    set relative_path=!relative_path:%backup_dir%=!\n")
            f.write("    move \"%%F\" \"%original_project_dir%!relative_path!\"\n")
            f.write("    endlocal\n")
            f.write(")\n")
            f.write("echo Files restored successfully!\n")

        messagebox.showinfo("Success", "Restore scripts created successfully!")
# Entry point for the script
# Main application execution
if __name__ == "__main__":
    root = tk.Tk()
    app = UnusedAssetsManager(root)
    root.mainloop()

#[END of script with missing functionality
# [END OF SCRIPT UnusedAssetsManager.py]
