from tkinter import Tk, Label, Button, Frame, SUNKEN, Scrollbar, HORIZONTAL, Canvas, N, S, E, W, BOTH, ALL, simpledialog
from PIL import Image, ImageTk
import json
import numpy as np
import pandas as pd
import time
import calendar
import random




with open('data/data_with_factors.json') as f:
    STOP_DATA = json.load(f)
with open('data/tram_models_capacities.json','r') as f:
    TRAM_CAPACITIES = json.load(f)
df = pd.read_json('data/traffic_in_time.json')



def get_route_coords(route):
    coordinates = []
    for x in range(len(route)):
        for stop in STOP_DATA:
            if stop['stop_name'] == route[x]:
                coordinates.append((stop["x_coord"], stop["y_coord"]))
    return coordinates


def get_coords_of_stop(stop_name):
    for stop in STOP_DATA:
        if stop['stop_name'] == stop_name:
            return (stop["x_coord"], stop["y_coord"])

def get_value_from_timestamp(time,trafficIndexFormatted,trafficValues):
    return np.interp(time,trafficIndexFormatted,trafficValues)

def to_timestamp(d):
  return calendar.timegm(d.timetuple())

def decision(probability):
    return random.random() < probability

def get_hex_value(decimal):
    result = hex(decimal)[2:]
    if len(result) == 1:
        result = '0'+result
    return result


FPS = 24
STOP_COLOR = 'lightblue'
STOP_RADIUS = 12
TRAM_COLOR = 'yellow'
TRAM_RADIUS = 10
TIME_FACTOR = 1
START_DATE = to_timestamp(pd.Timestamp('2018-07-23 0:00:00'))
START_TIME = 6 * 3600 + 45
INDEPENDENT_COURSES = 500000
TIMES = pd.Series(df.index).apply(to_timestamp)
TRAFFIC = df.value*INDEPENDENT_COURSES

class TramStop:
    def __init__(self,canvas,x,y,name,factor):
        self.x = x
        self.y = y
        self.name = name
        self.factor = factor
        if self.factor == None:
            self.factor = 0
        self.canvas = canvas
        self.crowd = 0
        self.draw()

    def draw(self):
        self.body = self.canvas.create_oval(self.x, self.y, self.x + 2 * STOP_RADIUS, self.y + 2 * STOP_RADIUS, fill=STOP_COLOR)
        self.canvas.create_text(self.x, self.y - 20, fill="darkblue", font="Times 11 italic bold",
                                text=self.name)
        self.crowd_text = self.canvas.create_text(self.x+ STOP_RADIUS, self.y +STOP_RADIUS, fill="black", font="Times 11 bold",
                                text=self.crowd)

    def update(self,seconds):
        probability = get_value_from_timestamp(START_DATE+seconds,TIMES,TRAFFIC)*self.factor/FPS*TIME_FACTOR
        if probability>1:
            self.crowd+=int(probability)
        elif decision(probability):
            self.crowd += 1
        self.canvas.itemconfig(self.crowd_text, text=self.crowd)
        self.update_radius()

    def update_radius(self):
        difference = int(self.crowd / 5)
        x0 = self.x - difference
        y0 = self.y - difference
        x1 = self.x + 2 * STOP_RADIUS + difference
        y1 = self.y + 2 * STOP_RADIUS + difference
        self.canvas.coords(self.body, x0, y0, x1, y1)


class Tram:
    def __init__(self, canvas, route, times, number,stops):
        self.number = number
        self.canvas = canvas
        self.stops = stops
        self.route_names = route
        self.route = get_route_coords(route)
        self.times = np.multiply(times, FPS)
        self.draw()
        self.people = 0
        self.max_people = TRAM_CAPACITIES[str(self.number)]['capacity']
        self.stop_count = 0
        self.counter = 0
        self.in_action = True
        self.moving = True
        self.time = self.times[self.stop_count]
        self.calculate_direction()


    def draw(self):
        x, y = self.route[0]
        self.body = self.canvas.create_oval(int(x), int(y), int(x + 2 * TRAM_RADIUS), int(y + 2 * TRAM_RADIUS),
                                            fill=TRAM_COLOR, outline='#00ff00',width=3)

        self.text = self.canvas.create_text(int(x + TRAM_RADIUS), int(y + TRAM_RADIUS), fill='black', text=self.number,
                                            font="Times 9 italic bold",
                                            activefill='red')

    def move(self):
        if self.in_action and (self.moving):
            self.action()

    def action(self):
        x, y = np.multiply(np.divide(self.direction, self.time), TIME_FACTOR)
        self.canvas.move(self.body, x, y)
        self.canvas.move(self.text, x, y)
        self.counter += 1 * TIME_FACTOR
        if self.counter >= self.time - TIME_FACTOR:
            self.canvas.coords(self.body, self.get_4_coords_of_stop(self.route[self.stop_count + 1]))
            self.canvas.coords(self.text, tuple(np.add(self.route[self.stop_count + 1], (TRAM_RADIUS, TRAM_RADIUS))))
            self.change_direction()

    def get_4_coords_of_stop(self, coords):
        return (coords[0], coords[1], coords[0] + 2 * TRAM_RADIUS, coords[1] + 2 * TRAM_RADIUS)

    def change_direction(self):
        self.counter = 0
        self.stop_count += 1
        if self.stop_count < len(self.times):
            self.calculate_direction()
            self.time = self.times[self.stop_count]
        else:
            self.interaction_with_tram_stop()
            self.in_action = False
            self.canvas.delete(self.body)
            self.canvas.delete(self.text)

    def calculate_direction(self):
        self.interaction_with_tram_stop()
        self.direction = np.subtract(self.route[self.stop_count + 1], self.route[self.stop_count])

    def interaction_with_tram_stop(self):
        stop = self.get_tram_stop_by_name(self.route_names[self.stop_count])
        if stop != None:

            people_leaving = self.calculate_people_leaving(stop)
            self.people -= people_leaving
            people_entering = self.calculate_people_entering(stop)
            stop.crowd -= people_entering
            self.people += people_entering
            self.update_tram_excess_border()
            self.stops.remove(stop)

    def update_tram_excess_border(self):
        excess = int(min(self.people / self.max_people * 255, 255))
        self.canvas.itemconfig(self.body, outline="#" + get_hex_value(excess) + get_hex_value(255 - excess) + "00")

    def calculate_people_leaving(self, stop):
        return int(self.people * self.get_probability_of_leaving(stop))

    def calculate_people_entering(self, stop):
        return min(self.max_people - self.people,
                   int(0.9 * (max(((1 - (self.stop_count) / len(self.route)), 0))) * stop.crowd))

    def get_tram_stop_by_name(self, name):
        for stop in self.stops:
            if stop.name == name:
                return stop
    def get_probability_of_leaving(self, stop):
        if self.stop_count > 0:
            sum = 0
            for s in self.stops:
                sum += s.factor
            return stop.factor/sum
        return 0


class ApplicationGui:
    def __init__(self, master, filename, stops_json, trams_data_json):
        with open(stops_json) as f:
            self.stops_data = json.load(f)

        with open(trams_data_json) as f:
            self.trams_data = json.load(f)

        open("output/result_stops.csv","w").close()
        open("output/result_trams.csv", "w").close()

        self.master = master
        self.filename = filename
        self.setup_animation_window()
        self.setup_trams_and_stops()
        self.master.after(0, self.animation)

    def setup_trams_and_stops(self):
        self.trams = []
        self.tram_counter = 0
        self.stops = []
        self.create_stops()

    def animation(self):
        self.spawn_trams()
        self.update_trams_and_stops()
        self.update_seconds()
        self.update_labels()
        self.master.after(int(1000 / FPS), self.animation)

    def spawn_trams(self):
        while self.trams_data[self.tram_counter]['start_time'] <= int(self.seconds):
            relevant_stops = []
            for stop in self.stops:
                if stop.name in self.trams_data[self.tram_counter]['route']:
                    relevant_stops.append(stop)
            t = Tram(self.canvas,
                     self.trams_data[self.tram_counter]['route'],
                     self.trams_data[self.tram_counter]['times'],
                     self.trams_data[self.tram_counter]['number'], relevant_stops)
            self.trams.append(t)
            self.tram_counter += 1

    def update_trams_and_stops(self):
        self.trams = [i for i in self.trams if i.in_action]
        for tram in self.trams:
            tram.move()
        for stop in self.stops:
            stop.update(self.seconds)
        if decision(1):
            with open("output/result_stops.csv","a",encoding="utf-8") as myfile:
                for stop in self.stops:
                    myfile.write("{},{},{}\n".format(int(self.seconds),stop.name,stop.crowd))
            with open("output/result_trams.csv","a",encoding="utf-8") as myfile:
                for tram in self.trams:
                    myfile.write("{},{},{},{}\n".format(int(self.seconds),
                                                     tram.number,
                                                     int(100*tram.people/tram.max_people),
                                                     tram.route_names[tram.stop_count]))

    def update_seconds(self):
        self.seconds += int(1000 / FPS) / 1000 * TIME_FACTOR

    def update_labels(self):
        self.time.config(text="Godzina: {}".format(time.strftime('%H:%M:%S', time.gmtime(self.seconds))))
        self.time_factor.config(text="Przyspieszenie: {}".format(TIME_FACTOR))

    def setup_animation_window(self):
        self.master.title("Symulacja krakowskich lini tramwajowych")
        self.setup_labels()
        self.setup_buttons()
        self.setup_frame()
        self.setup_scrolling()
        self.setup_canvas()
        self.setup_background()

    def setup_background(self):
        self.img = ImageTk.PhotoImage(Image.open(self.filename))
        self.canvas.create_image(0, 0, image=self.img, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

    def setup_canvas(self):
        self.canvas = Canvas(self.frame, bd=0, width=1326, height=400, xscrollcommand=self.xscroll.set,
                             yscrollcommand=self.yscroll.set)
        self.xscroll.config(command=self.canvas.xview)
        self.yscroll.config(command=self.canvas.yview)
        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
        self.bind_navigators()

    def bind_navigators(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Left>", lambda event: self.canvas.xview_scroll(-1, "units"))
        self.canvas.bind("<Right>", lambda event: self.canvas.xview_scroll(1, "units"))
        self.canvas.focus_set()
        self.canvas.bind("<1>", lambda event: self.canvas.focus_set())

    def setup_scrolling(self):
        self.xscroll = Scrollbar(self.frame, orient=HORIZONTAL)
        self.xscroll.grid(row=1, column=0, sticky=E + W)
        self.yscroll = Scrollbar(self.frame)
        self.yscroll.grid(row=0, column=1, sticky=N + S)

    def setup_frame(self):
        self.frame = Frame(root, bd=2, relief=SUNKEN)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.pack(fill=BOTH, expand=1)

    def setup_buttons(self):
        self.button = Button(self.master, text="speedUp", command=self.speed_up)
        self.button.pack()
        self.button = Button(self.master, text="speedDown", command=self.speed_down)
        self.button.pack()

    def setup_labels(self):
        self.label = Label(self.master, text="Mapa")
        self.label.pack()
        self.seconds = START_TIME
        self.time = Label(self.master, text="Godzina: {}".format(time.strftime('%H:%M:%S', time.gmtime(self.seconds))))
        self.time.pack()
        self.time_factor = Label(self.master, text="Przyspieszenie: {}".format(TIME_FACTOR))
        self.time_factor.pack()

    def draw_route(self, coords):
        for i in range(len(coords) - 1):
            self.canvas.create_line(coords[i][0] + TRAM_RADIUS, coords[i][1] + TRAM_RADIUS,
                                    coords[i + 1][0] + TRAM_RADIUS, coords[i + 1][1] + TRAM_RADIUS, width=3)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_left_arrow(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_stop(self, x, y, name):
        self.canvas.create_oval(x, y, x + 2 * STOP_RADIUS, y + 2 * STOP_RADIUS, fill=STOP_COLOR)
        self.canvas.create_text(x, y - 20, fill="darkblue", font="Times 11 italic bold",
                                text=name)

    def create_stops(self):
        for stop in self.stops_data:
            s = TramStop(self.canvas,stop['x_coord'],stop['y_coord'],stop['stop_name'],stop['factor'])
            self.stops.append(s)

    def speed_up(self):
        global TIME_FACTOR
        TIME_FACTOR *= 2

    def speed_down(self):
        global TIME_FACTOR
        TIME_FACTOR /= 2


if __name__ == '__main__':
    root = Tk()
    filename = "resources/linie_tramwajowe_blank.png"
    stops_json = 'data/data_with_factors.json'
    tram_data_json = 'data/tram_data.json'
    my_gui = ApplicationGui(root, filename, stops_json, tram_data_json)
    root.mainloop()
