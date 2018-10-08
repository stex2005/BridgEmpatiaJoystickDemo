# -*- coding: utf-8 -*-
import threading, time
import pygame
from serial import *
import math
from numpy.linalg import inv
import math
import numpy
from BridgeConf import BridgeConfClass, BridgeClass, BridgeCoordClass
import scipy.io as spio
import datetime
import winsound

global file_EndEff0
file_EndEff0 = []
global file_EndEff_des
file_EndEff_des = []
global file_Jpos
file_Jpos = []
global file_Jdes
file_Jdes = []
global file_p0
file_p0_ = []


class Thread_ControlClass(threading.Thread):
    def __init__(self, Bridge, Conf, Coord, Debug=False):

        threading.Thread.__init__(self)
        self.stop           = threading.Event()
        self.running        = False
        self.Conf           = Conf
        self.Coord          = Coord
        self.Bridge         = Bridge

        self.checkWS        = False
        self.EndEff_des     = numpy.array([0.0, 0.0, 0.0, 0.0])

        self.Jacob          = numpy.zeros((3, 4))
        self.Wq             = numpy.eye(4);
        self.Coord.Jdes     = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0])
        self.Coord.Jv       = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0])
        self.IM_x           = []
        self.IM_y           = []
        self.IM_z           = []
        self.IM_WS          = []
        self.Jpos_rad       = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0])
        self.Jdes_rad       = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0])
        self.temp_Jpos      = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0])
        #self.temp_EndEff0   = numpy.array([0.33167254, 0.22277789, 0.04704141, 0.0])
        self.temp_EndEff0   = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0])
        self.deltaJ         = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0])

        self.Debug          = Debug

        self.i_cnt_debug    = 0

       # inizializzazioni
        self.dq_prec        = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0]) # inizializzazione del primo step
        self.ul             = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0]) # inizializzazione temporal ramp
        self.dl             = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0])
        # parametri
        self.dol            = 5 # gradi di distanza da ROM
        self.du             = 1 # steo to increase/decrease joint limit ramps??
        self.alpha0         = 1

        self.GoToSavedPosMainTrigger    = False

        #self.p0_file        = spio.loadmat('p0.mat')['p0']

        # CULO: erano in connect command
        if self.Conf.CtrlInput == 'joystick':
            try:
                pygame.joystick.init()
                JoystickCnt = pygame.joystick.get_count()
            except:
                print '# Error: pygame.joystick.init() failed.'

        self.p0_check = [0]*4


        self.FirstStart = True

        
    def run(self):

        self.running = True
        #self.loop = len(self.p0_file)
        #self.loop_count = 0

        if self.running:
            
            self.Conf.InitDone = True
             
            ''' Select Joystick nr 0 '''
            if self.Conf.CtrlInput == 'joystick':
                pygame.init()
                try:
                    joystick = pygame.joystick.Joystick(0)
                    joystick.init()

                except Exception, e:
                    print "# Error: Joystick not found | "+str(e)
        else:
            print '* CtrlTherad: exit forced from GUI'


        while self.running:
            # measure process time
            t0 = time.clock()

            self.p0_check = [0, 0, 0, 0]

            " Get data from joystick"
            if self.Conf.CtrlInput == 'joystick':
                #start pygame
                try:
                    events = pygame.event.get()

                    for event in events:
                        if event.type == pygame.QUIT:
                            self.terminate()

                        elif event.type == pygame.JOYAXISMOTION:
                            for i in range (0,2):
                                axis = (joystick.get_axis(i) - self.Conf.Joystick.AxisOffset[i]) * self.Conf.Joystick.Gain

                                # controllo la banda morta (troppo vicino al non spostamento del joystick)
                                if abs(axis) < 0.1:
                                    axis = 0.0

                                if self.Conf.Joystick.Mode == 0:
                                    if i == 0:
                                        self.Coord.p0[i] = -axis * 1.2
                                    else:
                                        self.Coord.p0[i] = axis * 1.2

                                    self.Coord.p0[2] = 0.0
                                    self.Coord.p0[3] = 0.0
                                else:
                                    if i == 0:
                                        #self.Coord.p0[3] = axis * 1.2
                                        self.Coord.p0[3] = 0
                                    else:
                                        self.Coord.p0[2] = axis * 1.2

                                    self.Coord.p0[0] = 0.0
                                    self.Coord.p0[1] = 0.0

                        elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                            winsound.Beep(880, 500)
                            self.Conf.Joystick.Mode                 = joystick.get_button(1)
                            self.Conf.Joystick.SavePosition         = joystick.get_button(2)
                            self.Conf.Joystick.GotoSavedPosition    = joystick.get_button(3)
                            self.Conf.Joystick.Alarm                = joystick.get_button(4)

                    pygame.event.clear()
                except Exception,e:
                    print "# Error: Joystick not found | "+str(e)

            if self.Conf.CtrlEnable:

                if not self.Coord.GoToSavedPosMainTrigger:
                    #print 'CONTROL'
                    self.MartaCtrl()
                else:
                    self.MartaPath()
            else:
                self.Coord.Jv = [1,1,1,1,1]

            elapsed_time = time.clock() - t0

            if elapsed_time > self.Conf.CtrlThreadPeriod:
                elapsed_time = self.Conf.CtrlThreadPeriod
                # print ' CtrlTherad: overrun'
                                
            time.sleep(self.Conf.CtrlThreadPeriod - elapsed_time)


    def MartaPath(self):

        arr = 0

        for i in range (4):
            if self.Coord.GoToSavedPos[i]:
                arr += 1

        if arr == 0:
            self.Coord.GoToSavedPosMainTrigger  = False
            self.Coord.FirstStart               = [True, True, True, True, True]

    def MartaCtrl(self):
        for i in range (4):
            self.Jpos_rad[i] = self.Coord.Jpos[i]*math.pi/180

        # cinematica diretta per calcolo di posizione attuale -> EndEff0
        self.Coord.EndEff0[0] = math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*(self.Conf.l1+self.Conf.l2)-self.Conf.l3*math.sin(self.Jpos_rad[3])*(math.sin(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2])+math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2]))+self.Conf.Rjoint2*(math.sin(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0])-math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.cos(self.Jpos_rad[2]))+self.Conf.l3*math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[3])*math.cos(self.Jpos_rad[1])
        self.Coord.EndEff0[1] = -self.Conf.Rjoint2*(math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[2])+math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2]))+self.Conf.l3*math.sin(self.Jpos_rad[3])*(math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2])-math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0]))+math.sin(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*(self.Conf.l1+self.Conf.l2)+self.Conf.l3*math.cos(self.Jpos_rad[3])*math.sin(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])
        self.Coord.EndEff0[2] = self.Conf.Rjoint2*math.cos(self.Jpos_rad[1])*math.cos(self.Jpos_rad[2])+self.Conf.l3*math.cos(self.Jpos_rad[3])*math.sin(self.Jpos_rad[1])+math.sin(self.Jpos_rad[1])*(self.Conf.l1+self.Conf.l2)+self.Conf.l3*math.sin(self.Jpos_rad[2])*math.sin(self.Jpos_rad[3])*math.cos(self.Jpos_rad[1])
        self.Coord.EndEff0[3] = self.Coord.Jpos[4];

        self.Coord.Elbow[0]   = math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*(self.Conf.l1+self.Conf.l2)+self.Conf.Rjoint2*(math.sin(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0])-math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.cos(self.Jpos_rad[2]))
        self.Coord.Elbow[1]   = -self.Conf.Rjoint2*(math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[2])+math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2]))+math.sin(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*(self.Conf.l1+self.Conf.l2)
        self.Coord.Elbow[2]   = self.Conf.Rjoint2*math.cos(self.Jpos_rad[1])*math.cos(self.Jpos_rad[2])+math.sin(self.Jpos_rad[1])*(self.Conf.l1+self.Conf.l2)

        # calcolo posizione desiderata end effector
        self.EndEff_des[0] = self.Coord.EndEff0[0] - self.Coord.p0[1]*self.Conf.s*self.Conf.ctrl_t # x attuale + joystick*v_max*tempo loop controllo [m]
        self.EndEff_des[1] = self.Coord.EndEff0[1] + self.Coord.p0[0]*self.Conf.s*self.Conf.ctrl_t # y attuale + dy [m]
        self.EndEff_des[2] = self.Coord.EndEff0[2] - self.Coord.p0[2]*self.Conf.s*self.Conf.ctrl_t # z attuale + dz [m]
        self.EndEff_des[3] = self.Coord.EndEff0[3]

        #print self.Coord.EndEff0


        for i in range (4):
            self.temp_EndEff0[i] = self.Coord.EndEff0[i]

        '''
        STEP 2: Check belonging to the possible workspace di EndEff_des
        '''
        self.checkWS = True # da ripristinare if needed


        " STEP 3: IK: EndEff_des -> Jdes (valori di giunto che devo raggiungere [deg]) "

        exit = False
        n = 0
        self.Wq = numpy.eye(4);
        self.dq_prec = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0])

        if self.checkWS and (abs(self.Coord.p0[0]) > 0 or abs(self.Coord.p0[1]) > 0 or abs(self.Coord.p0[2]) > 0 or abs(self.Coord.p0[3]) > 0):
            
            dp = self.EndEff_des[0:3]-self.temp_EndEff0[0:3]

            while (abs(dp[0]) > 1e-7+self.Conf.toll*abs(self.Coord.p0[0]) or abs(dp[1]) > 1e-7+self.Conf.toll*abs(self.Coord.p0[0]) or abs(dp[2]) > 1e-7+self.Conf.toll*abs(self.Coord.p0[0])) and exit == False:

                self.Jacob[0,0]= self.Conf.Rjoint2 *(math.cos(self.Jpos_rad[0]) *math.sin(self.Jpos_rad[2]) + math.cos(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])) - self.Conf.l3*math.sin(self.Jpos_rad[3])*(math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2]) - math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])) - math.cos(self.Jpos_rad[1])*math.sin(self.Jpos_rad[0])*(self.Conf.l1 + self.Conf.l2) - self.Conf.l3*math.cos(self.Jpos_rad[1])*math.cos(self.Jpos_rad[3])*math.sin(self.Jpos_rad[0])
                self.Jacob[0,1]= -math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*(self.Conf.l1 + self.Conf.l2) -self.Conf.Rjoint2*math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*math.cos(self.Jpos_rad[2]) -self.Conf.l3*math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[3])*math.sin(self.Jpos_rad[1]) -self.Conf.l3*math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])*math.sin(self.Jpos_rad[3])
                self.Jacob[0,2]= self.Conf.Rjoint2*(math.cos(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0]) + math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])) + self.Conf.l3*math.sin(self.Jpos_rad[3])*(math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[2]) - math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2])*math.sin(self.Jpos_rad[1]))
                self.Jacob[0,3]= - self.Conf.l3*math.cos(self.Jpos_rad[3])*(math.cos(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0]) + math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])) - self.Conf.l3*math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*math.sin(self.Jpos_rad[3])
                self.Jacob[1,0]= self.Conf.Rjoint2*(math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[2]) - math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2])*math.sin(self.Jpos_rad[1])) - self.Conf.l3*math.sin(self.Jpos_rad[3])*(math.cos(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0]) + math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])) + math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*(self.Conf.l1 + self.Conf.l2) + self.Conf.l3*math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*math.cos(self.Jpos_rad[3]) 
                self.Jacob[1,1]= - math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*(self.Conf.l1 + self.Conf.l2) - self.Conf.Rjoint2*math.cos(self.Jpos_rad[1])*math.cos(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0]) - self.Conf.l3*math.cos(self.Jpos_rad[3])*math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1]) - self.Conf.l3*math.cos(self.Jpos_rad[1])*math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[2])*math.sin(self.Jpos_rad[3])
                self.Jacob[1,2]= - self.Conf.Rjoint2*(math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2]) - math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])) - self.Conf.l3*math.sin(self.Jpos_rad[3])*(math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[2]) + math.cos(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1]))
                self.Jacob[1,3]= self.Conf.l3*math.cos(self.Jpos_rad[3])*(math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2]) - math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])) - self.Conf.l3*math.cos(self.Jpos_rad[1])*math.sin(self.Jpos_rad[0])*math.sin(self.Jpos_rad[3])
                self.Jacob[2,0]= 0
                self.Jacob[2,1]= math.cos(self.Jpos_rad[1])*(self.Conf.l1 + self.Conf.l2) - self.Conf.Rjoint2*math.cos(self.Jpos_rad[2])*math.sin(self.Jpos_rad[1]) + self.Conf.l3*math.cos(self.Jpos_rad[1])*math.cos(self.Jpos_rad[3]) - self.Conf.l3*math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])*math.sin(self.Jpos_rad[3]) 
                self.Jacob[2,2]= self.Conf.l3*math.cos(self.Jpos_rad[1])*math.cos(self.Jpos_rad[2])*math.sin(self.Jpos_rad[3]) - self.Conf.Rjoint2*math.cos(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])
                self.Jacob[2,3]= self.Conf.l3*math.cos(self.Jpos_rad[1])*math.cos(self.Jpos_rad[3])*math.sin(self.Jpos_rad[2]) - self.Conf.l3*math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[3])

                # Jacobiano moltiplicato per i pesi -> iterazione sulla matrice Jacobiana
                JacobW = numpy.dot(self.Jacob,self.Wq)

                # SVD
                U, s, V = numpy.linalg.svd(JacobW, full_matrices=False)
                s_min = numpy.amin(s)

                if s_min < self.Conf.eps:
                    self.Wq[0,0] = self.Conf.wq0s+(1-self.Conf.wq0s)*s_min/self.Conf.eps #peso per smorzare le velocità di giunto in singolarità
                    self.Wq[1,1] = self.Conf.wq0s+(1-self.Conf.wq0s)*s_min/self.Conf.eps #peso per smorzare le velocità di giunto in singolarità
                    self.Wq[2,2] = self.Conf.wq0s+(1-self.Conf.wq0s)*s_min/self.Conf.eps #peso per smorzare le velocità di giunto in singolarità
                    self.Wq[3,3] = self.Conf.wq0s+(1-self.Conf.wq0s)*s_min/self.Conf.eps #peso per smorzare le velocità di giunto in singolarità
            
                else:
                    self.Wq[0,0] = 1
                    self.Wq[1,1] = 1
                    self.Wq[2,2] = 1
                    self.Wq[3,3] = 1

                '''
                3.2. LIMITI dei ROM
                '''
                # aggiunta algoritmo
                for i, Jpos, Jmin, Jmax in zip(range(0,4), self.Jpos_rad*180/math.pi, self.Conf.Jmin, self.Conf.Jmax):
                    if self.dq_prec[i] >= 0:
                        self.dl[i] = Jmax-Jpos
                    else:
                        self.dl[i] = Jpos-Jmin
                    
                    if self.dl[i] < self.dol:
                        self.ul[i] = max(self.ul[i]-self.du, self.dl[i]/self.dol)
                    else:
                        self.ul[i] = min(self.ul[i]+self.du, 1)

                    self.Wq[i,i] = self.Conf.wq0s+(1-self.Conf.wq0s)*self.ul[i]
                    self.Conf.alpha = self.alpha0*(1-self.ul[i]**2)

                '''
                3.3 Aggiornamento e calcolo della variazione di giunto
                '''
                # aggiono il Jacobiano
                JacobW = numpy.dot(self.Jacob,self.Wq)
                # equazione per trovare la variazione di giunto da applicare
                temp = inv(numpy.dot(JacobW,JacobW.transpose())+self.Conf.alpha*numpy.eye(3))
                dq = numpy.dot(numpy.dot(numpy.dot(self.Wq,JacobW.transpose()),temp),dp.transpose())
                self.dq_prec = dq

                # update dei valori di giunto che voglio raggiungere
                self.Coord.Jdes[0:4] = self.Jpos_rad[0:4]*180/math.pi + dq*180/math.pi

                '''
                3.4. Aggiornamento valori di giunto
                '''
                self.Jpos_rad = self.Coord.Jdes*math.pi/180

                p_update = numpy.array([0.0, 0.0, 0.0]) 
                p_update[0] = math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*(self.Conf.l1+self.Conf.l2)-self.Conf.l3*math.sin(self.Jpos_rad[3])*(math.sin(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2])+math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2]))+self.Conf.Rjoint2*(math.sin(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0])-math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[1])*math.cos(self.Jpos_rad[2]))+self.Conf.l3*math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[3])*math.cos(self.Jpos_rad[1])
                p_update[1] = -self.Conf.Rjoint2*(math.cos(self.Jpos_rad[0])*math.sin(self.Jpos_rad[2])+math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2]))+self.Conf.l3*math.sin(self.Jpos_rad[3])*(math.cos(self.Jpos_rad[0])*math.cos(self.Jpos_rad[2])-math.sin(self.Jpos_rad[1])*math.sin(self.Jpos_rad[2])*math.sin(self.Jpos_rad[0]))+math.sin(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])*(self.Conf.l1+self.Conf.l2)+self.Conf.l3*math.cos(self.Jpos_rad[3])*math.sin(self.Jpos_rad[0])*math.cos(self.Jpos_rad[1])
                p_update[2] = self.Conf.Rjoint2*math.cos(self.Jpos_rad[1])*math.cos(self.Jpos_rad[2])+self.Conf.l3*math.cos(self.Jpos_rad[3])*math.sin(self.Jpos_rad[1])+math.sin(self.Jpos_rad[1])*(self.Conf.l1+self.Conf.l2)+self.Conf.l3*math.sin(self.Jpos_rad[2])*math.sin(self.Jpos_rad[3])*math.cos(self.Jpos_rad[1])

                # update errore che devo ridurre con le mie iterazioni (idealmente zero)
                dp = self.EndEff_des[0:3] -p_update

                # update del num di iterazioni ciclo while
                n = n+1
                if n >= self.Conf.it_max:
                    exit = True
                    print '************* Maximum number of iterations reached'

            # Verifico che la soluzione trovata rispetti i limiti di giunto altrimenti li limito all'estremo più vicino --> riporto errore
            for i, Jmin, Jmax in zip(range(0,4), self.Conf.Jmin, self.Conf.Jmax):
                if Jmin+5 > self.Coord.Jdes[i]:
                    winsound.Beep(440, 500) # frequency, duration[ms]
                    print 'J%d close to lower limit (%f)' % (i+1, self.Coord.Jdes[i])
                    #self.Coord.Jdes[i] = Jmin+5
                    self.Coord.change_dir_count[i] = self.Coord.change_dir_count[i]+1
                    self.Coord.Jdes[i] = Jmin+5

                elif self.Coord.Jdes[i]> Jmax-5:
                    winsound.Beep(440, 500) # frequency, duration[ms]
                    print 'J%d close to upper limit (%f)' % (i+1, self.Coord.Jdes[i])
                    #self.Coord.Jdes[i] = Jmax-5
                    self.Coord.change_dir_count[i] = self.Coord.change_dir_count[i]+1
                    self.Coord.Jdes[i] = Jmax-5
                
                if self.Coord.change_dir_count[i] > 2:
                    #print 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                    #print i
                    self.Coord.change_dir_count = [0]*5
                    #self.Conf.CtrlEnable =  False
                    self.p0_check = self.Coord.p0
                    #print '+++++++++++ ', self.p0_check

            """
            # Mappo lo spostamento di posizione in spostamento di velocità richiesto ai giunti
            # calcolo delta in gradi che voglio muovere sui vari motori
            self.Coord.Jv = ((self.Coord.Jdes-self.Coord.Jpos)/self.Conf.ctrl_t)*1.5
            for i in range(0,5):
                if abs(self.Coord.Jv[i]) < 1:
                    # print 'Jv = 0', i, self.Coord.Jv[i]
                    self.Coord.Jv[i] = 1
            """
            " Check no repentine change of joints value!"
            
            diff = [x - y for x, y in zip(self.Coord.JposPrec, self.Coord.Jpos)]

            for i in diff:
                if abs(i) > self.Conf.MaxDegDispl:
                    self.Coord.Jpos = self.Coord.JposPrec

            self.Coord.JposPrec = self.Coord.Jpos


            ''' set Jpos as the starting point (a mano)'''
            self.Coord.Jpos = self.Coord.Jdes
            # print "Jdes: ", self.Coord.Jpos

            # Faccio update giunti dopo calcolo IK
            #self.Coord.joint_update = True
            #self.Coord.Jupdate = [True, True, True, True, True]
            
            '''
            for i in range(0, len(self.Coord.Jupdate)):
                #if self.Coord.Jpos[i] != self.Coord.Jdes[i]:
                
                self.Coord.Jupdate[i] = True
            '''
            # Per discriminare cosa muovere
            #self.Coord.Jpos - self.Coord.Jdes

            # SOLO PER VERSIONE ATTUALE #CULO
            # self.Coord.Jpos = self.Coord.Jdes

            
            # monitor variables
            file_p0_.append(self.Coord.p0[0])
            file_p0_.append(self.Coord.p0[1])
            file_p0_.append(self.Coord.p0[2])
            file_p0_.append(self.Coord.p0[3])
            file_EndEff0.append(self.Coord.EndEff0[0])
            file_EndEff0.append(self.Coord.EndEff0[1])
            file_EndEff0.append(self.Coord.EndEff0[2])
            file_EndEff0.append(self.Coord.EndEff0[3])
            file_EndEff_des.append(self.EndEff_des[0])
            file_EndEff_des.append(self.EndEff_des[1])
            file_EndEff_des.append(self.EndEff_des[2])
            file_EndEff_des.append(self.EndEff_des[3])
            file_Jpos.append(self.Coord.Jpos[0])
            file_Jpos.append(self.Coord.Jpos[1])
            file_Jpos.append(self.Coord.Jpos[2])
            file_Jpos.append(self.Coord.Jpos[3])
            file_Jpos.append(self.Coord.Jpos[4])
            file_Jdes.append(self.Coord.Jpos[0])
            file_Jdes.append(self.Coord.Jpos[1])
            file_Jdes.append(self.Coord.Jpos[2])
            file_Jdes.append(self.Coord.Jpos[3])
            file_Jdes.append(self.Coord.Jpos[4])
            
        else:
            self.Coord.Jv = [1, 1, 1, 1, 1]


    '''
    def DebugCtrl(self):

        self.Coord.Jdes = self.Coord.Jdebug[self.i_cnt_debug,:]
        self.i_cnt_debug += 4
        if self.i_cnt_debug >= 1082:
            self.i_cnt_debug = 0


        self.Coord.joint_update = True
    '''

    def terminate(self):
        self.running = False
        
        # apro file per sccrittura dati
        text_file_EndEff0 = open("Output_EndEff0.txt", "w")
        text_file_EndEff_des = open("Output_EndEff_des.txt", "w")
        text_file_Jpos = open("Output_Jpos.txt", "w")
        text_file_Jdes = open("Output_Jdes.txt", "w")
        text_file_p0_ = open("Output_p0.txt", "w")

        # scrivo variabili sui file prima di chiudere
        text_file_EndEff0.write("\n{0}".format(file_EndEff0))
        text_file_EndEff_des.write("\n{0}".format(file_EndEff_des))
        text_file_Jpos.write("\n{0}".format(file_Jpos))
        text_file_Jdes.write("\n{0}".format(file_Jdes))
        text_file_p0_.write("\n{0}".format(file_p0_))


