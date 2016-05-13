# Part of the LINEViewer library
# Copyright (C) 2016 Michael Notter
# Distributed under the terms of the GNU General Public License (GPL).

from LINEViewer import StartLINEViewer

# version info for LINEViewer
__version__ = '0.2.02'
__package__ = 'lineviewer'
__license__ = 'GNU GPLv3 (or more recent equivalent)'
__author__ = 'Michael Notter'
__author_email__ = 'michaelnotter@hotmail.com'
__downloadUrl__ = 'https://github.com/miykael/LINEViewer/releases/'
__url__ = 'https://github.com/miykael/LINEViewer'


# To start the gui
def gui():
    app = StartLINEViewer()
    app.MainLoop()
