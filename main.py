from math import acos, cos, radians, sin
import tkinter as tk
import xml.etree.ElementTree as ET
from multiprocessing import Process, Queue
from tkinter import ttk
import serial
import pynmea2
import time
import csv
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure

def worker():
    print("getting GPS data")

class App(tk.Tk):
    def __init__(self, master=None):
        tk.Tk.__init__(self)
        self.title("CarTrack")
        self.maxsize(800, 400)
        self.minsize(800, 400)
        self._frame = None
        self.switch_frame(DragRacePage)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()

class DragRacePage(tk.Frame):    
    def StartTimer(self):
        self.startLabel.config(text="Waiting for launch...", background="green")
        serial_port = 'COM3'
        baudrate = 38400
        try:
            ser = serial.Serial(serial_port, baudrate=baudrate, timeout=1)
        except serial.serialutil.SerialException as e:
            self.startLabel.config(text=str(e)[:26], background="red")
            return # Exit if no GPS is found

        # 1-Foot Rollout Constants & State
        self.ROLLOUT_DIST_KM = 0.0003048 
        self.rollout_active = False
        self.is_recording = False
        self.current_speed = 0.0
        setInitial = True
        record = True
        
        self.startLat = 0.0
        self.startLong = 0.0
        self.currLat = 0.0
        self.currLong = 0.0

        # Milestones Setup
        self.dist_milestones = [
            {"threshold": 0.09144,  "time": None, "label": self.YARD100TIMELABEL, "stop": False}, 
            {"threshold": 0.201168, "time": None, "label": self.TIMEEIGHTHLABEL, "stop": False},
            {"threshold": 0.402336, "time": None, "label": self.TIMEQAURTERLABEL, "stop": True}
        ]

        self.speed_milestones = [
            {"threshold": 30,  "time": None, "label": self.ZERO30TIMELABEL},
            {"threshold": 60,  "time": None, "label": self.ZERO60TIMELABEL},
            {"threshold": 100, "time": None, "label": self.ZERO100TIMELABEL}
        ]

        while record:
            self.update() # REQUIRED: Forces Tkinter to redraw the UI so it doesn't freeze during the loop
            
            data = ser.readline()
            
            # 1. Update Speed First
            if data.startswith(b'$GNVTG'): 
                msg = pynmea2.parse(data.decode('utf-8'))
                self.current_speed = float(msg.spd_over_grnd_kmph)

                # Process speed milestones only if rollout is finished
                if self.is_recording:
                    for m in self.speed_milestones:
                        if m["time"] is None and self.current_speed >= m["threshold"]:
                            m["time"] = time.time() - self.start_time
                            m["label"].config(text=f'{m["time"]:.3f}')

            # 2. Update Location & Distances
            if data.startswith(b'$GNGLL'):
                msg = pynmea2.parse(data.decode('utf-8'))
                self.currLat = float(msg.latitude)
                self.currLong = float(msg.longitude)
                
                # PHASE A: Staging (Getting ready)
                if setInitial and self.currLat != 0 and self.currLong != 0:
                    self.staged_lat_rad = radians(self.currLat)
                    self.staged_lon_rad = radians(self.currLong)
                    
                    self.startLabel.config(text="Staged (Waiting for Rollout)", background="orange")
                    setInitial = False
                    self.rollout_active = True
                    
                # PHASE B: 1-Foot Rollout
                elif self.rollout_active:
                    currLat_rad = radians(self.currLat)
                    currLong_rad = radians(self.currLong)
                    
                    distance_from_stage = acos(
                        sin(self.staged_lat_rad) * sin(currLat_rad) +
                        cos(self.staged_lat_rad) * cos(currLat_rad) * cos(currLong_rad - self.staged_lon_rad)
                    ) * 6371
                    
                    # Car moved 1 foot AND speed > 2 km/h (ignores GPS drift)
                    if distance_from_stage >= self.ROLLOUT_DIST_KM and self.current_speed > 2.0:
                        self.start_time = time.time()
                        
                        # Set official start line
                        self.startLat = self.currLat
                        self.startLong = self.currLong
                        self.startLat_rad = currLat_rad
                        self.startLong_rad = currLong_rad
                        
                        self.startLabel.config(text="Recording", background="yellow")
                        self.rollout_active = False
                        self.is_recording = True

                # PHASE C: Active Recording
                elif self.is_recording:
                    currLat_rad = radians(self.currLat)
                    currLong_rad = radians(self.currLong)
                    
                    distance = acos(
                        sin(self.startLat_rad) * sin(currLat_rad) +
                        cos(self.startLat_rad) * cos(currLat_rad) * cos(currLong_rad - self.startLong_rad)
                    ) * 6371
                    
                    for m in self.dist_milestones:
                        if m["time"] is None and distance >= m["threshold"]:
                            m["time"] = time.time() - self.start_time
                            m["label"].config(text=f'{m["time"]:.3f}')
                            
                            if m["stop"]:
                                record = False

        # Post-Run Data Saving
        self.endLatLabel.config(text=str(self.currLat))
        self.endLongLabel.config(text=str(self.currLong))
        
        with open(r'drag_race_events.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            # Fetch variables dynamically from the milestone arrays
            row_data = [
                self.start_time, self.startLat, self.startLong, self.currLat, self.currLong, 
                self.dist_milestones[0]["time"], self.dist_milestones[1]["time"], self.dist_milestones[2]["time"], 
                self.speed_milestones[0]["time"], self.speed_milestones[1]["time"], self.speed_milestones[2]["time"]
            ]
            writer.writerow(row_data)

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Welcome to the Stopwatch App!").grid(column=0, row=0)
        
        # Row 1 Content
        tk.Label(self, text="Current Position").grid(column=0, row=1)
        tk.Label(self, text="Lat").grid(column=1, row=1)
        tk.Label(self, text="Long").grid(column=2, row=1)

        # Row 2 Content
        tk.Label(self, text="Now").grid(column=0, row=2)
        tk.Label(self, text="-41.3939429").grid(column=1, row=2)
        tk.Label(self, text="-72.2139239").grid(column=2, row=2)

        # Row 3 Content 
        tk.Label(self, text="End").grid(column=0, row=3)
        self.endLatLabel = tk.Label(self, text="TBD")
        self.endLatLabel.grid(column=1, row=3)
        self.endLongLabel = tk.Label(self, text="TBD")
        self.endLongLabel.grid(column=2, row=3)

        # Row 4 Content
        tk.Button(self, text="Start", command=self.StartTimer).grid(column=0, row=4, columnspan=3, sticky = tk.W+tk.E)

        # Row 5 Content
        tk.Label(self, text="-41.3939429").grid(column=1, row=5)
        tk.Label(self, text="-72.2139239").grid(column=2, row=5)
        
        # Row 6 Content
        self.startLabel = tk.Label(self, text="", background="black")
        self.startLabel.grid(column=0, row=6, columnspan=3, sticky = tk.W+tk.E)
        
        # Row 7 Content
        tk.Label(self, text="0-30").grid(column=0, row=7)
        self.ZERO30TIMELABEL = tk.Label(self, text="TBD")
        self.ZERO30TIMELABEL.grid(column=1, row=7) 

        # Row 8 Content
        tk.Label(self, text="0-60").grid(column=0, row=8)
        self.ZERO60TIMELABEL = tk.Label(self, text="TBD")
        self.ZERO60TIMELABEL.grid(column=1, row=8)

        # Row 9 Content
        tk.Label(self, text="0-100").grid(column=0, row=9)
        self.ZERO100TIMELABEL = tk.Label(self, text="TBD")
        self.ZERO100TIMELABEL.grid(column=1, row=9)

        # Row 10 Content
        tk.Label(self, text="100 Yards").grid(column=0, row=10)
        self.YARD100TIMELABEL = tk.Label(self, text="TBD")
        self.YARD100TIMELABEL.grid(column=1, row=10)

        # Row 11 Content
        tk.Label(self, text="1/8th Mile").grid(column=0, row=11)
        self.TIMEEIGHTHLABEL = tk.Label(self, text="TBD")
        self.TIMEEIGHTHLABEL.grid(column=1, row=11)

        # Row 12 Content
        tk.Label(self, text="1/4 Mile").grid(column=0, row=12)
        self.TIMEQAURTERLABEL = tk.Label(self, text="TBD")
        self.TIMEQAURTERLABEL.grid(column=1, row=12)

        # Row 13 Content
        tk.Label(self, text="", background="black").grid(column=0, row=13, columnspan=3, sticky = tk.W+tk.E)

        # Row 14 Content
        tk.Button(self, text="Drag Records", command=lambda: master.switch_frame(DragRaceRecordsPage)).grid(column=1, row=14)

class DragRaceRecordsPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Records").grid(column=0, row=0)
        
        # Headers
        headers = ["Start Time", "Start Lat", "Start Long"," End Lat", "End Long", "100 Yard Time", "1/8 Time", "1/4 Time", "0-30 Time", "0-60 Time", "0-100 Time"]
        for counter, header in enumerate(headers):
            tk.Label(self, text=header).grid(column=counter, row=1)
        
        with open('drag_race_events.csv', mode='r') as csvfile:
            reader = csv.reader(csvfile)
            for rowCount, line in enumerate(reader):
                for ColoumCount, data in enumerate(line):
                    tk.Label(self, text=data).grid(column=ColoumCount, row=rowCount+3)
        tk.Button(self, text="Back", command=lambda: master.switch_frame(DragRacePage)).grid(column=0, row=100)

#     def __init__(self, master):
#         tk.Frame.__init__(self, master)
#         tk.Label(self, text="TMP Cayuga").grid(column=0, row=0)

#         fig = Figure(figsize=(4,4), dpi=100)
#         tree = ET.parse("cayuga.xml")
#         root = tree.getroot()

#         latCoords = []
#         longCoords = []

#         bigList = ["4378796399", "4378796442", "6342143866", "4378796444", "6342143867", "4378796447", "4378796449", "4378796450", "4378796448", "4378796446", "4378796435", "6342143868", "4378796434", "4378796432", "4378796421", "4378796420", "4378796419", "4378796418", "6342143869", "4378796429", "4378796430", "4378796428", "4378796426", "4378796424", "4378796422", "4378796423", "4378796425", "4378796427", "4378796431", "6342143871", "4378796437", "4378796439", "4378796440", "4378796438", "4378796436", "4378796433", "4378796417", "4378796416", "6342143870", "4378796415", "4378796412", "4378796410", "4378796409", "4378796414", "4378796413", "4378796411", "4378796408", "4378796407", "4378796406", "4378796405", "4378796404", "4378796403", "4378796402", "4378796401", "4378796400", "4378796397", "4378796395", "4378796396", "4378796398", "4378796399"]
#         for item in bigList:
#             for child in root:
#                 try:
#                     if child.attrib["id"] == item:
#                         latCoords.append(float(child.attrib["lat"]))
#                         longCoords.append(float(child.attrib["lon"]))
#                 except KeyError:
#                     pass
#         fig.add_subplot(111).plot(longCoords,latCoords)
#         canvas = FigureCanvasTkAgg(fig, master = self)  
#         canvas.draw()
#         canvas.get_tk_widget().grid(column=0,row=1)
        
app = App()
app.mainloop()
