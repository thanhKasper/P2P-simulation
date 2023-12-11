import socket
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from clientImplement import Client

# print(socket.gethostbyname(socket.gethostname()))

client = Client("115.73.173.12", 65432)


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
    client.start_connection()
    if client.is_connected:
        notebook.pack(fill="both", expand=True)


hostname_submit = Button(topFrame, text="Connect", command=handle_submit)
hostname_submit.grid(column=2, row=0)

# Second frame for displaying the h1
heading = Label(window, text="What do you want to do?")
heading.configure(font=("Ariel", 32))
heading.pack()

# Display the main section of the program only if user connect to server
notebook = ttk.Notebook(window)
# List of tabs
addFile = ttk.Frame(notebook)
removeFile = ttk.Frame(notebook)
updatePath = ttk.Frame(notebook)
downloadFile = ttk.Frame(notebook)

notebook.add(addFile, text="Add")
notebook.add(removeFile, text="Remove")
notebook.add(updatePath, text="Update")
notebook.add(downloadFile, text="Download")

def handle_tab_change(event):
    # user_data = client.handle_request("GET_INFO")
    # user_data = user_data[0]['file_info']

    if notebook.select() == ".!notebook.!frame":
        print("Add Tab")
    elif notebook.select() == ".!notebook.!frame2":
        # GET_INFO return data format
        # [
        #   {
        #     'client_name': 'Thanh',
        #     'IP': '192.168.56.1',
        #     'port': 51045,
        #     'file_info': [{'file_name': 'DBSchool1.sql', 'path': 'D:'}, {'file_name': 'ocean.png', 'path': 'D:'}]
        #   }
        # ]
        user_data = client.handle_request("GET_INFO")
        user_data = user_data[0]['file_info']
        children_list = remove_tree.get_children()
        for child in children_list:
            remove_tree.delete(child)
        for info in user_data:
            remove_tree.insert("", "end", values=(info["file_name"], info["path"]))
    elif notebook.select() == ".!notebook.!frame3":
        user_data = client.handle_request("GET_INFO")
        user_data = user_data[0]['file_info']
        children_list = update_tree.get_children()
        for child in children_list:
            update_tree.delete(child)
        for info in user_data:
            update_tree.insert("", "end", values=(info["file_name"], info["path"]))


notebook.bind("<<NotebookTabChanged>>", handle_tab_change)


#######################################
# Create a GUI for add file to server #
#######################################
def get_file():
    dialog = filedialog.askopenfile()
    split_idx = dialog.name.rfind('/')
    path_name = dialog.name[:split_idx]
    file_name = dialog.name[split_idx + 1:]
    command = "SEND " + path_name + " " + file_name
    client.handle_request(command)


addBtn = ttk.Button(addFile, text="Select file to add", command=get_file)
addBtn.pack(pady=20, padx=10)

label1 = ttk.Label(removeFile, text="File info")
label1.configure(font=('Ariel', 15))
label1.place(x=10, y=10)

##############################################
# Create a GUI to remove file from server    #
##############################################
label2 = ttk.Label(removeFile, text="Remove file")
label2.configure(font=('Ariel', 15))
label2.place(x=10, y=270)

remove_filename = ttk.Label(removeFile, text="Input file name:")
remove_filename.place(x=10, y=300)

remove_filename_text = ttk.Entry(removeFile, width=30)
remove_filename_text.place(x=100, y=300)


def handle_remove_file():
    file_name = remove_filename_text.get()
    client.handle_request(f"REMOVE {file_name}")
    user_data = client.handle_request("GET_INFO")
    user_data = user_data[0]['file_info']
    children_list = remove_tree.get_children()
    for child in children_list:
        remove_tree.delete(child)
    for info in user_data:
        remove_tree.insert("", "end", values=(info["file_name"], info["path"]))


removeBtn = ttk.Button(removeFile, text="Remove file", command=handle_remove_file)
removeBtn.place(x=300, y=300)

remove_tree = ttk.Treeview(removeFile, columns=("File name", "File path"), show="headings")
remove_tree.heading("File path", text="File path")
remove_tree.heading("File name", text="File name")
remove_tree.column("File path", width=250)
remove_tree.column("File name", width=200)
remove_tree.place(x=20, y=40)

###########################################
# Create a GUI for update path to server  #
###########################################
label1 = ttk.Label(updatePath, text="File info")
label1.configure(font=('Ariel', 15))
label1.place(x=10, y=10)

#
label2 = ttk.Label(updatePath, text="Update path file")
label2.configure(font=('Ariel', 15))
label2.place(x=10, y=270)

filename = ttk.Label(updatePath, text="Input file name:")
filename.place(x=10, y=300)

name_text = ttk.Entry(updatePath, width=30)
name_text.place(x=100, y=300)

new_path = ttk.Label(updatePath, text="Input new path:")
new_path.place(x=10, y=330)

path_text = ttk.Entry(updatePath, width=30)
path_text.place(x=100, y=330)


def handle_update_file():
    file_name = name_text.get()
    path_file = path_text.get()
    client.handle_request(f"UPDATE {path_file} {file_name}")
    user_data = client.handle_request("GET_INFO")
    user_data = user_data[0]['file_info']
    children_list = update_tree.get_children()
    for child in children_list:
        update_tree.delete(child)
    for info in user_data:
        update_tree.insert("", "end", values=(info["file_name"], info["path"]))


pathBtn = ttk.Button(updatePath, text="Update path", command=handle_update_file)
pathBtn.place(x=300, y=330)

update_tree = ttk.Treeview(updatePath, columns=("File name", "File path"), show="headings")
update_tree.heading("File path", text="File path")
update_tree.heading("File name", text="File name")
update_tree.column("File path", width=250)
update_tree.column("File name", width=200)
update_tree.place(x=20, y=40)

###################################
# Create a GUI for download file  #
###################################
entrylabel = ttk.Label(downloadFile, text="Input file name to fetch:")
entrylabel.place(x=10, y=10)

fetch_entry = ttk.Entry(downloadFile, width=30)
fetch_entry.place(x=150, y=10)


def handle_fetch_file():
    downloading_file = fetch_entry.get()
    response = client.handle_request(f"FETCH {downloading_file}")
    print(response)
    children_list = my_tree.get_children()
    for child in children_list:
        my_tree.delete(child)
    for choice in response:
        my_tree.insert("",
                       "end",
                       iid=str((choice['client_name'], choice['IP'], choice['path'] + '/' + downloading_file)),
                       values=[choice['client_name'], choice['IP'], choice['path'] + '/' + downloading_file])


fetchBtn = ttk.Button(downloadFile, text="Fetch file", command=handle_fetch_file)
fetchBtn.place(x=350, y=10)

my_tree = ttk.Treeview(downloadFile, columns=("Name", "IP", "File path"), show="headings")
my_tree.heading("Name", text="Name")
my_tree.heading("IP", text="IP")
my_tree.heading("File path", text="File path")
my_tree.column("Name", width=150)
my_tree.column("IP", width=100)
my_tree.column("File path", width=250)
my_tree.place(x=20, y=40)

user_choice = ()


def on_select(event):
    global user_choice
    selected_item = my_tree.focus()
    user_choice = eval(selected_item)


print("User choose this: ", user_choice)

my_tree.bind("<ButtonRelease-1>", on_select)


def download_file_from_client():
    print("User choose this client to download from", user_choice)
    ip_addr = user_choice[1]
    file_path = user_choice[2]
    client.create_connection_and_download(ip_addr, file_path)


downloadBtn = ttk.Button(downloadFile, text="Send request", width=20, command=download_file_from_client)
downloadBtn.place(x=450, y=280)

window.mainloop()
