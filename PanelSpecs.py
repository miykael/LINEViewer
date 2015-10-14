import wx
import numpy as np


class Specification(wx.Panel):

    """
    SOME TEXT
    """

    def __init__(self, ParentFrame, MainFrame):

        # Create Specification Frame window
        wx.Panel.__init__(self, parent=ParentFrame, size=(210, 1000),
                          style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.MainFrame = MainFrame

        # Panel: Specs Handler
        PanelSpecs = wx.Panel(self, wx.ID_ANY)
        sizerPanelSpecs = wx.BoxSizer(wx.VERTICAL)

        # Text: Data Filters Specifications
        TxtSpecData = wx.StaticText(PanelSpecs,
                                    wx.ID_ANY, style=wx.CENTRE,
                                    label=" Dataset Filters")
        TxtSpecData.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerPanelSpecs.Add(TxtSpecData, 0, wx.EXPAND)

        # High- & Lowpass Filter
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
        sizerPanelSpecs.Add(PanelPassTitle, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(2)

        PanelPassField = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerPassField = wx.BoxSizer(wx.HORIZONTAL)
        sizerPassField.AddSpacer(3)
        self.HighPass = wx.TextCtrl(PanelPassField, wx.ID_ANY,
                                    size=(67, 25), style=wx.TE_PROCESS_ENTER,
                                    value=str(0.1))
        sizerPassField.Add(self.HighPass, 0, wx.EXPAND)
        sizerPassField.AddSpacer(15)
        sizerPassField.AddSpacer(15)
        sizerPassField.AddSpacer(3)
        self.LowPass = wx.TextCtrl(PanelPassField, wx.ID_ANY,
                                   size=(67, 25), style=wx.TE_PROCESS_ENTER,
                                   value=str(80.0))
        sizerPassField.Add(self.LowPass, 0, wx.EXPAND)
        PanelPassField.SetSizer(sizerPassField)
        sizerPanelSpecs.Add(PanelPassField, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        # Notch Filter
        PanelNotch = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerNotch = wx.BoxSizer(wx.HORIZONTAL)
        self.CheckboxNotch = wx.CheckBox(PanelNotch, wx.ID_ANY,
                                         'Notch [Hz]')
        self.CheckboxNotch.SetValue(True)
        self.Notch = wx.TextCtrl(PanelNotch, wx.ID_ANY, size=(67, 25),
                                 style=wx.TE_PROCESS_ENTER,
                                 value=str(50.0))
        sizerNotch.Add(self.CheckboxNotch, 0, wx.EXPAND)
        sizerNotch.AddSpacer(5)
        sizerNotch.Add(self.Notch, 0, wx.EXPAND)
        PanelNotch.SetSizer(sizerNotch)
        sizerPanelSpecs.Add(PanelNotch, 0, wx.EXPAND)

        # Use DC Filter
        self.CheckboxDC = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                      'Remove DC')
        self.CheckboxDC.SetValue(True)
        sizerPanelSpecs.Add(self.CheckboxDC, 0, wx.EXPAND)

        # Average Reference
        self.CheckboxAverage = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                           'Average Reference')
        self.CheckboxAverage.SetValue(True)
        sizerPanelSpecs.Add(self.CheckboxAverage, 0, wx.EXPAND)

        # Specific Reference
        PanelNewRef = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerNewRef = wx.BoxSizer(wx.HORIZONTAL)
        sizerNewRef.AddSpacer(5)
        TextNewRef = wx.StaticText(PanelNewRef, wx.ID_ANY,
                                   label="Reference", style=wx.CENTRE)
        sizerNewRef.Add(TextNewRef, 0, wx.CENTER)
        sizerNewRef.AddSpacer(5)

        self.DropDownNewRef = wx.ComboBox(PanelNewRef, wx.ID_ANY,
                                          value='', choices=[],
                                          style=wx.CB_READONLY,
                                          size=(100, 25))
        sizerNewRef.Add(self.DropDownNewRef, 0, wx.EXPAND)
        PanelNewRef.SetSizer(sizerNewRef)
        sizerPanelSpecs.Add(PanelNewRef, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        self.ButtonInterpolate = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Interpolate Channels")
        self.ButtonInterpolate.Enable()
        self.channels2Interpolate = []
        sizerPanelSpecs.Add(self.ButtonInterpolate, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(40)

        # Text: Epoch Filters Specifications
        TxtSpecEpoch = wx.StaticText(PanelSpecs,
                                     wx.ID_ANY, style=wx.CENTRE,
                                     label=" Epoch Filters")
        TxtSpecEpoch.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerPanelSpecs.Add(TxtSpecEpoch, 0, wx.EXPAND)

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
        sizerPanelSpecs.Add(PanelEpochTitle, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(2)

        PanelEpochField = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerEpochField = wx.BoxSizer(wx.HORIZONTAL)
        sizerEpochField.AddSpacer(3)
        self.PreEpoch = wx.TextCtrl(PanelEpochField, wx.ID_ANY,
                                    size=(67, 25), style=wx.TE_PROCESS_ENTER,
                                    value=str(100.0))
        sizerEpochField.Add(self.PreEpoch, 0, wx.EXPAND)
        sizerEpochField.AddSpacer(15)
        sizerEpochField.AddSpacer(15)
        sizerEpochField.AddSpacer(3)
        self.PostEpoch = wx.TextCtrl(PanelEpochField, wx.ID_ANY,
                                     size=(67, 25), style=wx.TE_PROCESS_ENTER,
                                     value=str(500.0))
        sizerEpochField.Add(self.PostEpoch, 0, wx.EXPAND)
        PanelEpochField.SetSizer(sizerEpochField)
        sizerPanelSpecs.Add(PanelEpochField, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        # Baseline Correction
        self.CheckboxBaseline = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                            'Baseline Correction')
        self.CheckboxBaseline.SetValue(True)
        sizerPanelSpecs.Add(self.CheckboxBaseline, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        # Threshold Specification
        self.CheckboxThreshold = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                             'Threshold Correction')
        self.CheckboxThreshold.SetValue(True)
        sizerPanelSpecs.Add(self.CheckboxThreshold, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        PanelThreshTitle = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerThreshTitle = wx.BoxSizer(wx.HORIZONTAL)
        sizerThreshTitle.AddSpacer(5)

        TextThreshValue = wx.StaticText(PanelThreshTitle, wx.ID_ANY,
                                        label="Thresh. [uV]")
        sizerThreshTitle.Add(TextThreshValue, 0, wx.EXPAND)
        sizerThreshTitle.AddSpacer(15)
        sizerThreshTitle.AddSpacer(2)
        TextThreshWindow = wx.StaticText(PanelThreshTitle, wx.ID_ANY,
                                         label="Window [ms]")
        sizerThreshTitle.Add(TextThreshWindow, 0, wx.EXPAND)
        PanelThreshTitle.SetSizer(sizerThreshTitle)
        sizerPanelSpecs.Add(PanelThreshTitle, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(2)

        PanelThreshField = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerThreshField = wx.BoxSizer(wx.HORIZONTAL)
        sizerThreshField.AddSpacer(3)
        self.ThreshValue = wx.TextCtrl(PanelThreshField, wx.ID_ANY,
                                       size=(67, 25),
                                       style=wx.TE_PROCESS_ENTER,
                                       value=str(80.0))
        sizerThreshField.Add(self.ThreshValue, 0, wx.EXPAND)
        sizerThreshField.AddSpacer(15)
        sizerThreshField.AddSpacer(15)
        sizerThreshField.AddSpacer(3)
        self.ThreshWindow = wx.TextCtrl(PanelThreshField, wx.ID_ANY,
                                        size=(67, 25),
                                        style=wx.TE_PROCESS_ENTER,
                                        value=str(100.0))
        sizerThreshField.Add(self.ThreshWindow, 0, wx.EXPAND)
        PanelThreshField.SetSizer(sizerThreshField)
        sizerPanelSpecs.Add(PanelThreshField, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        self.ButtonExclude = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Exclude Channels for Thr.")
        self.ButtonExclude.Enable()
        self.channels2exclude = []
        sizerPanelSpecs.Add(self.ButtonExclude, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(40)

        # Text: Marker Specifications
        TxtSpecMarker = wx.StaticText(PanelSpecs,
                                      wx.ID_ANY, style=wx.CENTRE,
                                      label=" Marker Options")
        TxtSpecMarker.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerPanelSpecs.Add(TxtSpecMarker, 0, wx.EXPAND)

        self.ButtonMarker = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="Choose &markers to show")
        self.ButtonMarker.Enable()
        self.markers2use = []
        sizerPanelSpecs.Add(self.ButtonMarker, 0, wx.EXPAND)

        # Create vertical structure of Data Handler Frame
        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        sizerFrame.AddSpacer(3)
        sizerFrame.Add(PanelSpecs, 0)
        self.SetSizer(sizerFrame)
        PanelSpecs.SetSizer(sizerPanelSpecs)

        # Specification of events
        wx.EVT_TEXT_ENTER(self.HighPass, self.HighPass.Id, self.drawAll)
        wx.EVT_TEXT_ENTER(self.LowPass, self.LowPass.Id, self.drawAll)
        wx.EVT_TEXT_ENTER(self.Notch, self.Notch.Id, self.drawAll)
        wx.EVT_CHECKBOX(self.CheckboxAverage, self.CheckboxAverage.Id,
                        self.useAverage)
        wx.EVT_CHECKBOX(self.CheckboxDC, self.CheckboxDC.Id, self.useDC)
        wx.EVT_CHECKBOX(self.CheckboxNotch, self.CheckboxNotch.Id,
                        self.useNotch)
        wx.EVT_COMBOBOX(self.DropDownNewRef, self.DropDownNewRef.Id,
                        self.useNewRef)
        wx.EVT_BUTTON(self.ButtonInterpolate, self.ButtonInterpolate.Id,
                      self.interpolateChannels)

        wx.EVT_TEXT_ENTER(self.PreEpoch, self.PreEpoch.Id, self.drawAll)
        wx.EVT_TEXT_ENTER(self.PostEpoch, self.PostEpoch.Id, self.drawAll)
        wx.EVT_TEXT_ENTER(self.ThreshValue, self.ThreshValue.Id,
                          self.drawEpochs)
        wx.EVT_TEXT_ENTER(self.ThreshWindow, self.ThreshWindow.Id,
                          self.drawEpochs)
        wx.EVT_BUTTON(self.ButtonExclude, self.ButtonExclude.Id,
                      self.excludeChannel)
        wx.EVT_CHECKBOX(self.CheckboxThreshold, self.CheckboxThreshold.Id,
                        self.useThreshold)
        wx.EVT_CHECKBOX(self.CheckboxBaseline, self.CheckboxBaseline.Id,
                        self.drawEpochs)

        wx.EVT_BUTTON(self.ButtonMarker, self.ButtonMarker.Id,
                      self.selectMarkers)

    def drawAll(self, event):
        if self.MainFrame.Datasets != []:
            self.MainFrame.Results.updateAll()
        event.Skip()

    def drawEpochs(self, event):
        if self.MainFrame.Datasets != []:
            self.MainFrame.Results.updateEpochs()
        event.Skip()

    def useAverage(self, event):
        if self.CheckboxAverage.GetValue():
            self.DropDownNewRef.SetSelection(0)
            self.DropDownNewRef.SetValue('')
        self.drawAll(event)

    def useNewRef(self, event):
        if self.DropDownNewRef.GetSelection() == 0:
            self.useAverage(event)
            event.Skip()
        else:
            self.CheckboxAverage.SetValue(False)
            self.drawAll(event)

    def useDC(self, event):
        self.drawAll(event)

    def interpolateChannels(self, event):
        if self.MainFrame.Datasets != []:
            channels = self.MainFrame.Datasets[0].labelsChannel
            dlg = wx.MultiChoiceDialog(
                self, caption="Select channels to interpolate",
                message='Which channels should be interpolated?',
                choices=channels)
            selected = [i for i, e in enumerate(channels)
                        if e in self.channels2Interpolate]
            dlg.SetSelections(selected)
            if dlg.ShowModal() == wx.ID_OK:
                self.channels2Interpolate = [channels[x]
                                             for x in dlg.GetSelections()]
            dlg.Destroy()

            self.MainFrame.Results.updateAll()
        event.Skip()

    def useThreshold(self, event):
        if self.CheckboxThreshold.GetValue():
            self.ThreshValue.Enable()
            self.ThreshWindow.Enable()
        else:
            self.ThreshValue.Disable()
            self.ThreshWindow.Disable()
        self.drawEpochs(event)

    def useNotch(self, event):
        if self.CheckboxNotch.GetValue():
            self.Notch.Enable()
        else:
            self.Notch.Disable()
        self.drawAll(event)

    def excludeChannel(self, event):
        if self.MainFrame.Datasets != []:
            channels = self.MainFrame.Datasets[0].labelsChannel
            dlg = wx.MultiChoiceDialog(
                self, caption="Select channels to exclude",
                message='Which channels should be ingored?',
                choices=channels)
            selected = [i for i, e in enumerate(channels)
                        if e in self.channels2exclude]
            dlg.SetSelections(selected)
            if dlg.ShowModal() == wx.ID_OK:
                self.channels2exclude = [channels[x]
                                         for x in dlg.GetSelections()]
            dlg.Destroy()
            self.MainFrame.Results.updateAll()
        event.Skip()

    def selectMarkers(self, event):
        if self.MainFrame.Datasets != []:
            markers = np.unique([m.markerValue
                                 for m in self.MainFrame.Datasets])
            markerTxt = [str(m) for m in markers]
            dlg = wx.MultiChoiceDialog(
                self, caption="Select markers to show",
                message='Which markers should be visualized?',
                choices=markerTxt)
            if self.markers2use == []:
                selected = range(
                    np.unique([m.markerValue
                               for m in self.MainFrame.Datasets]).shape[0])
            else:
                selected = [i for i, e in enumerate(markers)
                            if e in self.markers2use]
            dlg.SetSelections(selected)
            if dlg.ShowModal() == wx.ID_OK:
                self.markers2use = [markers[x]
                                    for x in dlg.GetSelections()]
            dlg.Destroy()

            # TODO: This function doesnt do anything right now

        event.Skip()


"""
PREPROCESSING (under development)
?? envelope filter (only if high and low pass)
?? if yes, than absolute or power: both have averagign window in ms
interpolation: how?
calculate also Global Map Dissimilarity (GMD)
check that GFP is calculated correct (GFP of average or average of GFPs?)
TODO: Create a figure that shows 1 electrode per marker and overlays mean and std for the epoch
"""
"""
ERP ANALYSIS (under development)
data normalization (according to GFP, yes or no)
"""
"""
OUTPUT (under development)
write eph, marker and tva files (also marker for origin)
write or load tvas
create and save figures
"""
"""
https://sites.google.com/site/cartoolcommunity/user-s-guide/analysis/artefacts-rejection-single-subjects-averages
"""
