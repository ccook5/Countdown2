#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Counts down to a specified time

author: Chris Cook
website: sourceforge.net 
last edited: January 2012

icon from http://live.gnome.org/AlarmClock/Blueprints/BetterIcons

"""

import sys
from datetime import *
from PyQt5 import QtCore, QtWidgets, QtGui, QtNetwork, QtWebKit

class SettingsWindow(QtWidgets.QWidget):

	def __init__(self, p):
		super(SettingsWindow, self).__init__()
		
		self.start_time_label     = QtWidgets.QLabel("Set the Start Time")
		self.target_time_label    = QtWidgets.QLabel("Set the End Time")
		
		msg_lbl_text  = "Set the display message<br /><br />"
		msg_lbl_text += "<i>{:d} = hours, {:02d} = minutes,<br /> ':' is displayed as is,<br />"
		msg_lbl_text += "basic HTML and inline CSS allowed. <br />See Qt4 Documentation for more info.</i>"
		
		self.message_label        = QtWidgets.QLabel(msg_lbl_text)
		
		self.start_time_tbox      = QtWidgets.QTimeEdit(QtCore.QTime(10,00,00))
		self.target_time_tbox     = QtWidgets.QTimeEdit(QtCore.QTime(10,30,00))
		
		self. start_time_tbox.setDisplayFormat("hh:mm:ss")
		self.target_time_tbox.setDisplayFormat("hh:mm:ss")

		msg  = "<span style='font-size: 15px'>Service starts in : </span>"
		msg += "<span style='font-size: 30px;'>"
		msg += "{:d}:{:02d}"
		msg += "</span>"
		
		self.message_txtbox       = QtWidgets.QTextEdit()
		self.message_txtbox.setPlainText(msg)
		
		self.save_settings_button = QtWidgets.QPushButton("Save Settings")
		self.close_button         = QtWidgets.QPushButton("Close Window")
		
		self.save_settings_button.clicked.connect(p.writeSettings)
		self.close_button.clicked.connect(self.hide)

		self.layout = QtWidgets.QGridLayout()
		
		self.layout.addWidget(self.start_time_label,     0, 0)
		self.layout.addWidget(self.start_time_tbox,      0, 2)
		
		self.layout.addWidget(self.target_time_label,    1, 0)
		self.layout.addWidget(self.target_time_tbox,     1, 2)

		self.layout.addWidget(self.message_label,        3, 0)
		
		self.layout.addWidget(self.message_txtbox,       3, 2)

		self.layout.addWidget(self.save_settings_button, 5, 0)
		self.layout.addWidget(self.close_button,         5, 2)
		
		self.setLayout(self.layout)
		self.setWindowTitle("Settings");

		self.resize(600,250)
#		self.show()
		

class MainWindow(QtWidgets.QLabel):

	def __init__(self):
#		print("Creating MainWindow instance...")
		super(MainWindow, self).__init__()

		self.SettingsWindow = SettingsWindow(self)
#		self.SettingsWindow.showNormal()
		
		self.readSettings()
		
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
		self.setMargin     (5)
		self.show          ()
		self.setText       ("")
		
		QtWidgets.QApplication.desktop().screenCountChanged.connect(self.screenCountChangedSlot)
		self.screenCountChangedSlot(0)
		
		width = len(self.SettingsWindow.message_txtbox.toPlainText()) * 2
		
		self.resize         (width, 50)

		self.restoreAction  = QtWidgets.QAction(self.tr("&Restore"),  self)
		self.settingsAction = QtWidgets.QAction(self.tr("&Settings"), self)
		self.quitAction     = QtWidgets.QAction(self.tr("&Quit"),     self)
		
		self.trayIconMenu   = QtWidgets.QMenu  (self)

		self.trayIcon       = QtWidgets.QSystemTrayIcon(QtGui.QIcon('c:\program files\countdown\icon.png'), self)

		self. restoreAction.triggered.connect(self.showNormal)
		self.settingsAction.triggered.connect(self.SettingsWindow.showNormal)
		self.    quitAction.triggered.connect(self.trayIcon.hide)
		self.    quitAction.triggered.connect(QtWidgets.qApp.quit)

		self.trayIconMenu.addAction(self.restoreAction)
		self.trayIconMenu.addSeparator()
		self.trayIconMenu.addAction(self.settingsAction)
		self.trayIconMenu.addSeparator()
		self.trayIconMenu.addAction(self.quitAction)
		
		self.trayIcon.setContextMenu(self.trayIconMenu)
		
		self.trayIcon.show()

		self.setWindowTitle('countdown')
		self.setWindowIcon(QtGui.QIcon('c:\program files\countdown\icon.png'))

		self.timer = QtCore.QTimer(self);
		self.timer.timeout.connect(self.timerEvent);
		self.timer.start(200); # 1000 miliseconds = 1 second
		
		self.timerEvent();
		
	def __del__(self):
		self.writeSettings()

	def timerEvent(self):
		t_now = datetime.time(datetime.now())

		if t_now >= self.SettingsWindow.start_time_tbox.time() and t_now <= self.SettingsWindow.target_time_tbox.time():
			hours = self.SettingsWindow.target_time_tbox.time().hour() - t_now.hour
			mins = (60 * hours)
			mins += (self.SettingsWindow.target_time_tbox.time().minute() - t_now.minute) - 1
			secs = 59 - -(self.SettingsWindow.target_time_tbox.time().second() - t_now.second)
			
		
			self.setText(self.SettingsWindow.message_txtbox.toPlainText().format(mins,secs))
#			width = self.SettingsWindow.message_txtbox.document().size().width()
			
#			print(width)
		
			self.resize         (280, 50)
			self.showNormal()
		else:
			self.hide()
			self.setText("")

	def screenCountChangedSlot(self, numScreens):
		print("Number of screens has changed...")
		print("There are now {num_screens} screen(s)/Display(s)".format(num_screens = QtWidgets.QDesktopWidget().screenCount()))
		
		if QtWidgets.QDesktopWidget().screenCount() == 2:
			# 0 = primary screen, 1 = secondary
			screenres = QtWidgets.QApplication.desktop().screenGeometry(1)
			self.move(QtCore.QPoint(screenres.x(), screenres.y()));
		else:
			self.move(0,0)
			
	def closeEvent(self, event):
#		print("Closing...")
		self.writeSettings()
		self.window().hide()
		self.trayIcon.hide()

	def readSettings(self):
#		print("Reading settings from registry...")
		settings = QtCore.QSettings("ChrisCook", "Countdown")
		
		msg  = "<span style='font-size: 15px'>Service starts in : </span>"
		msg += "<span style='font-size: 30px;'>"
		msg += "{:d}:{:02d}"
		msg += "</span>"
		
		self.SettingsWindow.message_txtbox.setPlainText(settings.value("formatted_message", msg))
		
		target_time_str  = settings.value("target_time",       "23:30:00")
		start_time_str   = settings.value("start_time",        "10:00:00")
		
		self.SettingsWindow.target_time_tbox.setTime(QtCore.QTime.fromString(target_time_str, "HH:mm:ss"))
		self.SettingsWindow.start_time_tbox.setTime(QtCore.QTime.fromString(start_time_str, "HH:mm:ss"))
		
	def writeSettings(self):
#		print("Writing settings to registry...")
		settings = QtCore.QSettings("ChrisCook", "Countdown")
		
		settings.setValue("formatted_message", self.SettingsWindow.message_txtbox.toPlainText())
		settings.setValue("target_time",       self.SettingsWindow.target_time_tbox.time().toString("HH:mm:ss"))
		settings.setValue("start_time",        self.SettingsWindow.start_time_tbox.time().toString("HH:mm:ss"))
		settings.sync()


def main():
    app = QtWidgets.QApplication(sys.argv)
    w   = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
