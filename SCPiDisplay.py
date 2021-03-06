__author__ = 'YutongGu'

from PiConnector import *
from Tkinter import *
from Datalists import Datalists
from PiReader import valueReader #@#################comment out when testing on laptop#####################
from PIL import Image, ImageTk
import datetime
#!/usr/bin/env python
# -*- coding: utf-8 -*-

#colors for GUI
FILL1="#008080"
FILL2="#00b3b3"
FILL3="#00e6e6"
FILL4="#1affff"
FILL5="#99ffff"
FILL6="#ccffff"
FILL7="WHITE"
BAD="#ff9980"
WARN="#ffffb3"
GOOD="#33cc33"



#Path for icons which I got from http://www.flaticon.com/free-icons/wifi_358/3
PATHROOT="/home/pi/Desktop/telemepi/"   #for raspberry pi
#PATHROOT=""                            #for laptop

#the purpose of this class is just for displaying values and updating them in the GUI
#values will be stored in DataLists class in Datalists
#values will be read from the dataReader class in PiReader
#values will be transmitted from the Connector class in PiConnector
class Display():

    timeLabel = Label()
    labels = {"cabintemp": Label(), "motortemp": Label(), "batterytemp": Label(), "motorrpm": Label(), "solarvolt": Label(), "batvolt": Label(), "connectIcon": Label()}
    icons = {"connection": PhotoImage()}
    UPDATESPEED_MS = 100
    batteryX1 = 0
    batteryX2 = 0
    batteryY1 = 0
    batteryY2 = 0
    height = 0
    chargedrainratio = 0.5
    first = 0
    WIDTH = 600
    HEIGHT = 350

    #close all sockets, stops reading values and clears GPIO pins before closing program
    def quit(self):
        self.connector.closeall()
        self.reader.quit() #@#################comment out when testing on laptop#####################
        print "Master quit"
        self.master.quit()

    #updates the GUI with values from the reader
    def update(self):
        #display time
        localtime=datetime.datetime.now().strftime('%H:%M')
        self.timeLabel.config(text=localtime)

        #update the labels with values
        keys=self.datalist.data.keys()
        for i in keys:
            color=WARN
            value=self.datalist.data[i]
            #doesn't change the color for motorrpm and batvoltlabels
            if i == "motorrpm" or i == "batvolt":
                self.labels[i].config(text=str(value)+self.datalist.dataunits[i])
                continue
            #assigning appropriate value for label color based on value
            if value < self.datalist.databounds[i][0]:
                color=self.datalist.datarules[i][0]
            elif value < self.datalist.databounds[i][1]:
                color=self.datalist.datarules[i][1]
            elif value < self.datalist.databounds[i][2]:
                color=self.datalist.datarules[i][2]
            elif value < self.datalist.databounds[i][3]:
                color=self.datalist.datarules[i][3]
            else:
                color=self.datalist.datarules[i][4]
            self.labels[i].config(text=str(value)+self.datalist.dataunits[i], bg=color)

        #delete the battery and charge bar to be redrawn later
        self.batterydisplay.delete("level")
        self.chargedisplay.delete("level")

        #update chargedischargeratio (will eventually change for more accurate model)
        total=self.datalist.data["solarvolt"]+self.datalist.data["motorrpm"]
        if(total == 0):
            self.chargedrainratio = 0.5
        else:
             self.chargedrainratio = (self.datalist.data["solarvolt"]*1.0/(total))

        #set the color for the charge bar based on chargedrainratio and redraw the bar
        color = GOOD
        if self.chargedrainratio<0.4:
            color = BAD
        elif self.chargedrainratio<0.6:
            color = WARN
        self.chargedisplay.create_rectangle(5, 7, (self.chargedisplay.winfo_reqwidth()-10)*self.chargedrainratio+5, self.chargedisplay.winfo_reqheight()-7, fill=color, width=2, tag="level")

        #set the color for the battery bar and redraw the bar
        color = GOOD
        if self.datalist.data["batvolt"] < 15:
            color = BAD
        elif self.datalist.data["batvolt"] < 40:
            color = WARN
        self.batterydisplay.create_rectangle(self.batteryX1, (self.batteryY2-(self.height*self.datalist.data["batvolt"]/100)), self.batteryX2, self.batteryY2,fill=color, tag="level")

        if self.connector.statusChanged:
            print("Connection status changed")
            if self.connector.connected:
                PILimage = Image.open(PATHROOT+"Images/connected.png")
                scale_w = self.WIDTH/600.0
                scale_h = self.HEIGHT/350.0
                PILimage = PILimage.resize((int(32*scale_w), int(32*scale_h)), Image.ANTIALIAS) #The (250, 250) is (height, width)
                if PILimage is not None:
                    self.icons["connection"] = ImageTk.PhotoImage(PILimage)
                    self.labels["connectIcon"].config(image=self.icons["connection"])
            else:
                PILimage = Image.open(PATHROOT+"Images/disconnected.png")
                scale_w = self.WIDTH/600.0
                scale_h = self.HEIGHT/350.0
                PILimage = PILimage.resize((int(32*scale_w), int(32*scale_h)), Image.ANTIALIAS) #The (250, 250) is (height, width)
                if PILimage is not None:
                    self.icons["connection"] = ImageTk.PhotoImage(PILimage)
                    self.labels["connectIcon"].config(image=self.icons["connection"])
            self.connector.statusChanged=False

        #ensuring that this window is on top
        if self.first < 2:
            self.master.lift()
            self.first += 1

        #update yoself
        self.master.after(self.UPDATESPEED_MS, self.update)
        pass
                
    def __init__(self):
        print('starting')

        #create the datalist, connector, valueReader, and the TK window
        self.datalist = Datalists()
        self.connector = Connector(self.datalist)
        self.reader = valueReader(self.datalist) #@#################comment out when testing on laptop#####################
        self.master = Toplevel()

        #give the window its dimensions and title
        self.master.geometry(str(self.WIDTH)+"x"+str(self.HEIGHT+25))
        self.master.title("SCSC Racing Telemetry")

        #frame for displaying the time
        timeframe = Frame(self.master, height=25, width=self.WIDTH, bg=FILL1)
        timeframe.pack_propagate(0)
        timeframe.grid(row=0, columnspan=3)

        #frame for displaying the speed
        speedframe=Frame(self.master, height=2*self.HEIGHT/5, width=self.WIDTH/2, bg=FILL2)
        speedframe.grid_propagate(0)
        speedframe.grid(row=1, column=0)

        #frame for displaying other stats
        statsframe=Frame(self.master, height=2*self.HEIGHT/5, width=self.WIDTH/2, bg=FILL3)
        statsframe.grid_propagate(0)
        statsframe.grid(row=2, column=0)

        #frame for displaying battery stats
        batteryframe=Frame(self.master, height=4*self.HEIGHT/5, width=3*self.WIDTH/8, bg=FILL4) #blue-ish
        batteryframe.grid_propagate(0)
        batteryframe.grid(row=1, column=1, rowspan=2)

        #frame for warning/error icons
        errorframe=Frame(self.master, height=4*self.HEIGHT/5, width=self.WIDTH/8, bg=FILL7)
        errorframe.grid_propagate(0)
        errorframe.grid(row=1, column=2, rowspan=2)

        #frame for the charging meter
        chargeframe=Frame(self.master, height=self.HEIGHT/10, width=self.WIDTH, bg=FILL5)
        chargeframe.grid_propagate(0)
        chargeframe.grid(row=3, columnspan=3)

        #frame for buttons (if necessary)
        buttonframe=Frame(self.master, height=self.HEIGHT/10, width=self.WIDTH, bg=FILL6)
        buttonframe.grid_propagate(0)
        buttonframe.grid(row=4, columnspan=3)

        '''***********************CREATING LABELS WITH VALUES*************************'''

        label = Label(statsframe, text="Cabin Temperature:", anchor=W, wraplength=self.WIDTH/7,bg=FILL3, justify=LEFT,
                         font=("Helvetica", 9, "bold"), padx=10)
        label.grid(row=0)
        self.labels["cabintemp"] = Label(statsframe, text="0"+str(self.datalist.dataunits["cabintemp"]), anchor=W,bg=FILL3, font=("Helvetica", 16))
        self.labels["cabintemp"].grid(row=0,column=1)

        label = Label(statsframe, text="Motor Temperature:", anchor=W, wraplength=self.WIDTH/7,bg=FILL3, justify=LEFT,
                         font=("Helvetica", 9, "bold"), padx=10)
        label.grid(row=1)
        self.labels["motortemp"] = Label(statsframe, text="0"+str(self.datalist.dataunits["motortemp"]), anchor=W,bg=FILL3, font=("Helvetica", 16))
        self.labels["motortemp"].grid(row=1,column=1)

        label = Label(statsframe, text="Battery Temperature:", anchor=W, wraplength=self.WIDTH/7,bg=FILL3, justify=LEFT,
                         font=("Helvetica", 9, "bold"), padx=10)
        label.grid(row=1, column=2)
        self.labels["batterytemp"] = Label(statsframe, text="0"+str(self.datalist.dataunits["batterytemp"]), anchor=W,bg=FILL3, font=("Helvetica", 16))
        self.labels["batterytemp"].grid(row=1,column=3)

        label = Label(speedframe, text="Motor RPM:", width=self.WIDTH/16, anchor=W, bg=FILL2,
                         font=("Helvetica", 12, "bold"), padx=10)
        label.grid(row=0, column=0)
        self.labels["motorrpm"] = Label(speedframe, text="0"+str(self.datalist.dataunits["motorrpm"]),width=self.WIDTH/80,anchor=W,bg=FILL2, font=("Helvetica", 48), padx=10)
        self.labels["motorrpm"].grid(row=1, column=0, sticky=W)

        label = Label(statsframe, text="Solar Panel Voltage:", anchor=W, wraplength=self.WIDTH/7,bg=FILL3, justify=LEFT,
                         font=("Helvetica", 9, "bold"), padx=10)
        label.grid(row=0, column=2)
        self.labels["solarvolt"] = Label(statsframe, text="0"+str(self.datalist.dataunits["solarvolt"]), anchor=W,bg=FILL3, font=("Helvetica", 16))
        self.labels["solarvolt"].grid(row=0,column=3)

        label = Label(batteryframe, text="Battery Voltage:", height=1, width=self.WIDTH/16, anchor=W, bg=FILL4,
                         font=("Helvetica", 12, "bold"), padx=10)
        label.grid(row=0, columnspan=2)
        self.labels["batvolt"] = Label(batteryframe, text="0"+str(self.datalist.dataunits["batvolt"]), bg=FILL4, font=("Helvetica", 24), pady=self.HEIGHT/40) #blue-ish
        self.labels["batvolt"].grid(row=1, column=0, sticky=E)

        '''**************************************************************************'''

        #displaying the time
        localtime = datetime.datetime.now().strftime('%H:%M')
        self.timeLabel = Label(timeframe, text=localtime, bg=FILL1, font=("Helvetica", 12, "bold"), anchor=E, padx=10)
        self.timeLabel.pack(side=RIGHT )

        #canvas for displaying the battery bar
        self.batterydisplay = Canvas(batteryframe, bg=FILL4, highlightthickness=0, width=batteryframe.winfo_reqwidth()/2, height=batteryframe.winfo_reqheight()-25) #blue-ish
        self.batteryX1 = self.batterydisplay.winfo_reqwidth()/4
        self.batteryY1 = self.batterydisplay.winfo_reqheight()/8
        self.batteryX2 = 3*self.batterydisplay.winfo_reqwidth()/4
        self.batteryY2 = 7*self.batterydisplay.winfo_reqheight()/8
        self.height = self.batteryY2-self.batteryY1
        self.batterydisplay.create_rectangle(self.batteryX1, self.batteryY1, self.batteryX2, self.batteryY2, outline="BLACK", width=2)
        self.batterydisplay.create_rectangle(self.batteryX1, (self.batteryY2-(self.height*self.datalist.data["batvolt"]/100)), self.batteryX2, self.batteryY2, fill=WARN, tag="level")
        self.batterydisplay.grid(row=1, column=1)

        #canvas for displaying the charging meter
        label= Label(chargeframe, text="Charging meter:", font=("Helvetica", 12, "bold"), anchor=W, bg=FILL5, justify=LEFT, padx=10)
        label.grid(row=0, column=0)
        self.chargedisplay = Canvas(chargeframe, bg=FILL5, highlightthickness=0, width=chargeframe.winfo_reqwidth()*3/4, height=chargeframe.winfo_reqheight())
        self.chargedisplay.grid(row=0, column=1)
        self.chargedisplay.create_rectangle(5, 7, self.chargedisplay.winfo_reqwidth()-5, self.chargedisplay.winfo_reqheight()-7, width=2)
        self.chargedisplay.create_line(self.chargedisplay.winfo_reqwidth()/2, 7, self.chargedisplay.winfo_reqwidth()/2, 0, width=2)
        self.chargedisplay.create_rectangle(5, 7, (self.chargedisplay.winfo_reqwidth()-10)*self.chargedrainratio+5, self.chargedisplay.winfo_reqheight()-7, fill=WARN, width=2, tag="level")


        PILimage = Image.open(PATHROOT+"Images/disconnected.png")
        if PILimage is not None:
            scale_w = self.WIDTH/600.0
            scale_h = self.HEIGHT/350.0
            PILimage = PILimage.resize((int(32*scale_w), int(32*scale_h)), Image.ANTIALIAS) #The (250, 250) is (height, width)
            self.icons["connection"] = ImageTk.PhotoImage(PILimage)
            if self.icons["connection"] is not None:

                self.labels["connectIcon"]=Label(errorframe,image=self.icons["connection"], justify=CENTER, height=50, bg=FILL7)
                self.labels["connectIcon"].grid(row=0, sticky=N)


        #fine tuning the positioning of labels
        buttonframe.grid_columnconfigure(0, weight=1)
        buttonframe.grid_columnconfigure(1, weight=1)
        statsframe.grid_columnconfigure(0, weight=2)
        statsframe.grid_columnconfigure(1, weight=1)
        statsframe.grid_columnconfigure(2, weight=2)
        statsframe.grid_columnconfigure(3, weight=1)
        statsframe.grid_rowconfigure(0, weight=1)
        statsframe.grid_rowconfigure(1, weight=1)
        speedframe.grid_rowconfigure(0, weight=1)
        speedframe.grid_rowconfigure(1, weight=7)
        batteryframe.grid_columnconfigure(0, weight=1)
        batteryframe.grid_columnconfigure(1, weight=1)
        errorframe.grid_columnconfigure(0, weight=1)

        #start updating the gui
        self.update()
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        self.master.mainloop()

if __name__ == '__main__':
   Display()
