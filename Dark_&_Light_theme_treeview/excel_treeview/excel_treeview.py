import os
import sys
import tkinter as tk
from sys import *
from tkinter import *
import tkinter.font as tkf
from tkinter import filedialog, ttk
import numpy
import openpyxl
import pandas as pd


# add path as global
global path
path = "people.xlsx"
# [Start of Function To Load data from Excel]
def load_data():
    """
    Load data from an Excel file into the TreeView widget.
    """
    # Open the Excel file
    try:
        df = pd.read_excel(path)
    except FileNotFoundError:
        print("File not found.")
        return

    # Get column names dynamically
    cols = list(df.columns)

    # Set columns for the TreeView
    treeview["columns"] = cols
    for col in cols:
        treeview.heading(col, text=col)
        # Adjust column width to fit content
        treeview.column(col, minwidth=0, width=tkf.Font().measure(col))
		#treeview.column(col, minwidth=0, width=tkf.Font().measure(col))

    # Insert data into the TreeView
    for index, row in df.iterrows():
        treeview.insert("", tk.END, values=tuple(row))
# [End of Function To Load data from Excel]
# [Start of Function to switch mode/ theme between dark and light]
# Function to switch mode/ theme between dark and light
def toggle_mode():
    if mode_switch.instate(["selected"]):
        style.theme_use("forest-light")
    else:
        style.theme_use("forest-dark")
# [End of Function to switch mode/ theme between dark and light]
# [START OF CODEMY]

# [Start of Function to Clear_TreeView]
def clear_tree():
    """
    Clear all items in the TreeView widget.
    """
    #for item in treeview.get_children():
        #treeview.delete(item)


# [End of Function to Clear_TreeView]

# [Start of Function to Clear_TreeView]
def clear_tree():
    my_tree.delete(*my_tree.get_children())


# [End of Function to Clear_TreeView]


# [Start of Function to Open Files]
# Function to Open Files
def file_open():
    """
    Open a file dialog to select a file, load its data into a DataFrame,
    and display the data in the TreeView widget.
    """
    #global path
    #pass           #pass when function is empty
    filename=filedialog.askopenfilename(
        initialdir=os.getcwd(),
        #initialdir='D:/',
        title="Select a file to open ",
        filetype=(("xlsx files","*.xlsx"),("csv files","*.csv"))
        )
    if filename:
        try:
		 # Attempt to read the file as an Excel file and load its data into a DataFrame
            #df = pd.read_excel(filename)
            filename = r"{}".format(filename)
            df = pd.read_excel(filename)

            # Set the global path variable to the selected file
            path = filename

            # Clear any existing data in the TreeView widget
            clear_tree()

            # Load the data from the DataFrame into the TreeView widget
            load_data()

        except ValueError:
            # Handle error if the file cannot be opened
            label.config(text="File Could Not Be Opened, Please Try Again!")
        except FileNotFoundError:
            # Handle error if the file is not found
            label.config(text="File Could Not Be Found, Please Try Again!")

            
# Clear Old TreeView
    clear_tree()       


# Setup new TreeView 
    my_tree["column"] = list(df.columns)
    my_tree["show"] = "headings"

    #loop thru column  list
    
    for column in my_tree["column"]:
        my_tree.heading(column, text=column)
    
    # put data in treeview
    df_rows = df.to_numpy().tolist()
    for row in df_rows:
        my_tree.insert("", "end", values=row)
    my_tree.pack()
    
 #[End of Function to Open Files]


# [END OF CODEMY]

#  main loop
root = tk.Tk()

root.title('Excel SpreadSheet or Sqlite to TreeView')
#root.geometry('700x500')
style = ttk.Style(root)
root.tk.call("source", "forest-light.tcl")
root.tk.call("source", "forest-dark.tcl")
style.theme_use("forest-dark")

my_tree = ttk.Treeview()

#Create Frame
frame = ttk.Frame(root)
frame.pack()
# [START OF CODEMY]
#ADD MENU
my_menu = Menu(root)
root.config(menu=my_menu)

# ADD MENU DROPDOWN
file_menu = Menu(my_menu)
file_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label='SpreadSheets', menu=file_menu)
file_menu.add_command(label='Open', command=file_open)

# [END OF CODEMY] line 202


# Insert widgets_frame
widgets_frame = ttk.LabelFrame(frame, text="Insert Row")
widgets_frame.grid(row=1, column=0, padx=20, pady=10)


# Insert rows inside the widgets_frame ttk.Entry(parent_object) 
# in this case widgets_frame is parent for name_entry row

name_entry = ttk.Entry(widgets_frame)
name_entry.insert(0, "Name")
#Clear text when clicked
name_entry.bind("<FocusIn>", lambda e: name_entry.delete('0', 'end'))

name_entry.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")

# Insert Switch button widget

mode_switch = ttk.Checkbutton(
    widgets_frame, text="Mode", style="Switch", command=toggle_mode)
mode_switch.grid(row=5, column=0, padx=5, pady=10, sticky="nsew")

# Insert label widget inside widgets_frame
#label = ttk.Label(widgets_frame, text="Hello GPTGO!")
#label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

# Insert label outside widgets_frame [in root]

label = ttk.Label(root, text="Hello GPTGO!")
label.pack()


# Create tkinter treeview to display excel data modify to work with:
treeFrame = ttk.Frame(frame)
treeFrame.grid(row=0, column=1, pady=10)
treeScroll = ttk.Scrollbar(treeFrame)
treeScroll.pack(side="right", fill="y")
# [START OF CODEMY]


# [END OF CODEMY]

# cols = ("Name", "Age", "Subscription", "Employment")
# treeview = ttk.Treeview(treeFrame, show="headings",
#                         yscrollcommand=treeScroll.set,
#                         columns=cols, #height=
#                         ) 

# Define columns for the TreeView dynamically
treeview = ttk.Treeview(
    treeFrame, show="headings", yscrollcommand=treeScroll.set, height=13
)
treeview.pack(fill="both", expand=True)
treeScroll.config(command=treeview.yview)

#treeview.pack()

# treeScroll.config(command=treeview.yview)
# load_data()




# In[ ]:


# Execute Main Loop
root.mainloop()
