import wx
import Analysis
import PanelData
import PanelSpecs
import PanelVisualize


class MainFrame(wx.Frame):

    """
    Initiation of MainFrame with PanelData, PanelOption and ButtonStart
    """

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="LINEViewer 0.1",
                          pos=(0, 0), size=(1200, 1000))
        # self.Maximize(True)

        # Default variables
        self.fileDirectory = ''
        self.Files = []
        self.Datasets = []
        self.Results = Analysis.Results(self)

        # Panel: MainFrame
        self.panel = wx.Panel(self, wx.ID_ANY)

        # Specify BoxSizer
        sizerMainH = wx.BoxSizer(wx.HORIZONTAL)

        # Panel: Data
        self.PanelData = PanelData.Selecter(self.panel, self)
        sizerMainH.Add(self.PanelData, 0, wx.EXPAND)

        # Panel: Visualization
        self.PanelOption = wx.Notebook(self.panel, wx.ID_ANY,
                                       style=wx.NB_TOP, size=(1000, 1000))
        self.GFPDetailed = PanelVisualize.GFPDetailed(self.PanelOption, self)
        self.GFPSummary = PanelVisualize.GFPSummary(self.PanelOption, self)
        self.PanelOption.AddPage(self.GFPSummary, 'GFP - Summary')
        self.PanelOption.AddPage(self.GFPDetailed, 'GFP - Detailed')
        self.GFPSummary.SetFocus()
        sizerMainH.Add(self.PanelOption, wx.ID_ANY, wx.EXPAND)

        # Panel: Specs
        self.PanelSpecs = PanelSpecs.Specification(self.panel, self)
        sizerMainH.Add(self.PanelSpecs, 0, wx.EXPAND)

        # Setup MainFrame
        self.panel.SetSizer(sizerMainH)
        self.Show(True)

        # Specification of events
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)
        self.PanelData.SetFocus()

        # MenuBar
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X",
                             "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.onClose, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About",
                              "Information about LINEViewer")
        self.Bind(wx.EVT_MENU, self.onAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)

    def onKeyDown(self, event):
        """Key event handler if key is pressed within frame"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:  # If ESC is pressed
            self.onClose(event)
        else:
            event.Skip()

    def onAbout(self, event):
        """Show about message when About Menu opened"""
        dlg = wx.MessageDialog(
            self,
            "For more Information about LINEViewer, go to " +
            "https://github.com/mnotter/LINEViewer",
            "About LINEViewer", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

    def onClose(self, event):
        """Show exit message when MainFrame gets closed"""
        dlg = wx.MessageDialog(
            self, "Do you really want to close LINEViewer?", "Exit LINEViewer",
            wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_OK:
            self.DestroyChildren()
            self.Destroy()
        event.Skip()
