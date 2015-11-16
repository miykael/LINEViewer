import wx
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar


class GFPSummary(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        self.ParentFrame = ParentFrame
        newFigure(self, showGrid=True)

        # Figure events
        self.canvas.mpl_connect('button_press_event', self.gotoDetailedGFP)

    def update(self, Results):
        if self.Data.Datasets == []:
            newFigure(self, showGrid=True)
        else:
            self.figure.clear()
            xaxis = getXaxis(Results)
            plt.plot(xaxis, np.transpose(Results.avgGFP))
            plt.xlabel('time [ms]')
            plt.ylabel('GFP')
            plt.title('GFP Overview')
            plt.legend(Results.uniqueMarkers)
            self.figure.subplots_adjust(left=0.03,
                                        bottom=0.04,
                                        right=0.98,
                                        top=0.97)
            plt.grid(self.CheckboxGrid.IsChecked())
            self.canvas.draw()

    def gotoDetailedGFP(self, event):
        ax = event.inaxes
        if ax is None:
            return
        if event.button is 1:
            if event.dblclick:
                self.ParentFrame.SetSelection(1)
                self.canvas.ReleaseMouse()
        elif event.button is 3:
            if event.dblclick:
                if hasattr(self.Data.Results, 'collapsedMarkers'):
                    del self.Data.Results.collapsedMarkers
                self.canvas.ReleaseMouse()
                self.Data.markers2hide = []
                self.Data.Results.updateEpochs(self.Data)

    def updateFigure(self, event):
        if self.Data.Datasets != []:
            self.Data.GFPSummary.update(self.Data.Results)
        event.Skip()


class GFPDetailed(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        self.ParentFrame = ParentFrame
        newFigure(self, showGrid=True, showGFP=True, showGMD=True)

        # Figure events
        self.canvas.mpl_connect('button_press_event', self.zoomInDetailedGFP)

    def update(self, Results):

        if self.Data.Datasets == []:
            newFigure(self, showGrid=True, showGFP=True, showGMD=True)
        else:
            self.figure.clear()
            figureShape = findSquare(Results.uniqueMarkers.shape[0])
            xaxis = getXaxis(Results)
            for i, g in enumerate(Results.avgGFP):
                axes = self.figure.add_subplot(figureShape[0],
                                               figureShape[1],
                                               i + 1)
                if self.CheckboxGFP.IsChecked():
                    axes.plot(xaxis, Results.avgGFP[i], 'b')
                if self.CheckboxGMD.IsChecked():
                    axes.plot(xaxis, Results.avgGMD[i], 'r')
                nMarkers = np.where(
                    Results.markers == Results.uniqueMarkers[i])[0].shape[0]
                axes.title.set_text(
                    'Marker: %s [N=%s]' % (Results.uniqueMarkers[i], nMarkers))
                axes.grid(self.CheckboxGrid.IsChecked())
            self.figure.subplots_adjust(left=0.03,
                                        bottom=0.03,
                                        right=0.98,
                                        top=0.97,
                                        wspace=0.20,
                                        hspace=0.24)
            self.canvas.draw()

    def updateFigure(self, event):
        if self.Data.Datasets != []:
            self.Data.GFPDetailed.update(self.Data.Results)
        event.Skip()

    def zoomInDetailedGFP(self, event):
        ax = event.inaxes
        if ax is None:
            return
        if event.dblclick:
            # On left click, zoom the selected axes
            if event.button is 1:
                subplotID = event.inaxes.get_subplotspec().num1
                markerID = self.Data.Results.uniqueMarkers[subplotID]

                self.Data.EpochSummary.update(markerID)
                self.Data.EpochMarkerDetail.update(markerID)
                self.ParentFrame.SetSelection(2)
                self.canvas.ReleaseMouse()


class EpochSummary(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        newFigure(self)

    def update(self, markerValue):
        epochs = self.Data.Results.epochs[
            np.where(self.Data.Results.markers == markerValue)]
        epoch = epochs.mean(axis=0)

        preEpoch = float(self.Data.Specs.PreEpoch.GetValue())
        postEpoch = float(self.Data.Specs.PostEpoch.GetValue())
        samplingPoints = epoch.shape[1]

        xaxis = [int(1.0 * i * (preEpoch + postEpoch) /
                     samplingPoints - preEpoch) for i in range(samplingPoints)]

        axes = self.figure.add_subplot(1, 1, 1)
        sizer = np.sqrt(np.sum(np.ptp(epoch, axis=1) / epoch.shape[0]))

        # correct for threshold
        badChannelThreshold = np.zeros(epoch.shape[0], dtype=int)
        if self.Data.Specs.CheckboxThreshold.GetValue():
            windowSteps = int(self.Data.Results.window *
                              self.Data.Results.sampleRate / 1000.)
            for j in range(epoch.shape[1] - windowSteps):
                channelThresholdOff = np.ptp(
                    epoch[:, j:j + windowSteps],
                    axis=1) > self.Data.Results.threshold
                if np.sum(channelThresholdOff) != 0:
                    badChannelThreshold += channelThresholdOff

        # correct for bridges
        badChannelBridge = np.zeros(epoch.shape[0], dtype=int)
        if self.Data.Specs.CheckboxBridge.GetValue():
            corrMatrix = np.where(np.corrcoef(epoch) > .99999)
            if epoch.shape[0] != corrMatrix[0].shape[0]:
                corrID = np.unique(
                    [corrMatrix[0][m]
                     for m in range(corrMatrix[0].shape[0])
                     if corrMatrix[0][m] != corrMatrix[1][m]])
                badChannelBridge[corrID] += 1

        # correct for alpha
        badChannelAlpha = np.zeros(epoch.shape[0], dtype=int)
        if self.Data.Specs.CheckboxAlpha.GetValue():
            ps = np.abs(np.fft.rfft(epoch))**2  # **2 for power specturm
            freq = np.linspace(
                0, self.Data.Results.sampleRate / 2, ps.shape[1])
            alphaFreq = [
                a for a in [b for b, f in enumerate(freq) if f > 7.5]
                if freq[a] < 12.5]
            alphaPower = ps[:, alphaFreq].sum(axis=1)
            alphaID = np.where(
                alphaPower > alphaPower.mean() +
                alphaPower.std() * 10)[0]
            if alphaID.shape[0] != 0:
                badChannelAlpha[alphaID] += 1

        badChannelIDThreshold = np.where(badChannelThreshold != 0)
        badChannelIDBridge = np.where(badChannelBridge != 0)
        badChannelIDAlpha = np.where(badChannelAlpha != 0)

        minmax = [0, 0]
        for j, c in enumerate(epoch):
            if j in badChannelIDThreshold:
                color = 'r'
            elif j in badChannelIDBridge:
                color = 'b'
            elif j in badChannelIDAlpha:
                color = 'g'
            else:
                color = 'gray'
            lines = axes.plot(xaxis, c / sizer - j, color)
            ydata = lines[0].get_ydata()
            lineMin = ydata.min()
            lineMax = ydata.max()
            if minmax[0] > lineMin:
                minmax[0] = lineMin
            if minmax[1] < lineMax:
                minmax[1] = lineMax

        delta = np.abs(minmax).sum() * .01
        minmax = [minmax[0] - delta, minmax[1] + delta]

        axes.set_ylim(minmax)
        axes.get_yaxis().set_visible(False)
        axes.vlines(0, minmax[0], minmax[1], linestyles='dotted')

        self.figure.subplots_adjust(left=0.03,
                                    bottom=0.03,
                                    right=0.98,
                                    top=0.97,
                                    wspace=0.20,
                                    hspace=0.24)
        self.canvas.draw()


class EpochMarkerDetail(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        newFigure(self, showDetailedEpochs=True)

    def update(self, markerValue, shiftView=0):
        self.figure.clear()
        self.shiftView = shiftView
        self.markerValue = markerValue
        self.id2Show = np.where(
            self.Data.Results.markers == self.markerValue)[0]
        if self.CheckboxEpochs.IsChecked():
            self.id2Show = [
                i for i in self.id2Show if i in self.Data.Results.badID]

        preEpoch = float(self.Data.Specs.PreEpoch.GetValue())
        postEpoch = float(self.Data.Specs.PostEpoch.GetValue())
        samplingPoints = self.Data.Results.epochs.shape[2]
        labelsChannel = self.Data.Datasets[0].labelsChannel

        xaxis = [int(1.0 * i * (preEpoch + postEpoch) /
                     samplingPoints - preEpoch) for i in range(samplingPoints)]

        # Compute number of subplots needed
        if len(self.id2Show) < 6:
            tiles = len(self.id2Show)
            hPlots, vPlots = findSquare(len(self.id2Show))
        else:
            tiles = 6
            vPlots = 3
            hPlots = 2

        # Draw the epochs
        for k, i in enumerate(range(shiftView, tiles + shiftView)):
            axes = self.figure.add_subplot(vPlots, hPlots, k + 1)
            if i < len(self.id2Show):
                epochID = self.id2Show[i]
                epoch = self.Data.Orig.epochs[epochID]

                sizer = np.sqrt(np.sum(np.ptp(epoch, axis=1) / epoch.shape[0]))

                minmax = [0, 0]
                for j, c in enumerate(epoch):
                    if self.Data.Results.badEpochThreshold[epochID][j]:
                        color = 'r'
                        axes.text(postEpoch, c[-1] / sizer - j,
                                  labelsChannel[j], color='r')
                    elif self.Data.Results.badEpochBridge[epochID][j]:
                        color = 'b'
                        axes.text(postEpoch, c[-1] / sizer - j,
                                  labelsChannel[j], color='b')
                    elif self.Data.Results.badEpochAlpha[epochID][j]:
                        color = 'g'
                        axes.text(postEpoch, c[-1] / sizer - j,
                                  labelsChannel[j], color='g')
                    else:
                        color = 'gray'
                    lines = axes.plot(xaxis, c / sizer - j, color)
                    ydata = lines[0].get_ydata()
                    lineMin = ydata.min()
                    lineMax = ydata.max()
                    if minmax[0] > lineMin:
                        minmax[0] = lineMin
                    if minmax[1] < lineMax:
                        minmax[1] = lineMax

                delta = np.abs(minmax).sum() * .01
                minmax = [minmax[0] - delta, minmax[1] + delta]

                axes.set_ylim(minmax)
                axes.get_yaxis().set_visible(False)
                axes.title.set_text('Epoch: %s' % epochID)
                axes.vlines(0, minmax[0], minmax[1], linestyles='dotted')

        self.figure.subplots_adjust(left=0.03,
                                    bottom=0.03,
                                    right=0.98,
                                    top=0.97,
                                    wspace=0.20,
                                    hspace=0.24)
        self.canvas.draw()

    def updateFigure(self, event):
        if self.Data.Datasets != []:
            self.Data.EpochMarkerDetail.update(
                self.Data.EpochMarkerDetail.markerValue)
        event.Skip()

    def shiftViewLeft(self, event):
        if self.Data.Datasets != []:
            if self.Data.EpochMarkerDetail.shiftView != 0:
                viewShift = self.Data.EpochMarkerDetail.shiftView - 6
                self.Data.EpochMarkerDetail.update(
                    self.Data.EpochMarkerDetail.markerValue, viewShift)
        event.Skip()

    def shiftViewRight(self, event):
        if self.Data.Datasets != []:
            if self.Data.EpochMarkerDetail.shiftView + 6 \
                    < len(self.Data.EpochMarkerDetail.id2Show):
                viewShift = self.Data.EpochMarkerDetail.shiftView + 6
                self.Data.EpochMarkerDetail.update(
                    self.Data.EpochMarkerDetail.markerValue, viewShift)
        event.Skip()


def newFigure(self, showGrid=False, showGFP=False, showGMD=False,
              showDetailedEpochs=False):
    self.figure = plt.figure(facecolor=(0.95, 0.95, 0.95))
    self.canvas = FigureCanvas(self, wx.ID_ANY, self.figure)
    self.toolbar = NavigationToolbar(self.canvas)

    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

    self.hbox = wx.BoxSizer(wx.HORIZONTAL)
    flags = wx.ALIGN_LEFT | wx.ALL | wx.ALIGN_CENTER_VERTICAL

    if showGrid:
        self.CheckboxGrid = wx.CheckBox(self, wx.ID_ANY, 'Show Grid')
        self.CheckboxGrid.SetValue(True)
        self.hbox.Add(self.CheckboxGrid, 0, border=3, flag=flags)
        wx.EVT_CHECKBOX(
            self.CheckboxGrid, self.CheckboxGrid.Id, self.updateFigure)

    if showGFP:
        self.CheckboxGFP = wx.CheckBox(self, wx.ID_ANY, 'Show GFP')
        self.CheckboxGFP.SetValue(True)
        self.hbox.Add(self.CheckboxGFP, 0, border=3, flag=flags)
        wx.EVT_CHECKBOX(
            self.CheckboxGFP, self.CheckboxGFP.Id, self.updateFigure)

    if showGMD:
        self.CheckboxGMD = wx.CheckBox(self, wx.ID_ANY, 'Show GMD')
        self.CheckboxGMD.SetValue(True)
        self.hbox.Add(self.CheckboxGMD, 0, border=3, flag=flags)
        wx.EVT_CHECKBOX(
            self.CheckboxGMD, self.CheckboxGMD.Id, self.updateFigure)

    if showDetailedEpochs:
        self.CheckboxEpochs = wx.CheckBox(self, wx.ID_ANY,
                                          'Show only dropped Epochs')
        self.CheckboxEpochs.SetValue(True)
        self.hbox.Add(self.CheckboxEpochs, 0, border=3, flag=flags)
        wx.EVT_CHECKBOX(
            self.CheckboxEpochs, self.CheckboxEpochs.Id, self.updateFigure)

        self.goLeftButton = wx.Button(self, wx.ID_ANY, "<<")
        self.goRightButton = wx.Button(self, wx.ID_ANY, ">>")
        wx.EVT_BUTTON(self.goLeftButton, self.goLeftButton.Id,
                      self.shiftViewLeft)
        wx.EVT_BUTTON(self.goRightButton, self.goRightButton.Id,
                      self.shiftViewRight)
        self.hbox.Add(self.goLeftButton, 0, border=3, flag=flags)
        self.hbox.Add(self.goRightButton, 0, border=3, flag=flags)

    self.sizer.Add(self.hbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)

    self.sizer.Add(self.toolbar, 0, wx.EXPAND)
    self.SetSizer(self.sizer)
    self.Fit()


def findSquare(number):
    if number == 0:
        return 1, 1
    else:
        s1 = int(np.round(np.sqrt(number)))
        s2 = int(np.ceil(1.0 * number / s1))
        return s1, s2


def getXaxis(Results):
    stepSize = (Results.preEpoch + Results.postEpoch) / \
        (Results.preFrame + Results.postFrame)
    xaxis = [int(i * stepSize - Results.preEpoch)
             for i in range(Results.preFrame + Results.postFrame)]
    return xaxis
