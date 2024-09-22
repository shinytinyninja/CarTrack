from math import acos, cos, radians, sin
import tkinter as tk
import xml.etree.ElementTree as ET
from multiprocessing import Process, Queue
from tkinter import ttk
import serial
import pynmea2
import time

def worker():
    print("getting GPS data")

class App(tk.Tk):
    def __init__(self, master=None):
        tk.Tk.__init__(self)
        self.title("CarTrack")
        self.maxsize(1000, 400)
        self.minsize(1000, 400)
        self._frame = None
        self.switch_frame(IntroPage)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()

class IntroPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Welcome to the Stopwatch App!").grid(column=0, row=0)

        tk.Label(self, text="Apps").grid(column=0, row=1)

        tk.Label(self, text="Drag Race").grid(column=0, row=2)
        tk.Label(self, text="0-100 Timer").grid(column=0, row=3)
        tk.Label(self, text="Track Lapping").grid(column=0, row=4)

        tk.Button(self, text="Enter", command=lambda: master.switch_frame(DragRacePage)).grid(column=1, row=2)
        tk.Button(self, text="Enter", command=lambda: master.switch_frame(DragRacePage)).grid(column=1, row=3)
        tk.Button(self, text="Enter", command=lambda: master.switch_frame(DragRacePage)).grid(column=1, row=4)

class DragRacePage(tk.Frame):    
    def StartTimer(self):
        self.startLabel.config(text="waiting for lanch", background="green")
        
        ZERO30TIME = 0
        ZERO60TIME = 0
        ZERO100TIME = 0  
        YARD100TIME = 0
        TIMEEIGHTH = 0
        TIMEQAURTER = 0
        serial_port='COM3'
        baudrate=38400
        ser = serial.Serial(serial_port, baudrate=baudrate, timeout=1)

        print("Staring Time" + msg)
        setInitial = True

        while True:
            data = ser.readline()
            if data.startswith(b'$GNGLL'):
                msg = pynmea2.parse(data.decode('utf-8'))
                if setInitial and float(msg.latitude) != 0 and float(msg.longitude) != 0:
                    self.start_time = time.time()
                    self.startLat = float(msg.latitude)
                    self.startLong = float(msg.longitude)
                    self.startLabel.config(text="Recording", background="Yellow")
                    setInitial = False
                else:
                    self.currLat = float(msg.latitude)
                    self.currLong = float(msg.longitude)
                    distance = acos(sin(radians(self.startLat))*sin(radians(self.currLat))+cos(radians(self.startLat))*cos(radians(self.currLat))*(cos(radians(self.currLong)-radians(self.startLong))))*6371
                    
                    if distance >= 91 and YARD100TIME == 0:
                        YARD100TIME = time.time() - self.start_time
                        self.TIME100YARDSLABEL.config(text=str(YARD100TIME))
                    if distance >= 0.201168 and TIMEEIGHTH == 0:
                        TIMEEIGHTH = time.time() - self.start_time
                        self.TIMEEIGHTHLABEL.config(text=str(TIMEEIGHTH))
                    if distance >= 0.402336 and TIMEQAURTER == 0:
                        TIMEQAURTER = time.time() - self.start_time
                        self.TIMEQAURTERLABEL.config(text=str(TIMEQAURTER))
                        break
            
            # Speed Related Metrics
            if data.startswith(b'$GNVTG'): 
                msg = pynmea2.parse(data.decode('utf-8'))
                if float(msg.spd_over_grnd_kmph) >= 30 and ZERO30TIME == 0:
                    ZERO30TIME = time.time() - self.start_time
                if float(msg.spd_over_grnd_kmph) >= 60 and ZERO60TIME == 0:
                    ZERO60TIME = time.time() - self.start_time
                if float(msg.spd_over_grnd_kmph) >= 100 and ZERO100TIME == 0:
                    ZERO100TIME = time.time() - self.start_time
  
        self.endLatLabel.config(text=str(self.currLat))
        self.endLongLabel.config(test=str(self.currLong))

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Welcome to the Stopwatch App!").grid(column=0, row=0)
        
        # Row 1 Content
        tk.Label(self, text="Current Postition").grid(column=0, row=1)
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
        self.startLabel = tk.Label(self, text="",background="black")
        self.startLabel.grid(column=0, row=5, columnspan=3, sticky = tk.W+tk.E)
        
        # Row 7 Content
        tk.Label(self, text="0-30").grid(column=0, row=7)

        # Row 8 Content
        tk.Label(self, text="0-60").grid(column=0, row=8)

        # Row 9 Content
        tk.Label(self, text="0-100").grid(column=0, row=9)
        
        # Row 10 Content
        tk.Label(self, text="100 Yards").grid(column=0, row=10)
        self.TIME100YARDSLABEL = tk.Label(self, text="TBD")
        self.TIME100YARDSLABEL.grid(column=1, row=10)

        # Row 11 Content
        tk.Label(self, text="1/8th Mile").grid(column=0, row=11)
        self.TIMEEIGHTHLABEL = tk.Label(self, text="TBD")
        self.TIMEEIGHTHLABEL.grid(column=1, row=11)

        # Row 12 Content
        tk.Label(self, text="1/4 Mile").grid(column=0, row=12)
        self.TIMEQAURTERLABEL = tk.Label(self, text="TBD")
        self.TIMEQAURTERLABEL.grid(column=1, row=12)

        # Row 13 Content
        tk.Label(self, text="",background="black").grid(column=0, row=13, columnspan=3, sticky = tk.W+tk.E)

        # Row 14 Content
        tk.Button(self, text="Back", command=lambda: master.switch_frame(IntroPage)).grid(column=0, row=14)
        tk.Button(self, text="Drag Records", command=lambda: master.switch_frame(DragRaceRecordsPage)).grid(column=1, row=14)


class DragRaceRecordsPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Welcome to the Stopwatch App!").grid(column=0, row=0)
        tk.Label(self, text="Welcome to the Stopwatch App!").grid(column=0, row=1)

app = App()
app.mainloop()
