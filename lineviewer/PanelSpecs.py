import wx
import numpy as np
from os.path import dirname
from FileHandler import ReadEEG


class Specification(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Specification Frame window
        wx.Panel.__init__(self, parent=ParentFrame, size=(210, 1000),
                          style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        self.Data.Specs = type('Specs', (object,), {})()

        # Panel: Specs Handler
        PanelSpecs = wx.Panel(self, wx.ID_ANY)
        sizerPanelSpecs = wx.BoxSizer(wx.VERTICAL)

        # Box: Data Filters Specifications
        BoxSpecData = wx.StaticBox(PanelSpecs,
                                   wx.ID_ANY, style=wx.CENTRE,
                                   label="Dataset Filters")
        BoxSpecData.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerBoxData = wx.StaticBoxSizer(BoxSpecData, wx.VERTICAL)

        # Use DC Filter
        self.Data.Specs.CheckboxDC = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                                 'Remove DC')
        self.Data.Specs.CheckboxDC.SetValue(True)
        sizerBoxData.Add(self.Data.Specs.CheckboxDC, 0, wx.EXPAND)

        # Average Reference
        self.Data.Specs.CheckboxAverage = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                                      'Average Reference')
        self.Data.Specs.CheckboxAverage.SetValue(False)
        sizerBoxData.Add(self.Data.Specs.CheckboxAverage, 0, wx.EXPAND)

        # Specific Reference
        PanelNewRef = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerNewRef = wx.BoxSizer(wx.HORIZONTAL)
        sizerNewRef.AddSpacer(5)
        TextNewRef = wx.StaticText(PanelNewRef, wx.ID_ANY,
                                   label="Reference", style=wx.CENTRE)
        sizerNewRef.Add(TextNewRef, 0, wx.CENTER)
        sizerNewRef.AddSpacer(5)

        self.Data.Specs.DropDownNewRef = wx.ComboBox(PanelNewRef, wx.ID_ANY,
                                                     value='None', choices=[],
                                                     style=wx.CB_READONLY,
                                                     size=(100, 25))
        sizerNewRef.Add(self.Data.Specs.DropDownNewRef, 0, wx.EXPAND)
        PanelNewRef.SetSizer(sizerNewRef)
        sizerBoxData.Add(PanelNewRef, 0, wx.EXPAND)

        # High- & Lowpass Filter
        self.Data.Specs.CheckboxPass = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                                   'Use Pass Filters')
        self.Data.Specs.CheckboxPass.SetValue(True)
        sizerBoxData.Add(self.Data.Specs.CheckboxPass, 0, wx.EXPAND)

        PanelPassTitle = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerPassTitle = wx.BoxSizer(wx.HORIZONTAL)
        sizerPassTitle.AddSpacer(5)

        TextHighPass = wx.StaticText(PanelPassTitle, wx.ID_ANY,
                                     label="Highpass [Hz]")
        sizerPassTitle.Add(TextHighPass, 0, wx.EXPAND)
        sizerPassTitle.AddSpacer(5)
        TextLowPass = wx.StaticText(PanelPassTitle, wx.ID_ANY,
                                    label="Lowpass [Hz]")
        sizerPassTitle.Add(TextLowPass, 0, wx.EXPAND)
        PanelPassTitle.SetSizer(sizerPassTitle)
        sizerBoxData.Add(PanelPassTitle, 0, wx.EXPAND)
        sizerBoxData.AddSpacer(2)

        PanelPassField = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerPassField = wx.BoxSizer(wx.HORIZONTAL)
        sizerPassField.AddSpacer(3)
        self.Data.Specs.HighPass = wx.TextCtrl(PanelPassField, wx.ID_ANY,
                                               size=(67, 25),
                                               style=wx.TE_PROCESS_ENTER,
                                               value=str(0.1))
        sizerPassField.Add(self.Data.Specs.HighPass, 0, wx.EXPAND)
        sizerPassField.AddSpacer(15)
        sizerPassField.AddSpacer(15)
        sizerPassField.AddSpacer(3)
        self.Data.Specs.LowPass = wx.TextCtrl(PanelPassField, wx.ID_ANY,
                                              size=(67, 25),
                                              style=wx.TE_PROCESS_ENTER,
                                              value=str(80.0))
        sizerPassField.Add(self.Data.Specs.LowPass, 0, wx.EXPAND)
        PanelPassField.SetSizer(sizerPassField)
        sizerBoxData.Add(PanelPassField, 0, wx.EXPAND)
        sizerBoxData.AddSpacer(5)

        # Notch Filter
        PanelNotch = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerNotch = wx.BoxSizer(wx.HORIZONTAL)
        self.Data.Specs.CheckboxNotch = wx.CheckBox(PanelNotch, wx.ID_ANY,
                                                    'Notch [Hz]')
        self.Data.Specs.CheckboxNotch.SetValue(True)
        self.Data.Specs.Notch = wx.TextCtrl(PanelNotch, wx.ID_ANY,
                                            size=(67, 25),
                                            style=wx.TE_PROCESS_ENTER,
                                            value=str(50.0))
        sizerNotch.Add(self.Data.Specs.CheckboxNotch, 0, wx.EXPAND)
        sizerNotch.AddSpacer(5)
        sizerNotch.Add(self.Data.Specs.Notch, 0, wx.EXPAND)
        PanelNotch.SetSizer(sizerNotch)
        sizerBoxData.Add(PanelNotch, 0, wx.EXPAND)

        # Box: Channels to Ignore
        self.ButtonChannel = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="Exclude &Channels")
        self.ButtonChannel.Enable()
        self.Data.Specs.channels2exclude = []
        sizerBoxData.Add(self.ButtonChannel, 0, wx.EXPAND)

        sizerPanelSpecs.Add(sizerBoxData, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(20)

        # Box: Epoch Filters Specifications
        BoxSpecEpoch = wx.StaticBox(PanelSpecs, wx.ID_ANY, style=wx.CENTRE,
                                    label="Epoch Filters")
        BoxSpecEpoch.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerBoxEpoch = wx.StaticBoxSizer(BoxSpecEpoch, wx.VERTICAL)

        # Epoch Specification
        PanelEpochTitle = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerEpochTitle = wx.BoxSizer(wx.HORIZONTAL)
        sizerEpochTitle.AddSpacer(5)

        TextHighEpoch = wx.StaticText(PanelEpochTitle, wx.ID_ANY,
                                      label="Pre [ms]")
        sizerEpochTitle.Add(TextHighEpoch, 0, wx.EXPAND)
        sizerEpochTitle.AddSpacer(15)
        sizerEpochTitle.AddSpacer(15)
        sizerEpochTitle.AddSpacer(12)
        TextLowEpoch = wx.StaticText(PanelEpochTitle, wx.ID_ANY,
                                     label="Post [ms]")
        sizerEpochTitle.Add(TextLowEpoch, 0, wx.EXPAND)
        PanelEpochTitle.SetSizer(sizerEpochTitle)
        sizerBoxEpoch.Add(PanelEpochTitle, 0, wx.EXPAND)
        sizerBoxEpoch.AddSpacer(2)

        PanelEpochField = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerEpochField = wx.BoxSizer(wx.HORIZONTAL)
        sizerEpochField.AddSpacer(3)
        self.Data.Specs.PreEpoch = wx.TextCtrl(PanelEpochField, wx.ID_ANY,
                                               size=(67, 25),
                                               style=wx.TE_PROCESS_ENTER,
                                               value=str(100.0))
        sizerEpochField.Add(self.Data.Specs.PreEpoch, 0, wx.EXPAND)
        sizerEpochField.AddSpacer(15)
        sizerEpochField.AddSpacer(15)
        sizerEpochField.AddSpacer(3)
        self.Data.Specs.PostEpoch = wx.TextCtrl(PanelEpochField, wx.ID_ANY,
                                                size=(67, 25),
                                                style=wx.TE_PROCESS_ENTER,
                                                value=str(500.0))
        sizerEpochField.Add(self.Data.Specs.PostEpoch, 0, wx.EXPAND)
        PanelEpochField.SetSizer(sizerEpochField)
        sizerBoxEpoch.Add(PanelEpochField, 0, wx.EXPAND)
        sizerBoxEpoch.AddSpacer(5)

        # Baseline Correction
        PanelBaseTitle = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerBaseTitle = wx.BoxSizer(wx.HORIZONTAL)
        sizerBaseTitle.AddSpacer(5)
        TextBase = wx.StaticText(PanelBaseTitle, wx.ID_ANY,
                                 label="Baseline Correction")
        sizerBaseTitle.Add(TextBase, 0, wx.EXPAND)
        PanelBaseTitle.SetSizer(sizerBaseTitle)
        sizerBoxEpoch.Add(PanelBaseTitle, 0, wx.EXPAND)
        sizerBoxEpoch.AddSpacer(2)

        PanelBaseDrop = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerBaseDrop = wx.BoxSizer(wx.HORIZONTAL)
        sizerBaseDrop.AddSpacer(3)
        self.Data.Specs.DropDownBase = wx.ComboBox(
            PanelBaseDrop, wx.ID_ANY, value='None',
            choices=['None', 'pre2zero', 'pre2post'],
            style=wx.CB_READONLY, size=(100, 25))
        self.Data.Specs.DropDownBase.SetSelection(0)
        sizerBaseDrop.Add(self.Data.Specs.DropDownBase, 0, wx.EXPAND)
        PanelBaseDrop.SetSizer(sizerBaseDrop)
        sizerBoxEpoch.Add(PanelBaseDrop, 0, wx.EXPAND)
        sizerBoxEpoch.AddSpacer(5)

        # Bridge Specification
        self.Data.Specs.CheckboxBridge = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                                     'Bridge Detection')
        self.Data.Specs.CheckboxBridge.SetValue(False)
        sizerBoxEpoch.Add(self.Data.Specs.CheckboxBridge, 0, wx.EXPAND)

        # Blink Specification
        self.Data.Specs.CheckboxBlink = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                                    'Blink Detection')
        self.Data.Specs.CheckboxBlink.SetValue(False)
        sizerBoxEpoch.Add(self.Data.Specs.CheckboxBlink, 0, wx.EXPAND)

        # Threshold Specification
        PanelThresh = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerThresh = wx.BoxSizer(wx.HORIZONTAL)
        self.Data.Specs.CheckboxThreshold = wx.CheckBox(PanelThresh, wx.ID_ANY,
                                                        'Thresh. [uV]')
        self.Data.Specs.CheckboxThreshold.SetValue(True)
        self.Data.Specs.ThreshValue = wx.TextCtrl(PanelThresh, wx.ID_ANY,
                                                  size=(67, 25),
                                                  style=wx.TE_PROCESS_ENTER,
                                                  value=str(80.0))
        sizerThresh.Add(self.Data.Specs.CheckboxThreshold, 0, wx.EXPAND)
        sizerThresh.AddSpacer(5)
        sizerThresh.Add(self.Data.Specs.ThreshValue, 0, wx.EXPAND)
        PanelThresh.SetSizer(sizerThresh)
        sizerBoxEpoch.Add(PanelThresh, 0, wx.EXPAND)
        sizerBoxEpoch.AddSpacer(5)

        self.ButtonExclude = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Exclude channels from Thr.")
        self.ButtonExclude.Enable()
        self.Data.Specs.channels2ignore = []
        sizerBoxEpoch.Add(self.ButtonExclude, 0, wx.EXPAND)

        sizerPanelSpecs.Add(sizerBoxEpoch, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(20)

        # Box: Marker Specifications
        BoxSpecMarker = wx.StaticBox(PanelSpecs, wx.ID_ANY, style=wx.CENTRE,
                                     label="Marker Options")
        BoxSpecMarker.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerBoxMarker = wx.StaticBoxSizer(BoxSpecMarker, wx.VERTICAL)

        # Box: Marker Specifications
        self.ButtonMarker = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="Hide &markers")
        self.ButtonMarker.Enable()
        self.Data.markers2hide = []
        sizerBoxMarker.Add(self.ButtonMarker, 0, wx.EXPAND)

        self.ButtonMarkerCollapse = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="Collapse markers")
        self.ButtonMarkerCollapse.Enable()
        sizerBoxMarker.Add(self.ButtonMarkerCollapse, 0, wx.EXPAND)

        self.ButtonMarkerReset = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="Reset marker options")
        self.ButtonMarkerReset.Enable()
        sizerBoxMarker.Add(self.ButtonMarkerReset, 0, wx.EXPAND)

        sizerPanelSpecs.Add(sizerBoxMarker, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(20)

        # Box: Interpolation Specifications
        BoxSpecInterpolation = wx.StaticBox(PanelSpecs,
                                            wx.ID_ANY, style=wx.CENTRE,
                                            label="Interpolation")
        BoxSpecInterpolation.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL,
                                             wx.BOLD))
        sizerBoxInterpolation = wx.StaticBoxSizer(BoxSpecInterpolation,
                                                  wx.VERTICAL)

        self.ButtonInterpolate = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Channels to interpolate")
        self.ButtonInterpolate.Enable()
        self.Data.Specs.channels2interpolate = []
        sizerBoxInterpolation.Add(self.ButtonInterpolate, 0, wx.EXPAND)
        self.Data.Specs.xyzFile = ''
        self.TextInterpolated = wx.StaticText(
            PanelSpecs, wx.ID_ANY, label='No interpolated channels\n\n')
        sizerBoxInterpolation.Add(self.TextInterpolated, 0, wx.EXPAND)
        sizerPanelSpecs.Add(sizerBoxInterpolation, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(20)

        # Create vertical structure of Data Handler Frame
        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        sizerFrame.AddSpacer(3)
        sizerFrame.Add(PanelSpecs, 0)
        self.SetSizer(sizerFrame)
        PanelSpecs.SetSizer(sizerPanelSpecs)

        # Specification of events
        wx.EVT_TEXT_ENTER(self.Data.Specs.HighPass,
                          self.Data.Specs.HighPass.Id, self.drawAll)
        wx.EVT_TEXT_ENTER(self.Data.Specs.LowPass, self.Data.Specs.LowPass.Id,
                          self.drawAll)
        wx.EVT_TEXT_ENTER(self.Data.Specs.Notch, self.Data.Specs.Notch.Id,
                          self.drawAll)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxAverage,
                        self.Data.Specs.CheckboxAverage.Id, self.useAverage)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxDC,
                        self.Data.Specs.CheckboxDC.Id, self.useDC)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxNotch,
                        self.Data.Specs.CheckboxNotch.Id, self.useNotch)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxPass,
                        self.Data.Specs.CheckboxPass.Id, self.usePass)
        wx.EVT_COMBOBOX(self.Data.Specs.DropDownNewRef,
                        self.Data.Specs.DropDownNewRef.Id, self.useNewRef)
        wx.EVT_BUTTON(self.ButtonChannel, self.ButtonChannel.Id,
                      self.excludeChannels)

        wx.EVT_TEXT_ENTER(self.Data.Specs.PreEpoch,
                          self.Data.Specs.PreEpoch.Id, self.drawAll)
        wx.EVT_TEXT_ENTER(self.Data.Specs.PostEpoch,
                          self.Data.Specs.PostEpoch.Id, self.drawAll)
        wx.EVT_TEXT_ENTER(self.Data.Specs.ThreshValue,
                          self.Data.Specs.ThreshValue.Id, self.useThreshold)
        wx.EVT_BUTTON(self.ButtonExclude, self.ButtonExclude.Id,
                      self.ignoreChannelThresh)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxThreshold,
                        self.Data.Specs.CheckboxThreshold.Id,
                        self.useThreshold)
        wx.EVT_COMBOBOX(self.Data.Specs.DropDownBase,
                        self.Data.Specs.DropDownBase.Id, self.drawEpochs)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxBridge,
                        self.Data.Specs.CheckboxBridge.Id, self.drawEpochs)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxBlink,
                        self.Data.Specs.CheckboxBlink.Id, self.drawEpochs)

        wx.EVT_BUTTON(self.ButtonMarker, self.ButtonMarker.Id,
                      self.hideMarkers)
        wx.EVT_BUTTON(self.ButtonMarkerCollapse, self.ButtonMarkerCollapse.Id,
                      self.collapseMarkers)
        wx.EVT_BUTTON(self.ButtonMarkerReset, self.ButtonMarkerReset.Id,
                      self.resetMarkers)

        wx.EVT_BUTTON(self.ButtonInterpolate, self.ButtonInterpolate.Id,
                      self.interpolateChannels)

    def drawAll(self, event):
        if self.Data.Datasets != []:
            self.Data.Results.updateAll(self.Data)
        event.Skip()

    def drawEpochs(self, event):
        if self.Data.Datasets != []:
            self.Data.Results.updateEpochs(self.Data)
        event.Skip()

    def redrawFigures(self, event):
        if self.Data.Datasets != []:
            self.Data.Overview.update(self.Data.Results)
            self.Data.GFPSummary.update(self.Data.Results)
            self.Data.GFPDetail.update(self.Data.Results)
            self.Data.ERPSummary.update(self.Data.EpochsDetail.markerValue)
            self.Data.EpochsDetail.update(self.Data.EpochsDetail.markerValue)
        event.Skip()

    def useAverage(self, event):
        if self.Data.Specs.CheckboxAverage.GetValue():
            self.Data.Specs.DropDownNewRef.SetSelection(0)
        else:
            self.Data.Specs.DropDownNewRef.SetSelection(1)
        self.drawAll(event)

    def useNewRef(self, event):
        if self.Data.Specs.DropDownNewRef.GetSelection() == 0:
            self.Data.Specs.CheckboxAverage.SetValue(True)
            self.useAverage(event)
            event.Skip()
        else:
            self.Data.Specs.CheckboxAverage.SetValue(False)
            self.drawAll(event)

    def useDC(self, event):
        self.drawAll(event)

    def interpolateChannels(self, event):
        if self.Data.Datasets != []:
            channels = self.Data.Datasets[0].labelsChannel
            dlgSelect = wx.MultiChoiceDialog(
                self, caption="Select channels to interpolate",
                message='Which channels should be interpolated?',
                choices=channels)
            selected = [i for i, e in enumerate(channels)
                        if e in self.Data.Specs.channels2interpolate]
            dlgSelect.SetSelections(selected)
            if dlgSelect.ShowModal() == wx.ID_OK:
                self.Data.Specs.channels2interpolate = [
                    channels[x] for x in dlgSelect.GetSelections()]

                if self.Data.Specs.xyzFile == '':
                    self.xyzPath = self.Data.DirPath

                    dlgXYZ = wx.FileDialog(None, "Load xyz file",
                                           defaultDir=self.xyzPath,
                                           wildcard='*.xyz')
                    if dlgXYZ.ShowModal() == wx.ID_OK:
                        self.Data.Specs.xyzFile = dlgXYZ.GetPath()
                        self.Data.Results.interpolationCheck(self.Data)
                    dlgXYZ.Destroy()
                else:
                    self.xyzPath = dirname(self.Data.Specs.xyzFile)
                    self.Data.Results.interpolationCheck(self.Data)

                labeltxt = 'Interpolated Channels:\n' + \
                    ''.join([e + ', ' if i % 7 != 6
                             else e + ',\n'
                             for i, e in enumerate(
                                 self.Data.Specs.channels2interpolate)])
                if self.Data.Specs.channels2interpolate == []:
                    labeltxt = 'No interpolated channels\n\n'

                self.TextInterpolated.SetLabel(labeltxt)
            dlgSelect.Destroy()
        event.Skip()

    def useThreshold(self, event):
        if self.Data.Specs.CheckboxThreshold.GetValue():
            self.Data.Specs.ThreshValue.Enable()
            self.ButtonExclude.Enable()
        else:
            self.Data.Specs.ThreshValue.Disable()
            self.ButtonExclude.Disable()

        # Reset matrixSelected
        if hasattr(self.Data.Results, 'matrixSelected'):
            del self.Data.Results.matrixSelected

        self.drawEpochs(event)

    def useNotch(self, event):
        if self.Data.Specs.CheckboxNotch.GetValue():
            self.Data.Specs.Notch.Enable()
        else:
            self.Data.Specs.Notch.Disable()
        self.drawAll(event)

    def usePass(self, event):
        if self.Data.Specs.CheckboxPass.GetValue():
            self.Data.Specs.HighPass.Enable()
            self.Data.Specs.LowPass.Enable()
        else:
            self.Data.Specs.HighPass.Disable()
            self.Data.Specs.LowPass.Disable()
        self.drawAll(event)

    def ignoreChannelThresh(self, event):
        if self.Data.Datasets != []:
            channels = self.Data.Datasets[0].labelsChannel
            dlg = wx.MultiChoiceDialog(
                self, caption="Select channels to exclude",
                message='Which channels should be ingored?',
                choices=channels)
            selected = [i for i, e in enumerate(channels)
                        if e in self.Data.Specs.channels2ignore]
            dlg.SetSelections(selected)
            if dlg.ShowModal() == wx.ID_OK:
                self.Data.Specs.channels2ignore = [
                    channels[x] for x in dlg.GetSelections()]
                self.Data.Results.updateEpochs(self.Data)
            dlg.Destroy()
        event.Skip()

    def excludeChannels(self, event):
        if self.Data.Datasets != []:
            channels = self.Data.Datasets[0].labelsChannel
            dlg = wx.MultiChoiceDialog(
                self, caption="Select channels to exclude",
                message='Which channels should be excluded?',
                choices=channels)
            selected = [i for i, e in enumerate(channels)
                        if e in self.Data.Specs.channels2exclude]
            dlg.SetSelections(selected)
            if dlg.ShowModal() == wx.ID_OK:
                self.Data.Specs.channels2exclude = [
                    channels[x] for x in dlg.GetSelections()]
                sampleRate = self.Data.Datasets[0].sampleRate
                filelist = [f.filename for f in self.Data.Datasets]
                newfiles = [ReadEEG(
                    f, sampleRate, self.Data.Specs.channels2exclude)
                    for f in filelist]
                self.Data.Datasets = newfiles
                del self.Data.Results.matrixSelected
                self.Data.Results.updateAll(self.Data)
            dlg.Destroy()
        event.Skip()

    def hideMarkers(self, event):

        if self.Data.Datasets != []:
            if not hasattr(self.Data.Results, 'collapsedMarkers'):
                markers = np.copy(self.Data.Results.markers)
            else:
                markers = self.Data.Results.collapsedMarkers
            markers = np.unique(markers)
            markers = markers.tolist() + self.Data.markers2hide
            markers = np.unique(markers).tolist()
            markers.sort()
            markerTxt = [str(m) for m in markers]
            dlg = wx.MultiChoiceDialog(
                self, caption="Select markers to hide",
                message='Which markers should be hidden ' +
                        'from further analysis?',
                choices=markerTxt)
            if self.Data.markers2hide == []:
                selected = []
            else:
                selected = [i for i, e in enumerate(markers)
                            if e in self.Data.markers2hide]
            dlg.SetSelections(selected)
            if dlg.ShowModal() == wx.ID_OK:
                if len(markers) != len(dlg.GetSelections()):
                    self.Data.markers2hide = [markers[x]
                                              for x in dlg.GetSelections()]
                    self.redrawFigures(event)

            dlg.Destroy()
        event.Skip()

    def collapseMarkers(self, event):

        if self.Data.Datasets != []:
            if not hasattr(self.Data.Results, 'collapsedMarkers'):
                markers = np.copy(self.Data.Results.markers)
                self.Data.Results.collapsedTransform = []
            else:
                markers = self.Data.Results.collapsedMarkers
            markers = np.unique(markers)
            markerTxt = [str(m) for m in markers]

            self.getCollapseList(markerTxt)
            if self.updateMarkers:
                self.drawEpochs(event)
        event.Skip()

    def getCollapseList(self, markerTxt):

        self.updateMarkers = False

        dlg = wx.MultiChoiceDialog(
            self, caption="Select markers to collapse",
            message='Which markers should be collapsed?',
            choices=markerTxt)
        if dlg.ShowModal() == wx.ID_OK:
            selected = dlg.GetSelections()

            while True:
                dlgText = wx.TextEntryDialog(
                    None, 'What should be the new value of the marker?\n')
                if dlgText.ShowModal() == wx.ID_OK:
                    newMarkerName = dlgText.GetValue()
                    dlgText.Destroy()

                    markers2collapse = np.array(markerTxt,
                                                dtype='str')[selected]
                    if not hasattr(self.Data.Results, 'collapsedMarkers'):
                        rawMarkers = np.copy(self.Data.Results.markers)
                    else:
                        rawMarkers = self.Data.Results.collapsedMarkers
                    for i, e in enumerate(markers2collapse):
                        rawMarkers[rawMarkers == e] = np.str(newMarkerName)
                    self.Data.Results.collapsedMarkers = rawMarkers
                    self.Data.Results.collapsedTransform.append(
                        [newMarkerName, markers2collapse])

                    # Should more markers be collapsed
                    dlgMore = wx.MessageDialog(
                        self, "Do you want to collapse more markers?",
                        "Select markers to collapse",
                        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                    if dlgMore.ShowModal() == wx.ID_YES:
                        markerTxt = [str(m) for m in np.unique(rawMarkers)]
                        self.getCollapseList(markerTxt)
                        dlgMore.Destroy()
                    self.updateMarkers = True
                break
        dlg.Destroy()

    def resetMarkers(self, event):
        if self.Data.Datasets != []:
            if hasattr(self.Data.Results, 'collapsedMarkers'):
                del self.Data.Results.collapsedMarkers
            self.Data.markers2hide = []
            self.Data.Results.matrixSelected[
                np.where(
                    self.Data.Results.matrixSelected == 'selected')
            ] = 'ok_normal'
            self.drawEpochs(event)
            event.Skip()
