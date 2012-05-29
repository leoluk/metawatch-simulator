# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Apr 10 2012)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"MetaWatch Remote Protocol Simulator 0.1", pos = wx.DefaultPosition, size = wx.Size( 841,463 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BACKGROUND ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		
		bMainSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizer12 = wx.BoxSizer( wx.VERTICAL )
		
		bScreenSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_SideA = wx.Button( self, wx.ID_ANY, u"A", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.m_SideA.SetMinSize( wx.Size( 27,-1 ) )
		
		bSizer2.Add( self.m_SideA, 0, wx.ALL, 5 )
		
		self.m_SideB = wx.Button( self, wx.ID_ANY, u"B", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.m_SideB.SetMinSize( wx.Size( 27,-1 ) )
		
		bSizer2.Add( self.m_SideB, 0, wx.ALL, 5 )
		
		self.m_SideC = wx.Button( self, wx.ID_ANY, u"C", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.m_SideC.SetMinSize( wx.Size( 27,-1 ) )
		
		bSizer2.Add( self.m_SideC, 0, wx.ALL, 5 )
		
		
		bScreenSizer.Add( bSizer2, 0, 0, 5 )
		
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.DOUBLE_BORDER|wx.TAB_TRAVERSAL )
		self.m_panel1.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.m_panel1.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.m_panel1.SetMinSize( wx.Size( 96,96 ) )
		
		bSizer3.Add( self.m_panel1, 0, wx.ALL, 5 )
		
		
		bScreenSizer.Add( bSizer3, 0, 0, 5 )
		
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_SideD = wx.Button( self, wx.ID_ANY, u"D", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.m_SideD.SetMinSize( wx.Size( 27,-1 ) )
		
		bSizer5.Add( self.m_SideD, 0, wx.ALL, 5 )
		
		self.m_SideE = wx.Button( self, wx.ID_ANY, u"E", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.m_SideE.SetMinSize( wx.Size( 27,-1 ) )
		
		bSizer5.Add( self.m_SideE, 0, wx.ALL, 5 )
		
		self.m_SideF = wx.Button( self, wx.ID_ANY, u"F", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.m_SideF.SetMinSize( wx.Size( 27,-1 ) )
		
		bSizer5.Add( self.m_SideF, 0, wx.ALL, 5 )
		
		
		bScreenSizer.Add( bSizer5, 0, 0, 5 )
		
		bSizer10 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_battWarning = wx.Button( self, wx.ID_ANY, u"Low battery warning", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.m_battWarning, 0, wx.EXPAND|wx.ALL, 5 )
		
		self.m_btWarning = wx.Button( self, wx.ID_ANY, u"Bluetooth off warning", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.m_btWarning, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_resetWatch = wx.Button( self, wx.ID_ANY, u"Reset watch state", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.m_resetWatch, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		bScreenSizer.Add( bSizer10, 0, wx.EXPAND, 5 )
		
		bSizer11 = wx.BoxSizer( wx.VERTICAL )
		
		m_watchModeChoices = [ u"Idle", u"Application", u"Notification" ]
		self.m_watchMode = wx.RadioBox( self, wx.ID_ANY, u"Watch mode", wx.DefaultPosition, wx.DefaultSize, m_watchModeChoices, 1, wx.RA_SPECIFY_COLS )
		self.m_watchMode.SetSelection( 0 )
		self.m_watchMode.Enable( False )
		
		bSizer11.Add( self.m_watchMode, 0, wx.ALL, 5 )
		
		self.m_manualModeSet = wx.CheckBox( self, wx.ID_ANY, u"Manual mode", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer11.Add( self.m_manualModeSet, 0, wx.ALL, 5 )
		
		self.m_LEDNotice = wx.StaticText( self, wx.ID_ANY, u"LED", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.m_LEDNotice.Wrap( -1 )
		self.m_LEDNotice.SetFont( wx.Font( 11, 74, 90, 92, False, "Tahoma" ) )
		self.m_LEDNotice.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BACKGROUND ) )
		self.m_LEDNotice.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_SCROLLBAR ) )
		
		bSizer11.Add( self.m_LEDNotice, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_vibrateNotice = wx.StaticText( self, wx.ID_ANY, u"Vibrate", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE|wx.ALIGN_LEFT )
		self.m_vibrateNotice.Wrap( -1 )
		self.m_vibrateNotice.SetFont( wx.Font( 11, 74, 90, 92, False, "Tahoma" ) )
		self.m_vibrateNotice.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BACKGROUND ) )
		self.m_vibrateNotice.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_SCROLLBAR ) )
		
		bSizer11.Add( self.m_vibrateNotice, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer11.AddSpacer( ( 0, 23), 1, wx.EXPAND, 5 )
		
		
		bScreenSizer.Add( bSizer11, 0, wx.EXPAND, 5 )
		
		
		bSizer12.Add( bScreenSizer, 0, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		fgSizer2 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer2.SetFlexibleDirection( wx.BOTH )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"COM port:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE )
		self.m_staticText5.Wrap( -1 )
		fgSizer2.Add( self.m_staticText5, 0, wx.ALIGN_CENTER|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_comPort = wx.TextCtrl( self, wx.ID_ANY, u"COM8", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		fgSizer2.Add( self.m_comPort, 0, wx.ALL, 5 )
		
		self.m_serialSetup = wx.Button( self, wx.ID_ANY, u"Setup...", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2.Add( self.m_serialSetup, 0, wx.ALL, 5 )
		
		
		bSizer12.Add( fgSizer2, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_openConnection = wx.Button( self, wx.ID_ANY, u"&Open connection", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.m_openConnection, 0, wx.ALL, 5 )
		
		self.m_closeConnection = wx.Button( self, wx.ID_ANY, u"&Close connection", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.m_closeConnection, 0, wx.ALL, 5 )
		
		self.m_debug = wx.CheckBox( self, wx.ID_ANY, u"Debug output", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.m_debug, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_saveLog = wx.Button( self, wx.ID_ANY, u"Save log...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.m_saveLog, 0, wx.ALL, 5 )
		
		
		bSizer12.Add( bSizer9, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_log = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2 )
		bSizer12.Add( self.m_log, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bMainSizer.Add( bSizer12, 1, wx.EXPAND, 5 )
		
		p_Sizer13 = wx.BoxSizer( wx.VERTICAL )
		
		p_Sizer13.SetMinSize( wx.Size( 350,-1 ) ) 
		# WARNING: wxPython code generation isn't supported for this widget yet.
		self.m_pg = wx.Window( self )
		p_Sizer13.Add( self.m_pg, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		bMainSizer.Add( p_Sizer13, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( bMainSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.MainFrameOnClose )
		self.m_SideA.Bind( wx.EVT_BUTTON, self.m_OnSideButtonClick )
		self.m_SideB.Bind( wx.EVT_BUTTON, self.m_OnSideButtonClick )
		self.m_SideC.Bind( wx.EVT_BUTTON, self.m_OnSideButtonClick )
		self.m_SideD.Bind( wx.EVT_BUTTON, self.m_OnSideButtonClick )
		self.m_SideE.Bind( wx.EVT_BUTTON, self.m_OnSideButtonClick )
		self.m_SideF.Bind( wx.EVT_BUTTON, self.m_OnSideButtonClick )
		self.m_resetWatch.Bind( wx.EVT_BUTTON, self.m_resetWatchOnButtonClick )
		self.m_manualModeSet.Bind( wx.EVT_CHECKBOX, self.m_manualModeSetOnCheckBox )
		self.m_serialSetup.Bind( wx.EVT_BUTTON, self.m_serialSetupOnButtonClick )
		self.m_openConnection.Bind( wx.EVT_BUTTON, self.m_openConnectionOnButtonClick )
		self.m_closeConnection.Bind( wx.EVT_BUTTON, self.m_closeConnectionOnButtonClick )
		self.m_debug.Bind( wx.EVT_CHECKBOX, self.m_debugOnCheckBox )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def MainFrameOnClose( self, event ):
		event.Skip()
	
	def m_OnSideButtonClick( self, event ):
		event.Skip()
	
	
	
	
	
	
	def m_resetWatchOnButtonClick( self, event ):
		event.Skip()
	
	def m_manualModeSetOnCheckBox( self, event ):
		event.Skip()
	
	def m_serialSetupOnButtonClick( self, event ):
		event.Skip()
	
	def m_openConnectionOnButtonClick( self, event ):
		event.Skip()
	
	def m_closeConnectionOnButtonClick( self, event ):
		event.Skip()
	
	def m_debugOnCheckBox( self, event ):
		event.Skip()
	

