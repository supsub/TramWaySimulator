import pandas as pd

class TramData:
    route = []
    times = []
    delays = [] # za kazdym razem dodaje do tej samej listy
    start = ''

    def __init__(self, df):
        self.number = df['number'].iloc[0]
        self.direction = df['direction'].iloc[0]
        for index, row in df.iterrows():
            self.route.append(row['stopName'])
            self.times.append(row['time_stamp'])
            self.delays.append(row['delay'])
        self.start = self.route[0]


    def __str__(self):
        return f'Nr. {self.number} Kierunek {self.start}  - {self.direction}: {self.route} - {self.times}'

if __name__ == '__main__':

    data = pd.read_csv('resources/data/report_07-23.csv');

    data = data[['time_stamp', 'stopName', 'number', 'direction', 'tripId', 'delay']]

    tripIds = data.tripId.unique()

    tramDatabase = []


    for ID in tripIds:
        tt = TramData(data.loc[data['tripId'] == ID])
        tramDatabase.append(tt)

    tram = tramDatabase[0]
    print(tram)
