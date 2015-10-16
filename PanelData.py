import os
import wx
import numpy as np
from FileHandler import ReadBDF, SaveH5


class Selecter(wx.Panel):

    """
    SOME TEXT
    """

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, size=(200, 1000),
                          style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data

        # Panel: Data Handler
        PanelDataHandler = wx.Panel(self, wx.ID_ANY)
        sizerPanelDataHandler = wx.BoxSizer(wx.VERTICAL)

        # Text: Load Dataset
        sizerPanelDataHandler.AddSpacer(2)
        TxtDataset = wx.StaticText(PanelDataHandler,
                                   wx.ID_ANY, style=wx.CENTRE,
                                   label=" Datasets Loaded")
        TxtDataset.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerPanelDataHandler.Add(TxtDataset, 0, wx.EXPAND)

        # Panel: Input Area
        PanelInput = wx.Panel(self, wx.ID_ANY)
        self.ListInput = wx.ListBox(PanelInput, wx.ID_ANY,
                                    style=wx.LB_EXTENDED,
                                    size=(193, 200))
        sizerPanelDataHandler.Add(PanelInput, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(3)

        self.ButtonDataLoad = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Load Dataset")
        self.ButtonDataLoad.Enable()
        sizerPanelDataHandler.Add(
            self.ButtonDataLoad, 0, wx.EXPAND)

        self.ButtonDataDrop = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Drop Dataset")
        self.ButtonDataDrop.Disable()
        sizerPanelDataHandler.Add(
            self.ButtonDataDrop, 0, wx.EXPAND)

        self.ButtonDataSave = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Save Dataset")
        self.ButtonDataSave.Disable()
        sizerPanelDataHandler.Add(
            self.ButtonDataSave, 0, wx.EXPAND)

        # Text: Dataset Information
        sizerPanelDataHandler.AddSpacer(15)
        self.TxtInformation = wx.StaticText(PanelDataHandler, wx.ID_ANY,
                                            style=wx.Left, size=(200, 700))
        sizerPanelDataHandler.Add(self.TxtInformation, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(10)

        # Create vertical structure of Data Handler Frame
        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        sizerFrame.AddSpacer(3)
        sizerFrame.Add(PanelDataHandler, 0)
        self.SetSizer(sizerFrame)
        PanelDataHandler.SetSizer(sizerPanelDataHandler)

        # Event specifications
        wx.EVT_BUTTON(self, self.ButtonDataLoad.Id, self.loadData)
        wx.EVT_BUTTON(self, self.ButtonDataDrop.Id, self.dropData)
        wx.EVT_BUTTON(self, self.ButtonDataSave.Id, self.saveData)

    def loadData(self, event):
        """Load BDF files"""

        DirPath = self.Data.DirPath
        wildcard = "BDF files (*.bdf)|*.bdf|H5 files (*.h5)|*.h5"
        dlg = wx.FileDialog(None, "Load BDF or h5 Dataset",
                            defaultDir=DirPath,
                            wildcard=wildcard, style=wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:

            filelist = dlg.GetPaths()

            self.Data.DirPath = os.path.dirname(filelist[0])

            newlist = [os.path.basename(f)[:-4] for f in filelist]
            oldlist = self.Data.Filenames
            newfiles = [ReadBDF(f) for f in filelist
                        if os.path.basename(f)[:-4] not in oldlist]

            self.Data.Filenames += [e for e in newlist if e not in oldlist]
            self.Data.Datasets += newfiles

            self.ListInput.SetItems(self.Data.Filenames)

            self.updateInformation()
            self.ButtonDataDrop.Enable()
            self.Data.Results.updateAll(self.Data)
        dlg.Destroy()
        event.Skip()

    def saveData(self, event):
        """DESCRIPTION"""

        if self.ListInput.GetItems() == []:
            dlg = wx.MessageDialog(
                self, style=wx.OK,
                caption='No Dataset to Save',
                message='You have to load some BDF files before ' +
                        'you can save a dataset as an H5 file.')
            dlg.ShowModal()
            dlg.Destroy()

        else:
            DirPath = self.Data.DirPath
            dlg = wx.FileDialog(None, "Save Dataset as H5 File",
                                wildcard="*.h5",
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                                defaultDir=DirPath,
                                defaultFile='summary.h5')
            if dlg.ShowModal() == wx.ID_OK:
                filepath = dlg.GetPath()
                SaveH5(filepath, self.Data.H5files)
                self.Data.H5files = [filepath]
                self.ListInput.SetItems([os.path.basename(filepath)[:-3]])
            dlg.Destroy()
        event.Skip()

    def dropData(self, event):
        """DESCRIPTION"""
        if self.ListInput.Selections != ():
            drop = [self.ListInput.GetItems()[i]
                    for i in self.ListInput.Selections]
            keep = [h for h in self.Data.Filenames if h not in drop]
            id2keep = [i for i, e in enumerate(self.Data.Filenames)
                       if e in keep]
            self.Data.Filenames = keep
            self.ListInput.SetItems(keep)

            self.Data.Datasets = [
                d for i, d in enumerate(self.Data.Datasets)
                if i in id2keep]
            self.updateInformation()
            if self.Data.Datasets != []:
                self.Data.Results.updateAll(self.Data)
            else:
                self.ButtonDataDrop.Disable()
        event.Skip()

    def updateInformation(self):

        infotext = ''
        if self.Data.Datasets != []:

            sampleRate = self.Data.Datasets[0].sampleRate
            labelsChannel = self.Data.Datasets[0].labelsChannel
            infotext = 'Dataset Overview:\n' + \
                'Sampling Rate\t%i [Hz]\n' % sampleRate + \
                '#Channels\t\t%i\n\n' % labelsChannel.shape[0]

            for d in self.Data.Datasets:
                name = os.path.basename(d.lvFile)[:-3]
                recordtime = '%s at %s:%s' % (d.startDate,
                                              d.startTime[:2],
                                              d.startTime[3:5])
                duration = round(1.0 * d.dataRecorded * d.durationRecorded, 1)
                epochs = len(d.markerValue)
                markers = len(np.unique(d.markerValue))

                infotext += 'Name\t\t%s\n' % name + \
                    '#Epochs\t%s\n' % epochs + \
                    '#Markers\t%s\n' % markers + \
                    'Duration\t%s [s]\n' % duration + \
                    'Recorded\t%s\n\n' % recordtime

            dropdown = ['Average'] + labelsChannel.tolist()

            self.Data.Specs.DropDownNewRef.SetItems(dropdown)

        self.TxtInformation.SetLabel(infotext)

        self.Data.Specs.DropDownNewRef.SetSelection(0)
        self.Data.Specs.DropDownNewRef.SetValue('')
