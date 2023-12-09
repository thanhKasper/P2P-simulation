import tkinter as tk

# Function to switch to Frame 1
def show_frame1():
    frame1.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    label1.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
    button_frame1.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    frame2.place_forget()

# Function to switch to Frame 2
def show_frame2():
    frame2.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    label2.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
    label3.place(relx=0.1, rely=0.4, anchor=tk.CENTER)
    entry1.place(relx=0.6, rely=0.4, anchor=tk.CENTER)
    button_frame2.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

    frame1.place_forget()

# Create the main window
root = tk.Tk()
root.title("Frame Navigation Example")
root.minsize(width=600, height=500)

# Create Frame 1
frame1 = tk.Frame(root, width=600, height=600, bg="lightblue")
frame1.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Add widgets to Frame 1
label1 = tk.Label(frame1, text="Welcome to Server Deploying", bg="lightblue")
label1.config(font=("Ariel", 30))
label1.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

button_frame1 = tk.Button(frame1, text="Deploy Server", command=show_frame2, width=20, height=5)
button_frame1.config(font=("Ariel", 15))
button_frame1.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Create Frame 2
frame2 = tk.Frame(root, width=600, height=600)

# Add widgets to Frame 2
label2 = tk.Label(frame2, text="Server Deploying...")
label2.config(font=("Ariel", 15))

button_frame2 = tk.Button(frame2, text="Undeploy Server", command=show_frame1, width=20, height=3)

label3 = tk.Label(frame2, text="Input Command:")
label3.config(font=("Ariel", 10))

entry1 = tk.Entry(frame2, width=60)

# Set up initial visibility
show_frame1()

# Run the Tkinter event loop
root.mainloop()
