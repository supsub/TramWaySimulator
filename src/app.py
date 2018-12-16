from tkinter import Tk, Label, Frame,SUNKEN,Scrollbar,HORIZONTAL,Canvas,N,S,E,W,BOTH,ALL,simpledialog
from PIL import Image, ImageTk
import json
import numpy as np


STOP_COLOR = 'red'
STOP_RADIUS = 7
TRAM_COLOR = 'yellow'
TRAM_RADIUS = 7
LIGHT_RADIUS = 4

with open('data/data.json') as f:
    STOP_DATA = json.load(f)

class Tram:
    def __init__(self,canvas,route,times,intersections):
        self.stop_count = 0
        self.intersections_passed = 0
        self.counter = 0
        self.time_to_departure = 0
        self.route = route
        self.times = times
        self.canvas = canvas
        self.time = self.times[self.stop_count]
        x, y = route[0]
        self.in_action =True
        self.moving = True
        self.calculate_direction()
        self.draw(x, y)

    def draw(self, x, y):
        self.body = self.canvas.create_oval(int(x), int(y), int(x + 2 * TRAM_RADIUS), int(y + 2 * TRAM_RADIUS),
                                            fill=TRAM_COLOR)

    def calculate_direction(self):
        self.direction = np.subtract(self.route[self.stop_count + 1], self.route[self.stop_count])

    def move(self):
        if self.time_to_departure>0:
            self.time_to_departure -=1
        if self.in_action and (self.moving or self.time_to_departure == 0):
            self.action()

    def action(self):
        x, y = np.divide(self.direction, self.time)
        self.canvas.move(self.body, x, y)
        self.counter += 1
        if self.counter == self.time:
            self.change_direction()

    def change_direction(self):
        self.counter = 0
        self.stop_count += 1
        self.moving = False
        self.time_to_departure = 10
        if self.stop_count + 1 < len(self.route):
            self.calculate_direction()
            self.time = self.times[self.stop_count]
        else:
            self.in_action = False


class TrafficLight:
    def __init__(self, canvas,position):
        self.light_timer = 30
        self.canvas = canvas
        self.x, self.y = position
        self.preference = 'A'
        self.change_color()
        self.body = self.canvas.create_oval(int(self.x), int(self.y), int(self.x + 2*LIGHT_RADIUS),int(self.y + 2*LIGHT_RADIUS),fill=self.color)
        self.text = self.canvas.create_text(self.x-20, self.y, fill=self.color, font="Times 11 italic bold",
                                text=self.preference)

    def change_color(self):
        if self.preference == 'A':
            self.color = 'green'
        else:
            self.color = 'red'

    def change(self):
        if self.preference == 'A':
            self.preference = 'B'
        else:
            self.preference = 'A'
        self.change_color()
        self.change_items_color()

    def change_items_color(self):
        self.canvas.itemconfig(self.body, fill=self.color)
        self.canvas.itemconfig(self.text, fill=self.color, text=self.preference)

    def animate(self):
        self.light_timer -=1
        if self.light_timer ==0:
            self.light_timer = 30
            self.change()
class MyFirstGUI:
    def __init__(self, master,filename,stops_json,traffic_lights_json):
        with open(stops_json) as f:
            self.stops_data = json.load(f)

        with open(traffic_lights_json) as f:
            self.traffic_lights_data = json.load(f)

        self.master = master
        self.filename = filename
        self.setup()
        self.create_stops()
        self.lights = []
        #self.create_lights()
        self.lights.append(TrafficLight(self.canvas,get_coords_of_stop("Rondo Mogilskie")))


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

        times1 = np.divide([100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100],1)
        times2 = np.divide(
            [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100], 3)
        coords1 = get_route_coords(route1)

        self.draw_route(coords1)
        self.trams = [Tram(self.canvas,coords1,np.int_(times1),{'Rondo Mogilskie':'A'}),Tram(self.canvas,coords1,np.int_(times2),{'Rondo Mogilskie':'A'})]
        self.master.after(0,self.animation)

    def create_lights(self):

        for light in self.traffic_lights_data:
            type = light['stop_name']
            x = light['x_coord']
            y= light['y_coord']
            self.lights.append(TrafficLight(self.canvas,(x,y),type))

    def setup(self):
        self.master.title("Symulacja krakowskich lini tramwajowych")
        self.label = Label(self.master, text="Mapa")
        self.label.pack()
        self.frame = Frame(root, bd=2, relief=SUNKEN)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.xscroll = Scrollbar(self.frame, orient=HORIZONTAL)
        self.xscroll.grid(row=1, column=0, sticky=E + W)
        self.yscroll = Scrollbar(self.frame)
        self.yscroll.grid(row=0, column=1, sticky=N + S)
        self.canvas = Canvas(self.frame, bd=0, width=1326, height=400, xscrollcommand=self.xscroll.set,
                             yscrollcommand=self.yscroll.set)
        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Left>", lambda event: self.canvas.xview_scroll(-1, "units"))
        self.canvas.bind("<Right>", lambda event: self.canvas.xview_scroll(1, "units"))
        self.canvas.focus_set()
        self.canvas.bind("<1>", lambda event: self.canvas.focus_set())
        self.xscroll.config(command=self.canvas.xview)
        self.yscroll.config(command=self.canvas.yview)
        self.frame.pack(fill=BOTH, expand=1)
        self.img = ImageTk.PhotoImage(Image.open(self.filename))
        self.canvas.create_image(0, 0, image=self.img, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

    def draw_route(self,coords):
        for i in range(len(coords)-1):
            self.canvas.create_line(coords[i][0],coords[i][1],coords[i+1][0],coords[i+1][1],width=3)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_left_arrow(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_stop(self,x,y,name):
        self.canvas.create_oval(x, y, x+2*STOP_RADIUS , y +2*STOP_RADIUS, fill=STOP_COLOR)
        self.canvas.create_text(x, y-20, fill="darkblue", font="Times 11 italic bold",
                                text=name)
    def create_stops(self):

        for stop in self.stops_data:
            stop_name = stop['stop_name']
            x_coord = stop['x_coord']
            y_coord = stop['y_coord']
            self.create_stop(x_coord, y_coord, stop_name)

    def animation(self):
        for tram in self.trams:
            tram.move()
        for light in self.lights:
            light.animate()
        self.master.after(42,self.animation)



### tu funkcja która ci zamienia trase typu ['Wesele', 'Bronowice', 'Głowackiego']
###  na trase typu [(230, 203), (284, 202), (639, 484)]
def get_route_coords(route):
    coordinates = []
    for x in range(len(route)):
        for stop in STOP_DATA:
            if stop['stop_name'] == route[x]:
                coordinates.append((stop["x_coord"],stop["y_coord"]))
    return coordinates
def get_coords_of_stop(stop_name):
    for stop in STOP_DATA:
        if stop['stop_name'] == stop_name:
            return (stop["x_coord"],stop["y_coord"])


if __name__ == '__main__':

    root = Tk()
    filename = "resources/linie_tramwajowe_blank.png"
    stops_json = 'data/data.json'
    traffic_lights_json = 'data/traffic_lights.json'
    my_gui = MyFirstGUI(root,filename,stops_json,traffic_lights_json)
    root.mainloop()

