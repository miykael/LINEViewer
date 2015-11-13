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

    def showGrid(self, event):
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
        newFigure(self, showGrid=True)

        # Figure events
        self.canvas.mpl_connect('button_press_event', self.zoomInDetailedGFP)

    def update(self, Results):

        if self.Data.Datasets == []:
            newFigure(self, showGrid=True)
        else:
            self.figure.clear()
            figureShape = findSquare(Results.uniqueMarkers.shape[0])
            xaxis = getXaxis(Results)
            for i, g in enumerate(Results.avgGFP):
                axes = self.figure.add_subplot(figureShape[0],
                                               figureShape[1],
                                               i + 1)
                axes.plot(xaxis, Results.avgGFP[i], 'b')
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

    def showGrid(self, event):
        if self.Data.Datasets != []:
            self.Data.GFPDetailed.update(self.Data.Results)
        event.Skip()

    def zoomInDetailedGFP(self, event):
        ax = event.inaxes
        if ax is None:
            return
        if event.button is 1:
            if event.dblclick:
                subplotID = event.inaxes.get_subplotspec().num1
                markerID = self.Data.Results.uniqueMarkers[subplotID]

                # On left click, zoom the selected axes
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

        corrMatrix = np.where(np.abs(np.corrcoef(epoch)) > .999)
        corrID = np.unique([corrMatrix[0][m]
                            for m in range(corrMatrix[0].shape[0])
                            if corrMatrix[0][m] != corrMatrix[1][m]])

        ps = np.abs(np.fft.rfft(epoch))**2  # **2 for power specturm
        freq = np.linspace(0, 512. / 2, ps.shape[1])
        alphaFreq = [a for a in [b for b, f in enumerate(freq)
                                 if f > 7.5] if freq[a] < 12.5]
        alphaPower = ps[:, alphaFreq].sum(axis=1)
        alphaID = np.where(
            alphaPower > alphaPower.mean() + alphaPower.std() * 5)[0]

        minmax = [0, 0]
        for j, c in enumerate(epoch):
            if np.sum(c > 80.) != 0:
                color = 'r'
            elif j in corrID:
                color = 'b'
            elif j in alphaID:
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

        delta = np.abs(minmax).sum()*.01
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
        newFigure(self)

    def update(self, markerValue):
        epochs = self.Data.Results.epochs[
            np.where(self.Data.Results.markers == markerValue)]

        preEpoch = float(self.Data.Specs.PreEpoch.GetValue())
        postEpoch = float(self.Data.Specs.PostEpoch.GetValue())
        samplingPoints = epochs.shape[2]

        xaxis = [int(1.0 * i * (preEpoch + postEpoch) /
                     samplingPoints - preEpoch) for i in range(samplingPoints)]

        for i in range(6):
            axes = self.figure.add_subplot(3, 2, i + 1)
            sizer = np.sqrt(
                np.sum(np.ptp(epochs[i], axis=1) / epochs[i].shape[0]))

            corrMatrix = np.where(np.abs(np.corrcoef(epochs[i])) > .999)
            corrID = np.unique([corrMatrix[0][m]
                                for m in range(corrMatrix[0].shape[0])
                                if corrMatrix[0][m] != corrMatrix[1][m]])

            ps = np.abs(np.fft.rfft(epochs[i]))**2  # **2 for power specturm
            freq = np.linspace(0, 512. / 2, ps.shape[1])
            alphaFreq = [a for a in [b for b, f in enumerate(freq)
                                     if f > 7.5] if freq[a] < 12.5]
            alphaPower = ps[:, alphaFreq].sum(axis=1)
            alphaID = np.where(
                alphaPower > alphaPower.mean() + alphaPower.std() * 5)[0]

            minmax = [0, 0]
            for j, c in enumerate(epochs[i]):
                if np.sum(c > 80.) != 0:
                    color = 'r'
                elif j in corrID:
                    color = 'b'
                elif j in alphaID:
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

            delta = np.abs(minmax).sum()*.01
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


def newFigure(self, showGrid=False):
    self.figure = plt.figure(facecolor=(0.95, 0.95, 0.95))
    self.canvas = FigureCanvas(self, wx.ID_ANY, self.figure)
    self.toolbar = NavigationToolbar(self.canvas)

    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

    if showGrid:
        self.CheckboxGrid = wx.CheckBox(self, wx.ID_ANY, 'Show Grid')
        self.CheckboxGrid.SetValue(True)
        self.sizer.Add(self.CheckboxGrid, 0, wx.EXPAND)
        wx.EVT_CHECKBOX(self.CheckboxGrid, self.CheckboxGrid.Id, self.showGrid)

    self.sizer.Add(self.toolbar, 0, wx.EXPAND)
    self.SetSizer(self.sizer)
    self.Fit()


def findSquare(number):
    s1 = int(np.round(np.sqrt(number)))
    s2 = int(np.ceil(1.0 * number / s1))
    return s1, s2


def getXaxis(Results):
    stepSize = (Results.preEpoch + Results.postEpoch) / \
        (Results.preFrame + Results.postFrame)
    xaxis = [int(i * stepSize - Results.preEpoch)
             for i in range(Results.preFrame + Results.postFrame)]
    return xaxis
