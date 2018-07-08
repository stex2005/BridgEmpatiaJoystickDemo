# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
-------------------------------------------------------------------------------
Name        : BRIDGEVocal_main
Author      : Andrea Costa
Author      : Marta Gandolla
Created     : 06/06/2017
Version     : 0.1
-------------------------------------------------------------------------------
'''

import os
import sys
import time
import threading
import datetime
import pygame
import numpy
import math
import imutils


import BridgeJoystickGUI

from BridgeConf import BridgeConfClass, BridgeClass, BridgeCoordClass
from BridgeCtrl import Thread_ControlClass
from BridgeJoint import Joint

import wx
from wx.lib.wordwrap import wordwrap
from wx.lib.pubsub import setuparg1 #evita problemi con py2exe
from wx.lib.pubsub import pub as Publisher

import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.axes3d import get_test_data
import matplotlib.animation as animation
from matplotlib.patches import Ellipse, Polygon
from matplotlib import cm

import scipy.io as spio

from PIL import Image
import winsound # per audio feedback


###############################################################################
#PLOT JOYSTICK
class CreatePlotJoystick(wx.Panel):

    def __init__(self, parent, Conf):

        wx.Panel.__init__(self, parent, -1)

        self.Conf     = Conf

        self.dpi      = 75
        self.dim_pan  = parent.GetSize()
        self.figure   = Figure(figsize=(self.dim_pan[0]*1.0/self.dpi,(self.dim_pan[1])*1.0/self.dpi), dpi=self.dpi)
        
        #sysTextColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU) #colore sfondo come finestra
        #col_norm      = (sysTextColour[0]*1.0/255, sysTextColour[1]*1.0/255, sysTextColour[2]*1.0/255)
        #self.figure.patch.set_facecolor(col_norm)

        # Canvas
        self.canvas = FigureCanvas(parent, -1, self.figure)
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.canvas, 1, wx.ALL | wx.EXPAND)


        self.ax = self.figure.add_subplot(1, 1, 1)
        
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])

        parent.SetSizer(sizer1)
        parent.Fit()



###############################################################################
#PLOT 3D EXO
class CreatePlot3DExo(wx.Panel):

    def __init__(self,parent):

        wx.Panel.__init__(self, parent, -1)

        self.Conf     = BridgeConfClass() # serve per prendere le dimensioni del box dove plottare exo

        self.dpi      = 75
        self.dim_pan  = parent.GetSize()
        self.figure   = Figure(figsize=(self.dim_pan[0]*1.0/self.dpi,(self.dim_pan[1])*1.0/self.dpi), dpi=self.dpi)
        
        #sysTextColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU) #colore sfondo come finestra
        #col_norm      = (1.0, 1.0, 1.0)
        #self.figure.patch.set_facecolor(col_norm)

        # Canvas
        self.canvas = FigureCanvas(parent, -1, self.figure)
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.canvas, 1, wx.ALL | wx.EXPAND)


        self.ax = self.figure.add_subplot(1, 1, 1, projection='3d')
        self.ax.axis('equal')

        self.ax.set_xlim3d(-0.1, (self.Conf.l1+self.Conf.l2+self.Conf.l3))
        self.ax.set_ylim3d(-(self.Conf.l1+self.Conf.l2+self.Conf.l3), (self.Conf.l1+self.Conf.l2+self.Conf.l3))
        self.ax.set_zlim3d(-(self.Conf.l1+self.Conf.l2+self.Conf.l3), (self.Conf.l1+self.Conf.l2+self.Conf.l3))
        # self.ax.view_init(elev=10., azim=20)
        self.ax.view_init(elev=30, azim=-20)

        " Set virtual exo "
        marker_style = dict(linestyle='-', color=[0.2, 0.2, 0.2], markersize=20)
        self.line = self.ax.plot([], [], [], marker='o', zorder=0.5, **marker_style)[0]

        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.set_zticklabels([])

        parent.SetSizer(sizer1)
        parent.Fit()

###############################################################################
#PLOT 2D EXO
class CreatePlot2DExo(wx.Panel):

    def __init__(self,parent):

        wx.Panel.__init__(self, parent, -1)

        self.Conf     = BridgeConfClass() # serve per prendere le dimensioni del box dove plottare exo

        self.dpi      = 45
        self.dim_pan  = parent.GetSize()
        self.figure   = Figure(figsize=(self.dim_pan[0]*1.0/self.dpi,(self.dim_pan[1])*1.0/self.dpi), dpi=self.dpi)
        
        #sysTextColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU) #colore sfondo come finestra
        #col_norm      = (sysTextColour[0]*1.0/255, sysTextColour[1]*1.0/255, sysTextColour[2]*1.0/255)
        #self.figure.patch.set_facecolor(col_norm)

        # Canvas
        self.canvas = FigureCanvas(parent, -1, self.figure)
        sizer1 		= wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.canvas, 1, wx.ALL | wx.EXPAND)

        self.ax = self.figure.add_subplot(1, 1, 1)
        self.ax.axis('equal')

        self.ax.set_ylim(-(self.Conf.l1+self.Conf.l2+self.Conf.l3), (self.Conf.l1+self.Conf.l2+self.Conf.l3))
        self.ax.set_xlim(-(self.Conf.l1+self.Conf.l2+self.Conf.l3), (self.Conf.l1+self.Conf.l2+self.Conf.l3))

        " Set virtual exo "
        marker_style = dict(linestyle='-', color=[0.2, 0.2, 0.2], markersize=20)
        self.line = self.ax.plot([], [], marker='o', **marker_style)[0]

        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])

        parent.SetSizer(sizer1)
        parent.Fit()


###############################################################################
# GUI CLASS
class MainWindow(BridgeJoystickGUI.BridgeJoystickWin):
    def __init__(self, parent):

        BridgeJoystickGUI.BridgeJoystickWin.__init__(self,parent)

        " Redirect output to ctrl text "
        redir      			= RedirectText(self.show_terminal)
        sys.stdout 			= redir

        " Define bridge configurations "
        self.Bridge   		= BridgeClass()
        self.Conf     		= BridgeConfClass()
        self.Coord    		= BridgeCoordClass()

        self.TaskAchieved 	= False

        " Plot exo 3D "
        self.exo3d_plot     = CreatePlot3DExo(self.exo3d_container)
        self.ani 			= animation.FuncAnimation(self.exo3d_plot.figure, self.animate, fargs=[],interval = 500)

        " Plot exo 2D "
        self.exo2d_plot1    = CreatePlot2DExo(self.exo_piano1)
        self.exo2d_plot1.ax.set_xlabel('SINISTRA - DESTRA')
        self.exo2d_plot1.ax.set_ylabel('AVANTI - INDIETRO')
        self.ani2d_plot1    = animation.FuncAnimation(self.exo2d_plot1.figure, self.animate_plot2D1, fargs=[],interval = 500)
        self.exo2d_plot2    = CreatePlot2DExo(self.exo_piano2)
        self.exo2d_plot2.ax.set_ylabel('SCENDERE - SALIRE')
        self.exo2d_plot2.ax.set_xlabel('SINISTRA - DESTRA')
        self.ani2d_plot2    = animation.FuncAnimation(self.exo2d_plot2.figure, self.animate_plot2D2, fargs=[],interval = 500)
        self.exo2d_plot3    = CreatePlot2DExo(self.exo_piano3)
        self.exo2d_plot3.ax.set_xlabel('INDIETRO - AVANTI')
        self.exo2d_plot3.ax.set_ylabel('SCENDERE - SALIRE')
        self.ani2d_plot3    = animation.FuncAnimation(self.exo2d_plot3.figure, self.animate_plot2D3, fargs=[],interval = 500)


        # TODO disabilitare i bottoni

    def animate_plot2D1(self, i):
        self.exo2d_plot1.line.set_data([0, self.Coord.Elbow[1], self.Coord.EndEff0[1]], [0+0.1, -self.Coord.Elbow[0]+0.1, -self.Coord.EndEff0[0]+0.1])
        if self.TaskAchieved == True:
            tg = self.exo2d_plot1.ax.scatter(self.Conf.TargetPos[1], - self.Conf.TargetPos[0]+0.1, s=200, c='#33cc33', zorder=10)
        else:
            tg = self.exo2d_plot1.ax.scatter(self.Conf.TargetPos[1], - self.Conf.TargetPos[0]+0.1, s=200, c='red', zorder=10)

    def animate_plot2D2(self, i):
        self.exo2d_plot2.line.set_data([0, self.Coord.Elbow[1], self.Coord.EndEff0[1]], [0, self.Coord.Elbow[2], self.Coord.EndEff0[2]])
        if self.TaskAchieved == True:
            tg = self.exo2d_plot2.ax.scatter(self.Conf.TargetPos[1], self.Conf.TargetPos[2], s=200, c='#33cc33', zorder=10)
        else:
            tg = self.exo2d_plot2.ax.scatter(self.Conf.TargetPos[1], self.Conf.TargetPos[2], s=200, c='red', zorder=10)

    def animate_plot2D3(self, i):
        self.exo2d_plot3.line.set_data([0, self.Coord.Elbow[0], self.Coord.EndEff0[0]], [0, self.Coord.Elbow[2], self.Coord.EndEff0[2]])
        if self.TaskAchieved == True:
            tg = self.exo2d_plot3.ax.scatter(self.Conf.TargetPos[0], self.Conf.TargetPos[2], s=200, c='#33cc33', zorder=10)
        else:
            tg = self.exo2d_plot3.ax.scatter(self.Conf.TargetPos[0], self.Conf.TargetPos[2], s=200, c='red', zorder=10)

    def animate(self, i):
        # se target è davanti -> plot target dopo (così lo vedo davanti)
        if self.Conf.TargetPos[0] > self.Coord.EndEff0[0] or (abs(self.Conf.TargetPos[2]) - abs(self.Coord.EndEff0[2])) <= 0.01:
            self.exo3d_plot.line.set_data([0, self.Coord.Elbow[0], self.Coord.EndEff0[0]], [0, self.Coord.Elbow[1], self.Coord.EndEff0[1]])
            self.exo3d_plot.line.set_3d_properties([0, self.Coord.Elbow[2], self.Coord.EndEff0[2]])

            self.tg = self.exo3d_plot.ax.scatter(self.Conf.TargetPos[0], self.Conf.TargetPos[1], self.Conf.TargetPos[2], s=200, c='red')            
        else:
            self.tg = self.exo3d_plot.ax.scatter(self.Conf.TargetPos[0], self.Conf.TargetPos[1], self.Conf.TargetPos[2], s=200, c='red')

            self.exo3d_plot.line.set_data([0, self.Coord.Elbow[0], self.Coord.EndEff0[0]], [0, self.Coord.Elbow[1], self.Coord.EndEff0[1]])
            self.exo3d_plot.line.set_3d_properties([0, self.Coord.Elbow[2], self.Coord.EndEff0[2]])

        # se go raggiunto target -> taget diventa verde
        if abs(self.Conf.TargetPos[0]-self.Coord.EndEff0[0]) <= 0.02 and abs(self.Conf.TargetPos[1]-self.Coord.EndEff0[1]) <= 0.02 and abs(self.Conf.TargetPos[2]-self.Coord.EndEff0[2]) <= 0.02:
            self.TaskAchieved = True
            self.tg = self.exo3d_plot.ax.scatter(self.Conf.TargetPos[0], self.Conf.TargetPos[1], self.Conf.TargetPos[2], s=200, c='#33cc33')

        " Aggiornamento grafica - Leds "
        if self.Conf.Joystick.Mode == 1:
            self.lbl_Mode.SetLabel(u"●")
        else:
            self.lbl_Mode.SetLabel(u"○")

        if self.Conf.Joystick.SavePosition == 1:
            self.lbl_savePos.SetLabel(u"●")
        else:
            self.lbl_savePos.SetLabel(u"○")

        if self.Conf.Joystick.GotoSavedPosition == 1:
            self.lbl_Goto.SetLabel(u"●")
        else:
            self.lbl_Goto.SetLabel(u"○")

        if self.Conf.Joystick.Alarm == 1:
            self.lbl_alarm.SetBackgroundColour( wx.Colour( 255, 0, 0 ) )
            self.lbl_alarm.Refresh()
        else:
            self.lbl_alarm.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            self.lbl_alarm.Refresh()
        



    def preferences(self, event):
        print "Warning - No preferences available at the moment"

    """ COMMANDS """
    def enableCtrl_command(self, event):
        " Define and start control thread "
        self.Conf.CtrlEnable = True
        " set Jpos as the starting point (a mano) "
        self.Coord.Jpos = self.Conf.Target

        print '*************** Jpos: ', self.Coord.Jpos
        self.Conf.CtrlInput = 'joystick'
        
        self.Bridge.ControlThread = Thread_ControlClass(self.Bridge, self.Conf, self.Coord, Debug = False)
        self.Bridge.ControlThread.start()      

    def disableCtrl_command(self, events):
        print "* Exiting control..."
        self.Conf.CtrlEnable = False

        # Get active threads
        threads_list = threading.enumerate()

        # Kill all the threads except MainThread
        try:
            for i in range(0, len(threads_list)):
                th = threads_list[i]
                if th.name != "MainThread":
                    th.terminate()
        except Exception, e:
            print str(e)

        # Wait for the threads to end
        for i in range(1,len(threads_list)):
            th = threads_list[i]
            if th.name != "MainThread":
                th.join()


    def loadPatient_command(self,event):
        openFileDialog = wx.FileDialog(self, "Load configuration file", "", "",
                                       "Config files (*.ini)|*.ini",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        filename = openFileDialog.GetPath()
        openFileDialog.Destroy()

        if filename:
            if (self.Conf.ReadPatientFile(filename)):
                # self.update_monitor()
                self.Conf.PatientLoaded = True
                self.Conf.PatientFile   = filename
                print '* Patient config uploaded (%s)' % self.Conf.PatientFile
                print '* Init joits with new configurations'
                # TODO abilitare i bottoni
                self.JointInitialization()

    def JointInitialization(self):

        ''' Joints class init '''
        for i in range(0, len(self.Bridge.J)):
            self.Bridge.J[i] = Joint(   i+1,
                                        self.Conf.serial.COM[i],
                                        self.Conf.Jmax[i],
                                        self.Conf.Jmin[i], 
                                        self.Conf.Ratio[i], 
                                        self.Conf.Offset[i], 
                                        self.Conf.Target[i],
                                        self.Coord)


        ''' Define control threads '''
        #self.Bridge.ControlThread = Thread_ControlClass(self.Bridge, self.Conf, self.Coord, Debug = False)

    def exit(self,event):
        " Kill all the threads except MainThread "

        " Get active threads "
        threads_list = threading.enumerate()
        print threads_list

        print "* Terminating Threads ..."
        for i in range(0, len(threads_list)):
            th = threads_list[i]
            if th.name != "MainThread":
                try:
                    th.terminate()
                    th.join()
                except Exception, e:
                    print "# Error terminating " + th.name + " | " + str(e)
        try:
            self.Close()
            print "Closed"
        except Exception, e:
            print "# Error closing | " + str(e)


# STDOUTPUT REDIRECT
class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self, string):
        wx.CallAfter(self.out.WriteText, string)


###############################################################################
#MAIN
#mandatory in wx, create an app, False stands for not deteriction stdin/stdout
app = wx.App(False)

#create an object
frame = MainWindow (None)

#show the frame
frame.Show(True)

#start the applications
app.MainLoop()