import tkinter # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3
window = tkinter.Tk()
window.title("printwindow")
window.geometry("300x300")
window.configure(background="#a1dbcd")

lblInst = tkinter.Label(window, text="Please login to continue:", fg="#383a39", bg="#a1dbcd", font=("Helvetica", 16))
lblInst.pack()

#create the widgets for entering a username
lblUsername = tkinter.Label(window, text="Username:", fg="#383a39", bg="#a1dbcd")
entUsername = tkinter.Entry(window)
#and pack them into the window
lblUsername.pack(side=tkinter.LEFT)
entUsername.pack(side=tkinter.LEFT)

#create the widgets for entering a username
lblPassword = tkinter.Label(window, text="Password:", fg="#383a39", bg="#a1dbcd")
entPassword = tkinter.Entry(window)
#and pack them into to the window
lblPassword.pack()
entPassword.pack(side=tkinter.LEFT)

#create a button widget called btn
btn = tkinter.Button(window, text="Login", fg="#a1dbcd", bg="#383a39")
#pack the widget into the window
btn.pack(side=tkinter.LEFT)
window.mainloop()
