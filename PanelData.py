import os
import wx
import numpy as np
from FileHandler import ReadBDF, SaveH5, SaveEPH


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
        sizerPanelDataHandler.AddSpacer(2)

        # Box: Dataset Input
        BoxInput = wx.StaticBox(PanelDataHandler,
                                wx.ID_ANY, style=wx.CENTRE,
                                label="Dataset Input")
        BoxInput.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerBoxInput = wx.StaticBoxSizer(BoxInput, wx.VERTICAL)
        sizerBoxInput.AddSpacer(3)

        # Panel: Input Area
        PanelInput = wx.Panel(self, wx.ID_ANY)
        self.ListInput = wx.ListBox(PanelInput, wx.ID_ANY,
                                    style=wx.LB_EXTENDED,
                                    size=(193, 200))
        sizerBoxInput.Add(PanelInput, 0, wx.EXPAND)
        sizerBoxInput.AddSpacer(3)

        self.ButtonDataLoad = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Load Dataset")
        self.ButtonDataLoad.Enable()
        sizerBoxInput.Add(self.ButtonDataLoad, 0, wx.EXPAND)

        self.ButtonDataDrop = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Drop Dataset")
        self.ButtonDataDrop.Disable()
        sizerBoxInput.Add(self.ButtonDataDrop, 0, wx.EXPAND)
        sizerPanelDataHandler.Add(sizerBoxInput, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(20)

        # Box: Dataset Output
        BoxOutput = wx.StaticBox(PanelDataHandler,
                                 wx.ID_ANY, style=wx.CENTRE,
                                 label="Dataset Output")
        BoxOutput.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerBoxOutput = wx.StaticBoxSizer(BoxOutput, wx.VERTICAL)

        self.ButtonDataSaveH5 = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Save Dataset as H5")
        self.ButtonDataSaveH5.Disable()
        sizerBoxOutput.Add(self.ButtonDataSaveH5, 0, wx.EXPAND)

        self.ButtonDataLoadH5 = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Load Dataset from H5")
        self.ButtonDataLoadH5.Disable()
        sizerBoxOutput.Add(self.ButtonDataLoadH5, 0, wx.EXPAND)

        self.ButtonDataSaveTVA = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Save TVA files")
        self.ButtonDataSaveTVA.Disable()
        sizerBoxOutput.Add(self.ButtonDataSaveTVA, 0, wx.EXPAND)

        self.ButtonDataSaveEPH = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Save EPH files")
        self.ButtonDataSaveEPH.Disable()
        sizerBoxOutput.Add(self.ButtonDataSaveEPH, 0, wx.EXPAND)
        sizerPanelDataHandler.Add(sizerBoxOutput, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(20)

        # Box: Dataset Information
        BoxInformation = wx.StaticBox(PanelDataHandler,
                                      wx.ID_ANY, style=wx.CENTRE,
                                      label="Dataset Information")
        BoxInformation.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerBoxInformation = wx.StaticBoxSizer(BoxInformation, wx.VERTICAL)

        self.TxtInformation = wx.StaticText(PanelDataHandler, wx.ID_ANY,
                                            style=wx.Left, size=(200, 700))
        sizerBoxInformation.Add(self.TxtInformation, 0, wx.EXPAND)
        sizerPanelDataHandler.Add(sizerBoxInformation, 0, wx.EXPAND)

        # Create vertical structure of Data Handler Frame
        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        sizerFrame.AddSpacer(3)
        sizerFrame.Add(PanelDataHandler, 0)
        self.SetSizer(sizerFrame)
        PanelDataHandler.SetSizer(sizerPanelDataHandler)

        # Event specifications
        wx.EVT_BUTTON(self, self.ButtonDataLoad.Id, self.loadData)
        wx.EVT_BUTTON(self, self.ButtonDataDrop.Id, self.dropData)
        wx.EVT_BUTTON(self, self.ButtonDataSaveH5.Id, self.saveH5)
        wx.EVT_BUTTON(self, self.ButtonDataLoadH5.Id, self.loadH5)
        wx.EVT_BUTTON(self, self.ButtonDataSaveTVA.Id, self.saveTVA)
        wx.EVT_BUTTON(self, self.ButtonDataSaveEPH.Id, self.saveEPH)

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

            # Only load files if at least one of them is a new dataset
            newElements = np.array([True if e not in oldlist else False
                                    for e in newlist])
            if newElements.sum() != 0:

                newfiles = [ReadBDF(f) for f in filelist
                            if os.path.basename(f)[:-4] not in oldlist]

                self.Data.Filenames += [e for e in newlist if e not in oldlist]
                self.Data.Datasets += newfiles

                self.ListInput.SetItems(self.Data.Filenames)

                self.updateInformation()
                self.Data.Results.updateAll(self.Data)
                self.ButtonDataDrop.Enable()
                self.ButtonDataSaveEPH.Enable()
        dlg.Destroy()
        event.Skip()

    def saveH5(self, event):
        """TODO: Program Button"""

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

    def loadH5(self, event):
        """TODO: Program Button"""
        event.Skip()

    def saveTVA(self, event):
        """TODO: Program Button"""
        event.Skip()

    def saveEPH(self, event):
        """Saves the dataset averages into EPH files"""

        dlgTextName = wx.TextEntryDialog(
            None, 'Under what name do you want to save the output?',
            defaultValue='Results01')
        if dlgTextName.ShowModal() == wx.ID_OK:
            resultsName = dlgTextName.GetValue()

            dlgTextPath = wx.TextEntryDialog(
                None, 'Where do you want to save the output at?',
                defaultValue=os.path.join(self.Data.DirPath, resultsName))
            if dlgTextPath.ShowModal() == wx.ID_OK:
                resultsPath = dlgTextPath.GetValue()
            dlgTextPath.Destroy()

            SaveEPH(resultsName, resultsPath, self.Data.Results)

        dlgTextName.Destroy()
        event.Skip()

    def dropData(self, event):
        """Drops a loaded dataset"""

        if self.ListInput.Selections != ():
            drop = [self.ListInput.GetItems()[i]
                    for i in self.ListInput.Selections]
            keep = [h for h in self.Data.Filenames if h not in drop]
            id2keep = [i for i, e in enumerate(self.Data.Filenames)
                       if e in keep]
            self.Data.Filenames = keep
            self.ListInput.SetItems(keep)

            # Drop the dropped dataset from selectedMatrix
            selected2Keep = np.ones(
                self.Data.Results.matrixSelected.shape[0]).astype('bool')
            start = 0
            for i, e in enumerate(self.Data.Datasets):
                length = len(e.markerValue)
                if i not in id2keep:
                    selected2Keep[start:length+start] = False
                start += length

            newMatrixSelected = self.Data.Results.matrixSelected[selected2Keep]
            self.Data.Results.matrixSelected = newMatrixSelected

            # Drop Dataset
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
            infotext = 'Datasets loaded: %i\n' % len(self.Data.Datasets) + \
                'Channels: %i\n' % labelsChannel.shape[0] + \
                'Sampling Rate: %i [Hz]\n\n' % sampleRate

            for d in self.Data.Datasets:
                name = os.path.basename(d.lvFile)[:-3]
                recordtime = 'at %s:%s, %s' % (d.startTime[:2],
                                               d.startTime[3:5],
                                               d.startDate)
                duration = round(1.0 * d.dataRecorded * d.durationRecorded, 1)
                epochs = len(d.markerValue)
                markers = len(np.unique(d.markerValue))
                length = (int(duration) / 60, int(duration) % 60)

                infotext += 'Name: %s\n' % name + \
                    'Epochs:  \t%s\n' % epochs + \
                    'Markers:\t%s\n' % markers + \
                    'Length:\t%sm%ss\n' % length + \
                    'Recorded %s\n\n' % recordtime

            dropdown = ['Average'] + labelsChannel.tolist()

            self.Data.Specs.DropDownNewRef.SetItems(dropdown)

        self.TxtInformation.SetLabel(infotext)

        self.Data.Specs.DropDownNewRef.SetSelection(0)
        self.Data.Specs.DropDownNewRef.SetValue('')
