import pandas as pd
import numpy as np
import json


class TramData:

    def __init__(self, df, tripId):
        self.number = self.get_tram_number(df, tripId)
        self.start_time = self.get_time_of_spawn(df, tripId)
        self.route = self.get_stops_of_trip(df, tripId)
        self.times = self.get_times_of_trip(df, tripId)

    def get_times_of_trip(self, df, tripId):
        return np.int_((df.loc[df['tripId'] == tripId]['time_stamp'].diff() / np.timedelta64(1, 's'))[1:]).tolist()

    def get_delays(self, df, tripId):
        return np.int_(df.loc[df['tripId'] == tripId]['delay']).tolist()

    def get_stops_of_trip(self, df, tripId):
        return list(df.loc[df['tripId'] == tripId]['stopName'])

    def get_time_of_spawn(self, df, tripId):
        hour = df.loc[df['tripId'] == tripId]['time_stamp'].iloc[0].hour
        minute = df.loc[df['tripId'] == tripId]['time_stamp'].iloc[0].minute
        second = df.loc[df['tripId'] == tripId]['time_stamp'].iloc[0].second
        result = int(hour * 3600 + minute * 60 + second)
        return result

    def get_tram_number(self, df, tripId):
        return int(df.loc[df['tripId'] == tripId]['number'].iloc[0])

    def __str__(self):
        return f'Nr. {self.number},\nPoczątek: {self.start_time},\nTrasa {self.route}\nCzasy: {self.times}'

if __name__ == '__main__':
    data = pd.read_csv('../resources/data/report_07-23.csv')
    data = data[['time_stamp', 'stopName', 'number', 'direction', 'tripId', 'delay']]
    data['time_stamp'] = pd.to_datetime(data['time_stamp'], format="%Y/%m/%d %H:%M:%S" )
    tripIds = data.tripId.unique()
    tramDatabase = []

    for ID in tripIds:
        tt = TramData(data,ID)
        tramDatabase.append(tt.__dict__)
    filename = "../data/tram_data.json"
    with open(filename, 'w') as outfile:
        json.dump(tramDatabase, outfile)