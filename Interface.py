import wx
import PanelData
import PanelSpecs
import PanelVisualize
from Analysis import Results


class MainFrame(wx.Frame):

    """
    Initiation of MainFrame with PanelData, PanelOption and PanelSpecs
    """

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="LINEViewer 0.1",
                          pos=(0, 0), size=(1200, 1000))
        # self.Maximize(True)

        # Default variables
        self.Data = type('Data', (object,), {})()
        self.Data.DirPath = ''
        self.Data.Filenames = []
        self.Data.Datasets = []
        self.Data.Results = Results()

        # Panel: MainFrame
        MainPanel = wx.Panel(self, wx.ID_ANY)

        # Specify BoxSizer
        sizerMainH = wx.BoxSizer(wx.HORIZONTAL)

        # Panel: Data
        PanelDataInput = PanelData.Selecter(MainPanel, self.Data)
        sizerMainH.Add(PanelDataInput, 0, wx.EXPAND)

        # Panel: Visualization
        self.PanelOption = wx.Notebook(MainPanel, wx.ID_ANY,
                                       style=wx.NB_TOP, size=(1000, 1000))
        self.Data.GFPDetailed = PanelVisualize.GFPDetailed(
            self.PanelOption, self.Data)
        self.Data.EpochMarkerDetail = PanelVisualize.EpochMarkerDetail(
            self.PanelOption, self.Data)
        self.Data.GFPSummary = PanelVisualize.GFPSummary(
            self.PanelOption, self.Data)

        self.PanelOption.AddPage(self.Data.GFPSummary, 'GFP - Summary')
        self.PanelOption.AddPage(self.Data.GFPDetailed, 'GFP - Detailed')
        self.PanelOption.AddPage(
            self.Data.EpochMarkerDetail, 'Epoch - Marker Detail')
        self.Data.GFPSummary.SetFocus()
        sizerMainH.Add(self.PanelOption, wx.ID_ANY, wx.EXPAND)

        # Panel: Specs
        PanelSpecsInput = PanelSpecs.Specification(MainPanel, self.Data)
        sizerMainH.Add(PanelSpecsInput, 0, wx.EXPAND)

        # Setup MainFrame
        MainPanel.SetSizer(sizerMainH)
        self.Show(True)

        # Specification of events
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)
        PanelDataInput.SetFocus()

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
