from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import tkinter.simpledialog as simpledialog
from PIL import Image, ImageTk
import json
import os

class TramStop:
    x_coord = -1
    y_coord = -1
    stop_name = ""

    def __str__(self):
        return f"({self.x_coord},{self.y_coord}) - {self.stop_name}"

filename = "data/data.json"

stops = []
if os.stat(filename).st_size != 0:
    with open(filename) as f:
        stops = json.load(f)




if __name__ == "__main__":
    root = Tk()

    #setting up a tkinter canvas with scrollbars
    frame = Frame(root, bd=2, relief=SUNKEN)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    xscroll = Scrollbar(frame, orient=HORIZONTAL)
    xscroll.grid(row=1, column=0, sticky=E+W)
    yscroll = Scrollbar(frame)
    yscroll.grid(row=0, column=1, sticky=N+S)
    canvas = Canvas(frame, bd=0, xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    xscroll.config(command=canvas.xview)
    yscroll.config(command=canvas.yview)
    frame.pack(fill=BOTH,expand=1)

    #adding the image
    ##File = askopenfilename(parent=root, initialdir="C:/",title='Choose an image.')
    File = "resources/linie_tramwajowe_half.png"
    img = ImageTk.PhotoImage(Image.open(File))
    canvas.create_image(0,0,image=img,anchor="nw")
    canvas.config(scrollregion=canvas.bbox(ALL))

    #function to be called when mouse is clicked

    def printcoords(event):
        #outputting x and y coords to console
        stop = TramStop()
        stop.x_coord = canvas.canvasx(event.x)
        stop.y_coord = canvas.canvasy(event.y)
        print("{} {}".format(canvas.canvasx(event.x), canvas.canvasy(event.y)))
        stop.stop_name = simpledialog.askstring("Input", "What is the stop's name?", parent=root)
        if any(d['stop_name'] == stop.stop_name for d in stops):
            if messagebox.askyesno("Stop already exist", "Do you want to update it?"):
                stops.append(stop.__dict__)
        else:
            stops.append(stop.__dict__)


        for element in stops:
            print(element)



    #mouseclick event
    canvas.bind("<Button 1>",printcoords)

    root.mainloop()

    with open(filename, 'w') as outfile:
        json.dump(stops, outfile)
