import wx
import Interface

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
        aBitmap = wx.Image(name="LINEViewer_logo.png").ConvertToBitmap()
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splashDuration = 1000
        wx.SplashScreen.__init__(self, aBitmap, splashStyle,
                                 splashDuration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        wx.Yield()

    def OnExit(self, event):
        self.Hide()
        MyFrame = Interface.MainFrame()
        app.SetTopWindow(MyFrame)
        MyFrame.Show(True)
        event.Skip()

# Opens the GUI if script is run directly
if __name__ == "__main__":
    app = StartLINEViewer()
    app.MainLoop()
