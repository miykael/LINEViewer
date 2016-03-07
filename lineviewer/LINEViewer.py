import wx
import Interface
from os.path import join, dirname, abspath

"""
Start LINEViewer and open the GUI
"""


class StartLINEViewer(wx.App):

    """Calls LINEViewer Splash Screen"""

    def OnInit(self):
        LINEViewerSplash = LINEViewerSplashScreen()
        LINEViewerSplash.Show()
        return True


class LINEViewerSplashScreen(wx.SplashScreen):

    """Opens LINEViewer Splash Screen and after exit starts LINEViewer"""

    def __init__(self, parent=None):
        logopath = join(
            dirname(abspath(__file__)), 'static', 'LINEViewer_logo.png')
        aBitmap = wx.Image(name=logopath).ConvertToBitmap()
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splashDuration = 1000
        wx.SplashScreen.__init__(self, aBitmap, splashStyle,
                                 splashDuration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        wx.Yield()

    def OnExit(self, event):
        self.Hide()
        MyFrame = Interface.MainFrame()
        MyFrame.Show(True)
        event.Skip()
