# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Dec 21 2016)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class BridgeJoystickWin
###########################################################################

class BridgeJoystickWin ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"BridgeJoystick V0.1", pos = wx.DefaultPosition, size = wx.Size( 1002,536 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.Size( 1002,-1 ), wx.Size( -1,-1 ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		self.m_statusBar1 = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menuItem1 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Connect"+ u"\t" + u"Ctrl+S", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menuItem1.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_GO_FORWARD, wx.ART_MENU ) )
		self.m_menu1.AppendItem( self.m_menuItem1 )
		
		self.m_menuItem4 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Clear"+ u"\t" + u"Ctrl+C", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.AppendItem( self.m_menuItem4 )
		
		self.m_menu1.AppendSeparator()
		
		self.m_menuItem2 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Close"+ u"\t" + u"Ctrl+Q", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menuItem2.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_QUIT, wx.ART_MENU ) )
		self.m_menu1.AppendItem( self.m_menuItem2 )
		
		self.m_menubar1.Append( self.m_menu1, u"File" ) 
		
		self.m_menu2 = wx.Menu()
		self.m_menuItem3 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Preferences"+ u"\t" + u"Ctrl+P", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menuItem3.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_REPORT_VIEW, wx.ART_MENU ) )
		self.m_menu2.AppendItem( self.m_menuItem3 )
		
		self.m_menubar1.Append( self.m_menu2, u"Tools" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer41 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Mode", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )
		bSizer41.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.lbl_Mode = wx.StaticText( self, wx.ID_ANY, u"○", wx.DefaultPosition, wx.Size( -1,-1 ), wx.ST_NO_AUTORESIZE )
		self.lbl_Mode.Wrap( -1 )
		self.lbl_Mode.SetFont( wx.Font( 18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.lbl_Mode.SetForegroundColour( wx.Colour( 0, 255, 128 ) )
		
		bSizer41.Add( self.lbl_Mode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Save Position", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		bSizer41.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.lbl_savePos = wx.StaticText( self, wx.ID_ANY, u"○", wx.DefaultPosition, wx.DefaultSize, wx.ST_NO_AUTORESIZE )
		self.lbl_savePos.Wrap( -1 )
		self.lbl_savePos.SetFont( wx.Font( 18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.lbl_savePos.SetForegroundColour( wx.Colour( 128, 255, 128 ) )
		
		bSizer41.Add( self.lbl_savePos, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Go To Saved Position", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )
		bSizer41.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.lbl_Goto = wx.StaticText( self, wx.ID_ANY, u"○", wx.DefaultPosition, wx.DefaultSize, wx.ST_NO_AUTORESIZE )
		self.lbl_Goto.Wrap( -1 )
		self.lbl_Goto.SetFont( wx.Font( 18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.lbl_Goto.SetForegroundColour( wx.Colour( 128, 255, 128 ) )
		
		bSizer41.Add( self.lbl_Goto, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		bSizer7.Add( bSizer41, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.lbl_alarm = wx.StaticText( self, wx.ID_ANY, u"Alarm", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.lbl_alarm.Wrap( -1 )
		self.lbl_alarm.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		bSizer5.Add( self.lbl_alarm, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		bSizer7.Add( bSizer5, 1, wx.EXPAND, 5 )
		
		
		bSizer4.Add( bSizer7, 1, wx.EXPAND, 5 )
		
		sbSizer21 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Activities" ), wx.HORIZONTAL )
		
		
		sbSizer21.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.button_loadPatient = wx.Button( sbSizer21.GetStaticBox(), wx.ID_ANY, u"Settings", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer21.Add( self.button_loadPatient, 0, wx.ALL, 5 )
		
		self.button_StartCtrl = wx.Button( sbSizer21.GetStaticBox(), wx.ID_ANY, u"Ctrl", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer21.Add( self.button_StartCtrl, 0, wx.ALL, 5 )
		
		self.butt_StopControl = wx.Button( sbSizer21.GetStaticBox(), wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer21.Add( self.butt_StopControl, 0, wx.ALL, 5 )
		
		
		sbSizer21.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		bSizer4.Add( sbSizer21, 0, wx.EXPAND, 5 )
		
		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
		
		
		bSizer4.Add( bSizer3, 0, wx.EXPAND, 5 )
		
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		self.show_terminal = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		self.show_terminal.SetForegroundColour( wx.Colour( 255, 255, 255 ) )
		self.show_terminal.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BACKGROUND ) )
		
		bSizer8.Add( self.show_terminal, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer4.Add( bSizer8, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		bSizer2.Add( bSizer4, 1, wx.EXPAND, 5 )
		
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_panel5 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,100 ), wx.TAB_TRAVERSAL )
		self.m_panel5.SetMaxSize( wx.Size( -1,100 ) )
		
		bSizer6.Add( self.m_panel5, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.exo3d_container = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer6.Add( self.exo3d_container, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_panel6 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,100 ), wx.TAB_TRAVERSAL )
		self.m_panel6.SetMaxSize( wx.Size( -1,100 ) )
		
		bSizer6.Add( self.m_panel6, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		bSizer2.Add( bSizer6, 1, wx.EXPAND, 5 )
		
		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"2D view" ), wx.VERTICAL )
		
		self.exo_piano1 = wx.Panel( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sbSizer2.Add( self.exo_piano1, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.exo_piano2 = wx.Panel( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sbSizer2.Add( self.exo_piano2, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.exo_piano3 = wx.Panel( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sbSizer2.Add( self.exo_piano3, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		bSizer2.Add( sbSizer2, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer2 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.close )
		self.Bind( wx.EVT_MENU, self.connect_command, id = self.m_menuItem1.GetId() )
		self.Bind( wx.EVT_MENU, self.exit, id = self.m_menuItem2.GetId() )
		self.Bind( wx.EVT_MENU, self.preferences, id = self.m_menuItem3.GetId() )
		self.button_loadPatient.Bind( wx.EVT_BUTTON, self.loadPatient_command )
		self.button_StartCtrl.Bind( wx.EVT_BUTTON, self.enableCtrl_command )
		self.butt_StopControl.Bind( wx.EVT_BUTTON, self.disableCtrl_command )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def close( self, event ):
		event.Skip()
	
	def connect_command( self, event ):
		event.Skip()
	
	def exit( self, event ):
		event.Skip()
	
	def preferences( self, event ):
		event.Skip()
	
	def loadPatient_command( self, event ):
		event.Skip()
	
	def enableCtrl_command( self, event ):
		event.Skip()
	
	def disableCtrl_command( self, event ):
		event.Skip()
	

