from tkinter import Tk, Label, Frame,SUNKEN,Scrollbar,HORIZONTAL,Canvas,N,S,E,W,BOTH,ALL,simpledialog
from PIL import Image, ImageTk
import json
import numpy as np

STOP_COLOR = 'red'
STOP_RADIUS = 7
TRAM_COLOR = 'yellow'
TRAM_RADIUS = 7

class Tram:
    def __init__(self,canvas,route,times):
        self.stop_count = 0
        self.route = route
        self.times = times
        self.direction = np.subtract(route[self.stop_count + 1], route[self.stop_count])
        self.time = self.times[self.stop_count]
        self.counter =0
        self.canvas = canvas
        self.moving =True
        x, y = route[0]
        self.body = self.canvas.create_oval(int(x), int(y), int(x + 2*TRAM_RADIUS),int(y + 2*TRAM_RADIUS),fill=TRAM_COLOR)
    def move(self):
        if self.moving:
            x,y = np.divide(self.direction,self.time)
            self.canvas.move(self.body,x,y)
            self.counter +=1
            if self.counter == self.time:
                self.counter=0
                self.stop_count +=1
                if self.stop_count+1 < len(self.route):
                    self.direction = np.subtract(self.route[self.stop_count + 1], self.route[self.stop_count])
                    self.time = self.times[self.stop_count]
                else:
                    self.moving = False

class MyFirstGUI:
    def __init__(self, master,filename,json_file):
        with open(json_file) as f:
            self.data = json.load(f)

         ####jakieś pierdolenie z ustawianiem (i luuuuuuuuv copy-paste programming)

        self.master = master
        master.title("Symulacja krakowskich lini tramwajowych")
        self.label = Label(master, text="Mapa")
        self.label.pack()
        self.frame = Frame(root, bd=2, relief=SUNKEN)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.xscroll = Scrollbar(self.frame, orient=HORIZONTAL)
        self.xscroll.grid(row=1, column=0, sticky=E+W)
        self.yscroll = Scrollbar(self.frame)
        self.yscroll.grid(row=0, column=1, sticky=N+S)
        self.canvas = Canvas(self.frame, bd=0,width=1326,height=400, xscrollcommand=self.xscroll.set, yscrollcommand=self.yscroll.set)
        self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Left>", lambda event: self.canvas.xview_scroll(-1, "units"))
        self.canvas.bind("<Right>", lambda event: self.canvas.xview_scroll(1, "units"))
        self.canvas.focus_set()
        self.canvas.bind("<1>", lambda event: self.canvas.focus_set())
        self.xscroll.config(command=self.canvas.xview)
        self.yscroll.config(command=self.canvas.yview)
        self.frame.pack(fill=BOTH,expand=1)
        self.img = ImageTk.PhotoImage(Image.open(filename))
        self.canvas.create_image(0, 0, image=self.img, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))


        ##mój kod (done step by step)

        self.create_stops()

        route1 = [
            "Krowodrza Górka",
            "Bratysławska",
            "Szpital Narutowicza",
            "Dworzec Towarowy",
            "Politechnika",
            "Dworzec Główny Tunel",
            "Rondo Mogilskie",
            "Rondo Grzegórzeckie",
            "Zabłocie",
            "Klimeckiego",
            "Kuklińskiego",
            "Gromadzka",
            "Lipska",
            "Dworzec Płaszów Estakada",
            "Kabel",
            "Bieżanowska",
            "Dauna",
            "Piaski Nowe",
            "Nowosądecka",
            "Witosa",
            "Kurdwanów P+R"]

        times1 = np.divide([100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100],3)
        coords1 = get_route_coords(route1)

        print(times1,coords1)

        self.trams = [Tram(self.canvas,coords1,np.int_(times1))]
        self.master.after(0,self.animation)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_left_arrow(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_stop(self,x,y,name):
        self.canvas.create_oval(x, y, x+2*STOP_RADIUS , y +2*STOP_RADIUS, fill=STOP_COLOR)
        self.canvas.create_text(x, y-20, fill="darkblue", font="Times 11 italic bold",
                                text=name)
    def create_stops(self):

        for stop in self.data:
            stop_name = stop['stop_name']
            x_coord = stop['x_coord']
            y_coord = stop['y_coord']
            self.create_stop(x_coord, y_coord, stop_name)

    def animation(self):
        for tram in self.trams:
            tram.move();
        self.master.after(42,self.animation)



### tu funkcja która ci zamienia trase typu ['Wesele', 'Bronowice', 'Głowackiego']
###  na trase typu [(230, 203), (284, 202), (639, 484)]
def get_route_coords(route):
    coordinates = []
    for x in range(len(route)):
        for stop in data:
            if stop['stop_name'] == route[x]:
                coordinates.append((stop["x_coord"],stop["y_coord"]))
    return coordinates;



if __name__ == '__main__':
    with open('data.json') as f:
        data = json.load(f)
    root = Tk()
    filename = "resources/linie_tramwajowe_blank.png"
    json_file = "data.json"
    my_gui = MyFirstGUI(root,filename,json_file)
    root.mainloop()

