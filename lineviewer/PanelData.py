import os
import wx
import numpy as np
from FileHandler import (ReadEEG, SaveTVA, SaveERP, SaveEpochs, SaveFigures,
                         SaveVerbose)


class Selecter(wx.Panel):

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
        sizerBoxInput.AddSpacer(3)

        # Panel: Resample Signal
        PanelResample = wx.Panel(PanelDataHandler, wx.ID_ANY)
        sizerResample = wx.BoxSizer(wx.HORIZONTAL)
        sizerResample.AddSpacer(3)
        TextResample = wx.StaticText(PanelResample, wx.ID_ANY,
                                     label="Reslice to", style=wx.CENTRE)
        sizerResample.Add(TextResample, 0, wx.CENTER)
        sizerResample.AddSpacer(5)

        self.Resample = wx.TextCtrl(PanelResample, wx.ID_ANY,
                                    size=(60, 25),
                                    style=wx.TE_PROCESS_ENTER,
                                    value='')
        sizerResample.Add(self.Resample, 0, wx.CENTER)
        sizerResample.AddSpacer(3)
        TextResampleHz = wx.StaticText(PanelResample, wx.ID_ANY,
                                       label="[Hz]", style=wx.CENTRE)
        sizerResample.Add(TextResampleHz, 0, wx.CENTER)
        PanelResample.SetSizer(sizerResample)
        sizerBoxInput.Add(PanelResample, 0, wx.EXPAND)

        sizerPanelDataHandler.Add(sizerBoxInput, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(20)

        # Box: Dataset Output
        BoxOutput = wx.StaticBox(PanelDataHandler,
                                 wx.ID_ANY, style=wx.CENTRE,
                                 label="Dataset Output")
        BoxOutput.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerBoxOutput = wx.StaticBoxSizer(BoxOutput, wx.VERTICAL)

        self.ButtonDataSaveTVA = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="Save &TVA")
        self.ButtonDataSaveTVA.Disable()
        sizerBoxOutput.Add(self.ButtonDataSaveTVA, 0, wx.EXPAND)

        self.ButtonDataSaveEpochs = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="Save &Epochs")
        self.ButtonDataSaveEpochs.Disable()
        sizerBoxOutput.Add(self.ButtonDataSaveEpochs, 0, wx.EXPAND)

        self.ButtonDataSaveERP = wx.Button(
            PanelDataHandler, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="Save &ERP + Figures")
        self.ButtonDataSaveERP.Disable()
        sizerBoxOutput.Add(self.ButtonDataSaveERP, 0, wx.EXPAND)

        sizerPanelDataHandler.Add(sizerBoxOutput, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(20)

        # Box: Dataset Information
        BoxInformation = wx.StaticBox(PanelDataHandler,
                                      wx.ID_ANY, style=wx.CENTRE,
                                      label="Dataset Information")
        BoxInformation.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerBoxInformation = wx.StaticBoxSizer(BoxInformation, wx.VERTICAL)

        self.TxtInformation = wx.StaticText(PanelDataHandler, wx.ID_ANY,
                                            style=wx.Left, size=(200, 1200))
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
        wx.EVT_BUTTON(self, self.ButtonDataSaveTVA.Id, self.saveTVA)
        wx.EVT_BUTTON(self, self.ButtonDataSaveERP.Id, self.saveERP)
        wx.EVT_BUTTON(self, self.ButtonDataSaveEpochs.Id, self.saveEpochs)
        wx.EVT_TEXT_ENTER(self.Resample, self.Resample.Id, self.resampleData)

    def loadData(self, event):
        """Load EEG files"""

        DirPath = self.Data.DirPath
        wildcard = "EEG files (*.bdf,*.eeg)|*.bdf;*.eeg"
        dlg = wx.FileDialog(None, "Load EEG file(s)",
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

                # Which sampling rate to use
                try:
                    sampleRate = int(self.Resample.GetValue())
                except ValueError:
                    sampleRate = 0

                # Which channels to exclude from analysis completly
                excludeChannel = self.Data.Specs.channels2exclude

                # Read all the files
                newfiles = [ReadEEG(f, sampleRate, excludeChannel)
                            for f in filelist
                            if os.path.basename(f)[:-4] not in oldlist]

                self.Data.Filenames += [e for e in newlist if e not in oldlist]
                self.Data.Datasets += newfiles

                self.ListInput.SetItems(self.Data.Filenames)

                self.updateInformation()
                self.Data.Results.updateAll(self.Data)
                self.ButtonDataDrop.Enable()
                self.ButtonDataSaveERP.Enable()
                self.ButtonDataSaveTVA.Enable()
                self.ButtonDataSaveEpochs.Enable()
                self.Resample.SetValue(str(self.Data.Results.sampleRate))
        dlg.Destroy()
        event.Skip()

    def saveTVA(self, event):
        """Saves TVA's of current analysis"""

        SaveTVA(self.Data, self.Data.Results.preCut,
                self.Data.Results.postCut)

        event.Skip()

    def saveERP(self, event):
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

            # Update before saving
            if self.Data.Results.updateAnalysis:
                self.Data.Results.updateEpochs(self.Data)
                self.Data.Results.updateAnalysis = False

            # Save outputs
            SaveERP(resultsName, resultsPath, self.Data.Results,
                    self.Data.markers2hide, self.Data.Results.preFrame)
            SaveFigures(resultsName, resultsPath, self.Data)
            SaveVerbose(resultsName, resultsPath, self.Data)

        dlgTextName.Destroy()
        event.Skip()

    def saveEpochs(self, event):
        """Saves the dataset epochs into individual EPH files"""

        dlgTextName = wx.TextEntryDialog(
            None, 'Under what name do you want to save the output?',
            defaultValue=os.path.join('Results01', 'Epochs'))
        if dlgTextName.ShowModal() == wx.ID_OK:
            resultsName = dlgTextName.GetValue()

            dlgTextPath = wx.TextEntryDialog(
                None, 'Where do you want to save the output at?',
                defaultValue=os.path.join(self.Data.DirPath, resultsName))
            if dlgTextPath.ShowModal() == wx.ID_OK:
                resultsPath = dlgTextPath.GetValue()
            dlgTextPath.Destroy()

            # Update before saving
            if self.Data.Results.updateAnalysis:
                self.Data.Results.updateEpochs(self.Data)
                self.Data.Results.updateAnalysis = False

            # Save Epochs
            SaveEpochs(resultsPath, self.Data.Results,
                       self.Data.Results.preFrame)

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
                    selected2Keep[start:length + start] = False
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
                self.Resample.SetValue('')
        event.Skip()

    def resampleData(self, event):
        """reload data and resample to given value"""

        if self.Data.Datasets != []:

            oldSampleRate = self.Data.Datasets[0].sampleRate

            try:
                newSampleRate = int(self.Resample.GetValue())
            except ValueError:
                self.Resample.SetValue(str(oldSampleRate))
                newSampleRate = oldSampleRate

            # Which channels to exclude from analysis completly
            excludeChannel = self.Data.Specs.channels2exclude

            if oldSampleRate != newSampleRate:

                filelist = [f.filename for f in self.Data.Datasets]
                newfiles = [ReadEEG(f, newSampleRate, excludeChannel)
                            for f in filelist]

                self.Data.Datasets = newfiles
                self.updateInformation()
                del self.Data.Results.matrixSelected
                self.Data.Results.updateAll(self.Data)

        event.Skip()

    def updateInformation(self):

        infotext = ''
        if self.Data.Datasets != []:

            sampleRate = self.Data.Datasets[0].sampleRate
            labelsChannel = self.Data.Datasets[0].labelsChannel
            infotext = 'Datasets loaded: %i\n' % len(self.Data.Datasets) + \
                'Channels: %i\n' % labelsChannel.shape[0] + \
                'Sampling Freq.: %i [Hz]\n\n' % sampleRate

            for d in self.Data.Datasets:
                name = os.path.basename(d.eegFile).split('.')[0]
                recordtime = '%s %s:%s' % (d.startDate,
                                           d.startTime[:2],
                                           d.startTime[3:5])
                duration = round(float(d.dataRecorded) * d.durationRecorded, 1)
                epochs = len(d.markerValue)
                markers = len(np.unique(d.markerValue))
                length = (int(duration) / 60, int(duration) % 60)

                infotext += 'Name: %s\n' % name + \
                    'Epochs:  \t%s\n' % epochs + \
                    'Markers:\t%s\n' % markers + \
                    'Length:\t%sm%ss\n' % length + \
                    'Date:  \t%s\n\n' % recordtime

            dropdown = ['Average', 'None'] + labelsChannel.tolist()

            self.Data.Specs.DropDownNewRef.SetItems(dropdown)

        self.TxtInformation.SetLabel(infotext)

        self.Data.Specs.DropDownNewRef.SetSelection(1)
        self.Data.Specs.DropDownNewRef.SetValue('None')
