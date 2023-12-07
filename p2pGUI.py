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

addBtn = ttk.Button(addFile, text="Select file to add", command=get_file)
addBtn.pack(pady=20, padx=10)

# Create a GUI for remove file from server
label1 = ttk.Label(removeFile, text="File info")
label1.configure(font=('Ariel', 15))
label1.place(x=10, y=10)

###$
label2 = ttk.Label(removeFile, text="Remove file")
label2.configure(font=('Ariel', 15))
label2.place(x=10, y=270)


remove_filename = ttk.Label(removeFile, text="Input file name:")
remove_filename.place(x=10, y=300)

remove_filename_text = ttk.Entry(removeFile, width = 30)
remove_filename_text.place(x=100, y=300)


removeBtn = ttk.Button(removeFile, text="Remove file")
removeBtn.place(x=300, y=300)


remove_tree = ttk.Treeview(removeFile, columns=("File path", "File name"), show="headings")
remove_tree.heading("File path", text="File path")
remove_tree.heading("File name", text="File name")
remove_tree.column("File path",width=350)
remove_tree.column("File name",width=100)
remove_tree.place(x=20, y=40)

data=[('D:/','movie.mp4'),
      ('D:/','movie.mp4'),
      ('D:/','movie.mp4')]
for item in data:
    remove_tree.insert("","end", values=item)



# Create a GUI for updaet path to server
label1 = ttk.Label(updatePath, text="File info")
label1.configure(font=('Ariel', 15))
label1.place(x=10, y=10)

###$
label2 = ttk.Label(updatePath, text="Update path file")
label2.configure(font=('Ariel', 15))
label2.place(x=10, y=270)


filename = ttk.Label(updatePath, text="Input file name:")
filename.place(x=10, y=300)

name_text = ttk.Entry(updatePath, width = 30)
name_text.place(x=100, y=300)

newpath = ttk.Label(updatePath, text="Input new path:")
newpath.place(x=10, y=330)

path_text = ttk.Entry(updatePath, width = 30)
path_text.place(x=100, y=330)


pathBtn = ttk.Button(updatePath, text="Update path")
pathBtn.place(x=300, y=330)


update_tree = ttk.Treeview(updatePath, columns=("File path", "File name"), show="headings")
update_tree.heading("File path", text="File path")
update_tree.heading("File name", text="File name")
update_tree.column("File path",width=350)
update_tree.column("File name",width=100)
update_tree.place(x=20, y=40)

data=[('D:/','movie.mp4'),
      ('D:/','movie.mp4'),
      ('D:/','movie.mp4')]
for item in data:
    update_tree.insert("","end", values=item)


# Create a GUI for download file
entrylabel = ttk.Label(downloadFile, text="Input file name to fetch:")
entrylabel.place(x=10, y=10)

fetch_entry = ttk.Entry(downloadFile, width=30)
fetch_entry.place(x=150, y=10)

fetchBtn = ttk.Button(downloadFile, text="Fetch file")
fetchBtn.place(x=350, y=10)

my_tree = ttk.Treeview(downloadFile, columns=("Name", "IP", "Port", "File path"), show="headings")
my_tree.heading("Name", text="Name")
my_tree.heading("IP", text="IP")
my_tree.heading("Port", text="Port")
my_tree.heading("File path", text="File path")
my_tree.column("Name",width=150)
my_tree.column("IP",width=100)
my_tree.column("Port",width=50)
my_tree.column("File path",width=250)
my_tree.place(x=20, y=40)

data=[("Nguyen", '192.158.1.1', 53, 'D:/movie.mp4'),
      ("Minh", '192.158.1.2', 54, 'D:/movie.mp4'),
      ("Thanh", '192.158.1.3', 55, 'D:/movie.mp4')]
for item in data:
    my_tree.insert("","end", values=item)

def on_select(event):
    selected_item = my_tree.focus()
    print("Selected item:", selected_item)

my_tree.bind("<ButtonRelease-1>", on_select)

downloadBtn = ttk.Button(downloadFile, text="Send request", width=20)
downloadBtn.place(x=450, y=280)

window.mainloop()

