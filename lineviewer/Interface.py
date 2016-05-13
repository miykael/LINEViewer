import wx
import PanelData
import PanelSpecs
import PanelVisualize
from Analysis import Results
from os.path import join, dirname, abspath


class MainFrame(wx.Frame):

    """
    Initiation of MainFrame with PanelData, PanelOption and PanelSpecs
    """

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="LINEViewer 0.2.02",
                          pos=(0, 0), size=(1200, 1000))
        logopath = join(
            dirname(abspath(__file__)), 'static', 'favicon_256.ico')
        self.SetIcon(wx.Icon(logopath, wx.BITMAP_TYPE_ICO))

        # Default variables
        self.Data = type('Data', (object,), {})()
        self.Data.VERSION = '0.2.02'
        self.Data.DirPath = ''
        self.Data.Filenames = []
        self.Data.Datasets = []
        self.Data.Results = Results()
        self.Data.Results.updateAnalysis = False

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
        self.Data.ERPSummary = PanelVisualize.ERPSummary(
            self.PanelOption, self.Data)
        self.Data.GFPDetail = PanelVisualize.GFPDetail(
            self.PanelOption, self.Data)
        self.Data.EpochsDetail = PanelVisualize.EpochsDetail(
            self.PanelOption, self.Data)
        self.Data.Overview = PanelVisualize.Overview(self.PanelOption,
                                                     self.Data)
        self.Data.GFPSummary = PanelVisualize.GFPSummary(
            self.PanelOption, self.Data)

        self.PanelOption.AddPage(self.Data.Overview, 'Overview')
        self.PanelOption.AddPage(self.Data.GFPSummary, 'GFP - Summary')
        self.PanelOption.AddPage(self.Data.GFPDetail, 'GFP - Detail')
        self.PanelOption.AddPage(self.Data.ERPSummary,
                                 'ERP - Summary')
        self.PanelOption.AddPage(self.Data.EpochsDetail,
                                 'Epochs - Detail')
        self.Data.GFPSummary.SetFocus()
        sizerMainH.Add(self.PanelOption, wx.ID_ANY, wx.EXPAND)

        # Panel: Specs
        self.PanelSpecsInput = PanelSpecs.Specification(MainPanel, self.Data)
        sizerMainH.Add(self.PanelSpecsInput, 0, wx.EXPAND)

        # Setup MainFrame
        MainPanel.SetSizer(sizerMainH)
        self.Show(True)

        # Specification of events
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.notebookSelected)
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

    def notebookSelected(self, event):
        """Checks if Analysis needs to be rerun to update a Notebook channel"""

        if self.Data.Datasets != []:
            if self.Data.Results.updateAnalysis:
                self.Data.Results.updateAnalysis = False
                self.Data.Results.updateEpochs(self.Data)
