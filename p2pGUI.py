from client import ClientController
from tkinter import *
from tkinter import ttk
from tkinter import filedialog


client = ClientController("192.168.56.1", 23578)

window = Tk()
window.title("P2P Simulation")
window.minsize(width=600, height=500)

topFrame = Frame(window)
topFrame.pack()

label = Label(topFrame, text="Enter your hostname")
label.grid(column=0, row=0)

hostname_input = Entry(topFrame)
hostname_input.grid(column=1, row=0)


def handle_submit():
    content = hostname_input.get()
    client.username = content
    # client.connect_to_server()
    # if client.is_connected:
    notebook.pack(fill="both", expand=True)


hostname_submit = Button(topFrame, text="Connect", command=handle_submit)
hostname_submit.grid(column=2, row=0)

# Second frame for displaying the h1
heading = Label(window, text="What do you want to do?")
heading.configure(font=("Ariel", 32))
heading.pack()

# Display the main section of the program only if user connect to server
notebook = ttk.Notebook(window)
# notebook.pack()
addFile = ttk.Frame(notebook)
removeFile = ttk.Frame(notebook)
updatePath = ttk.Frame(notebook)
downloadFile = ttk.Frame(notebook)
notebook.add(addFile, text="Add")
notebook.add(removeFile, text="Remove")
notebook.add(updatePath, text="Update")
notebook.add(downloadFile, text="Download")


# Create a GUI for add file to server
def get_file():
    dialog = filedialog.askopenfile()
    print(dialog.name)
    file_path = dialog.name.rfind('/')


addBtn = ttk.Button(addFile, text="Add File", command=get_file)
addBtn.pack()

window.mainloop()

