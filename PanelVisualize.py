import wx
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar


class Overview(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        self.ParentFrame = ParentFrame
        newFigure(self)

    def update(self, Results):
        if self.Data.Datasets == []:
            newFigure(self)
        else:
            # Get relevant information
            self.figure.clear()
            labelsChannel = np.copy(self.Data.Orig.labelsChannel)
            if hasattr(self.Data.Results, 'collapsedMarkers'):
                markers = self.Data.Results.collapsedMarkers
            else:
                markers = np.copy(self.Data.Orig.markers)
            matrixThreshold = np.copy(self.Data.Results.matrixThreshold)
            matrixBridge = np.copy(self.Data.Results.matrixBridge)
            badBlinkEpochs = np.copy(self.Data.Results.badBlinkEpochs)

            # Check for broken Epochs; if 25% of channels are over threshold
            brokenID = np.where(matrixThreshold.sum(axis=1) >
                                matrixThreshold.shape[1] * 0.2)[0]
            matrixThreshold[brokenID] *= False
            matrixBridge[brokenID] *= False
            badBlinkEpochs[brokenID] *= False

            matrixBad = matrixThreshold + matrixBridge
            badChannelsID = np.where(matrixBad.sum(axis=0))[0]
            badChannelsLabel = ['Broken', 'Blink']
            badChannelsLabel.extend(labelsChannel[badChannelsID])

            # Get distribution of channels
            distChannelThreshold = [0, 0]
            distChannelBridge = [0, 0]
            distChannelThreshold.extend(
                matrixThreshold[:, badChannelsID].sum(axis=0))
            distChannelBridge.extend(
                matrixBridge[:, badChannelsID].sum(axis=0))
            distChannelBroken = [len(brokenID), 0] + [0] * len(badChannelsID)
            distChannelBlink = [0, badBlinkEpochs.sum()] + \
                [0] * len(badChannelsID)

            # Get distribution of markers
            markerIDBroken = list(brokenID)
            markerIDThreshold = list(
                np.where(matrixThreshold.sum(axis=1).astype('bool'))[0])
            markerIDBridge = list(
                np.where(matrixBridge.sum(axis=1).astype('bool'))[0])
            markerIDBridge = [
                m for m in markerIDBridge if m not in markerIDThreshold]
            markerIDBlink = list(np.where(badBlinkEpochs)[0])
            markerIDBlink = [
                m for m in markerIDBlink
                if m not in markerIDThreshold + markerIDBridge]

            uniqueMarkers = np.unique(markers)
            if self.Data.markers2hide != []:
                uniqueMarkers = np.array([u for u in uniqueMarkers
                                          if u not in self.Data.markers2hide])

            distMarkerBroken = [
                list(markers[markerIDBroken]).count(u)
                for u in uniqueMarkers]
            distMarkerThreshold = [
                list(markers[markerIDThreshold]).count(u)
                for u in uniqueMarkers]
            distMarkerBridge = [
                list(markers[markerIDBridge]).count(u) for u in uniqueMarkers]
            distMarkerBlink = [
                list(markers[markerIDBlink]).count(u) for u in uniqueMarkers]
            distMarkerOK = [
                [m for i, m in enumerate(markers)
                 if i not in markerIDThreshold + markerIDBridge +
                 markerIDBlink + markerIDBroken].count(u)
                for u in uniqueMarkers]

            # Create bad channel histogram
            axes = self.figure.add_subplot(2, 1, 1)
            axes.clear()

            nChannels = np.arange(len(badChannelsLabel))
            axes.bar(nChannels, distChannelBroken, 0.75, color='c',
                     label='Broken', alpha=0.5)
            axes.bar(nChannels, distChannelThreshold, 0.75, color='r',
                     label='Threshold', alpha=0.5)
            axes.bar(nChannels, distChannelBridge, 0.75, color='b',
                     bottom=distChannelThreshold, label='Bridge',
                     alpha=0.5)
            axes.bar(nChannels, distChannelBlink, 0.75, color='m',
                     bottom=np.sum(np.vstack((distChannelThreshold,
                                              distChannelBridge)), axis=0),
                     label='Blink', alpha=0.5)

            axes.title.set_text(
                'Channel Overview - %s Epochs Total' % markers.shape[0])
            axes.grid(True, axis='y')
            axes.set_xlabel('Channel')
            axes.set_ylabel('Epochs')
            axes.set_xticks(nChannels + .75 / 2)
            axes.set_xticklabels(badChannelsLabel)

            # Write percentage of outliers in channel overview plot
            ticks = axes.get_xticks()
            distOutliersChannel = np.vstack([distChannelThreshold,
                                             distChannelBridge,
                                             distChannelBroken,
                                             distChannelBlink]).sum(axis=0)
            distOutliersChannel = 1. * distOutliersChannel / markers.shape[0]

            for i, d in enumerate(distOutliersChannel):
                percentage = np.round(distOutliersChannel[i] * 100., 1)
                if percentage != 0:
                    axes.text(
                        ticks[i], 0.8,
                        '{0}%'.format(str(percentage)),
                        horizontalalignment='center',
                        verticalalignment='bottom', rotation=90)

            # Create bad marker histogram
            axes = self.figure.add_subplot(2, 1, 2)
            axes.clear()

            nMarker = np.arange(uniqueMarkers.shape[0])
            axes.bar(nMarker, distMarkerOK, 0.75, color='g',
                     label='OK', alpha=0.5)
            axes.bar(nMarker, distMarkerThreshold, 0.75, color='r',
                     bottom=distMarkerOK, label='Threshold', alpha=0.5)
            axes.bar(nMarker, distMarkerBridge, 0.75, color='b',
                     bottom=np.sum(np.vstack((distMarkerOK,
                                              distMarkerThreshold)), axis=0),
                     label='Bridge', alpha=0.5)
            axes.bar(nMarker, distMarkerBlink, 0.75, color='m',
                     bottom=np.sum(np.vstack((distMarkerOK,
                                              distMarkerThreshold,
                                              distMarkerBridge)), axis=0),
                     label='Blink', alpha=0.5)
            axes.bar(nMarker, distMarkerBroken, 0.75, color='c',
                     bottom=np.sum(np.vstack((distMarkerOK,
                                              distMarkerThreshold,
                                              distMarkerBridge,
                                              distMarkerBlink)), axis=0),
                     label='Blink', alpha=0.5)

            axes.title.set_text('Marker Overview')
            axes.grid(True, axis='y')
            axes.set_xlabel('Marker')
            axes.set_ylabel('Epochs')
            axes.set_xticks(nMarker + .75 / 2)
            axes.set_xticklabels(uniqueMarkers.astype('str'))

            # Write percentage of outliers in marker overview plot
            ticks = axes.get_xticks()
            distOutliersMarker = np.vstack([distMarkerThreshold,
                                            distMarkerBridge,
                                            distMarkerBroken,
                                            distMarkerBlink]).sum(axis=0)
            distOutliersMarker = np.divide(
                distOutliersMarker.astype('float'),
                distOutliersMarker + distMarkerOK)

            for i, d in enumerate(distOutliersMarker):
                percentage = np.round(distOutliersMarker[i] * 100., 1)
                if percentage != 0:
                    axes.text(
                        ticks[i], 0.8,
                        '{0}%'.format(str(percentage)),
                        horizontalalignment='center',
                        verticalalignment='bottom', rotation=90)

            # Adjust and draw histograms
            self.figure.subplots_adjust(left=0.05,
                                        bottom=0.05,
                                        right=0.95,
                                        top=0.95,
                                        wspace=0.20,
                                        hspace=0.20)
            self.canvas.draw()


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
            avgGFP = np.array(
                Results.avgGFP)[:, Results.preCut -
                                Results.preFrame:Results.preCut +
                                Results.postFrame]
            plt.plot(xaxis, np.transpose(avgGFP))
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
                self.ParentFrame.SetSelection(2)
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
            self.Data.Overview.update(self)
            self.update(self.Data.Results)
            self.Data.EpochDetail.update([])
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
            avgGFP = np.array(Results.avgGFP)[
                :, Results.preCut - Results.preFrame:Results.preCut +
                Results.postFrame]
            avgGMD = np.array(Results.avgGMD)[
                :, Results.preCut - Results.preFrame:Results.preCut +
                Results.postFrame]
            for i, g in enumerate(Results.avgGFP):
                axes = self.figure.add_subplot(figureShape[0],
                                               figureShape[1],
                                               i + 1)
                if self.CheckboxGFP.IsChecked():
                    axes.plot(xaxis, avgGFP[i], 'b')
                if self.CheckboxGMD.IsChecked():
                    axes.plot(xaxis, avgGMD[i], 'r')
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
            self.update(self.Data.Results)
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
                self.Data.EpochDetail.CheckboxMarkers.SetValue(False)
                self.Data.EpochDetail.update(markerID)
                self.ParentFrame.SetSelection(3)
                self.canvas.ReleaseMouse()


class EpochDetail(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        newFigure(self, showDetailedEpochs=True)

        # Figure events
        self.canvas.callbacks.connect('pick_event', self.onPick)

    def update(self, markerValue, shiftView=0):
        self.figure.clear()
        self.shiftView = shiftView
        self.markerValue = markerValue
        self.id2Show = np.where(
            self.Data.Results.markers == self.markerValue)[0]
        if self.markerValue == []:
            self.CheckboxMarkers.SetValue(True)
            self.id2Show = np.arange(self.Data.Results.markers.shape[0])
        if self.CheckboxEpochs.IsChecked():
            self.id2Show = [
                i for i in self.id2Show
                if i in np.where(self.Data.Results.badID)[0]]

        self.labelsChannel = self.Data.Datasets[0].labelsChannel
        Results = self.Data.Results
        samplingPoints = Results.epochs.shape[2]
        preStimuli = 1000. / (Results.sampleRate /
                              Results.preCut)
        postStimuli = 1000. / (Results.sampleRate /
                               Results.postCut)
        xaxis = [int(1.0 * i * (preStimuli + postStimuli) /
                     samplingPoints - preStimuli)
                 for i in range(samplingPoints)]

        # Get Visualization layout
        layout = self.ComboLayout.GetValue()
        vPlots = int(layout[-1])
        hPlots = int(layout[0])
        self.tiles = vPlots * hPlots

        # Draw the epochs
        for k, i in enumerate(range(shiftView, self.tiles + shiftView)):
            axes = self.figure.add_subplot(vPlots, hPlots, k + 1)
            if i < len(self.id2Show):
                epochID = self.id2Show[i]
                markerID = self.Data.Results.markers[epochID]
                epoch = self.Data.Orig.epochs[epochID]

                sizer = np.sqrt(
                    np.sum(np.ptp(epoch, axis=1) / epoch.shape[0])) * 2
                modulator = float(self.ComboAmplitude.GetValue()[:-1])
                sizer *= modulator / 100.

                # Highlight the epoch
                preEpoch = float(self.Data.Specs.PreEpoch.GetValue())
                postEpoch = float(self.Data.Specs.PostEpoch.GetValue())
                axes.axvspan(-preEpoch, postEpoch, facecolor='g', alpha=0.1)

                # Check if the epoch is broken
                isBroken = Results.matrixThreshold[
                    epochID].sum() > (Results.matrixThreshold.shape[1] * 0.2)

                # Draw blink periods in figure
                if Results.matrixBlink[epochID].sum() != 0:
                    blinkEpoch = np.append(Results.matrixBlink[epochID], False)
                    blinkPhase = np.where(blinkEpoch[:-1] != blinkEpoch[1:])[0]
                    color = 'm'
                    for i in range(blinkPhase.shape[0] / 2):
                        axes.axvspan(xaxis[blinkPhase[2 * i]],
                                     xaxis[blinkPhase[2 * i + 1]],
                                     facecolor=color, alpha=0.2)
                    stimuliSegment = Results.matrixBlink[
                        epochID, Results.preCut -
                        Results.preFrame:Results.preCut + Results.postFrame]
                    if stimuliSegment.sum() != 0:
                        axes.title.set_fontweight('bold')
                        axes.title.set_color(color)

                # Draw single channels
                minmax = [0, 0]
                for j, c in enumerate(epoch):
                    if isBroken:
                        color = 'c'
                        axes.title.set_fontweight('bold')
                        axes.title.set_color(color)
                    elif Results.matrixThreshold[epochID][j]:
                        color = 'r'
                        axes.text(postStimuli + 1, c[-1] / sizer - j,
                                  self.labelsChannel[j], color=color)
                        axes.title.set_fontweight('bold')
                        axes.title.set_color(color)
                    elif Results.matrixBridge[epochID][j]:
                        color = 'b'
                        axes.text(postStimuli + 1, c[-1] / sizer - j,
                                  self.labelsChannel[j], color=color)
                        axes.title.set_fontweight('bold')
                        axes.title.set_color(color)
                    else:
                        color = 'gray'
                    lines = axes.plot(xaxis, c / sizer - j, color, picker=1)
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
                axes.title.set_text('Marker %s - Epoch %s' % (markerID,
                                                              epochID + 1))
                axes.vlines(0, minmax[0], minmax[1], linestyles='dotted')

        currentPage = (self.shiftView / self.tiles) + 1
        totalPage = (len(self.id2Show) - 1) / self.tiles + 1
        if totalPage == 0:
            currentPage = 0

        self.TextPages.SetLabel('Page: %s/%s   ' % (currentPage, totalPage))

        self.figure.subplots_adjust(left=0.03,
                                    bottom=0.03,
                                    right=0.98,
                                    top=0.97,
                                    wspace=0.20,
                                    hspace=0.24)
        self.canvas.draw()

    def updateFigure(self, event):
        if self.Data.Datasets != []:
            if self.CheckboxMarkers.GetValue():
                self.markerValue = []
            self.update(self.markerValue)
        event.Skip()

    def shiftViewLeft(self, event):
        if self.Data.Datasets != []:
            if self.shiftView != 0:
                viewShift = self.shiftView - self.tiles
                self.update(self.markerValue, viewShift)
        event.Skip()

    def shiftViewRight(self, event):
        if self.Data.Datasets != []:
            if self.shiftView + self.tiles \
                    < len(self.id2Show):
                viewShift = self.shiftView + self.tiles
                self.update(self.markerValue, viewShift)
        event.Skip()

    def onPick(self, event):
        # only if left mouse button is pressed
        if event.mouseevent.button == 1:
            event.artist.set_color('black')
            linenumber = int(event.artist.get_label()[5:])
            xValue = 1000. * self.Data.Results.postCut / \
                self.Data.Results.sampleRate + 1
            yValue = event.artist.get_data()[1][-1]
            event.artist.axes.text(xValue, yValue,
                                   self.labelsChannel[linenumber],
                                   color='black')
            self.canvas.ReleaseMouse()
            self.canvas.draw()

    def updateLayout(self, event):
        if hasattr(self, 'markerValue'):
            self.update(self.markerValue)
        event.Skip()

    def updateSize(self, event):
        if hasattr(self, 'markerValue'):
            self.update(self.markerValue, self.shiftView)
        event.Skip()


class EpochSummary(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        newFigure(self)

    def update(self, markerValue):
        self.figure.clear()
        epochs = self.Data.Results.epochs[
            np.where(self.Data.Results.markers == markerValue)]
        epoch = epochs.mean(axis=0)

        preEpoch = float(self.Data.Specs.PreEpoch.GetValue())
        postEpoch = float(self.Data.Specs.PostEpoch.GetValue())
        samplingPoints = epoch.shape[1]

        xaxis = [int(1.0 * i * (preEpoch + postEpoch) /
                     samplingPoints - preEpoch) for i in range(samplingPoints)]

        axes = self.figure.add_subplot(1, 1, 1)
        sizer = np.sqrt(np.sum(np.ptp(epoch, axis=1) / epoch.shape[0])) * 2

        # detect threshold
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

        # detect bridge
        badChannelBridge = np.zeros(epoch.shape[0], dtype=int)
        if self.Data.Specs.CheckboxBridge.GetValue():
            corrMatrix = np.where(np.corrcoef(epoch) > .99999)
            if epoch.shape[0] != corrMatrix[0].shape[0]:
                corrID = np.unique(
                    [corrMatrix[0][m]
                     for m in range(corrMatrix[0].shape[0])
                     if corrMatrix[0][m] != corrMatrix[1][m]])
                badChannelBridge[corrID] += 1

        badChannelIDThreshold = np.where(badChannelThreshold != 0)
        badChannelIDBridge = np.where(badChannelBridge != 0)

        minmax = [0, 0]
        for j, c in enumerate(epoch):
            if j in badChannelIDThreshold:
                color = 'r'
            elif j in badChannelIDBridge:
                color = 'b'
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
        self.TextLayout = wx.StaticText(self, wx.ID_ANY, label='Layout:')
        self.ComboLayout = wx.ComboBox(self, style=wx.CB_READONLY,
                                       choices=['1x1', '1x2', '2x2', '2x3'])
        self.ComboLayout.SetSelection(2)
        wx.EVT_COMBOBOX(self.ComboLayout, self.ComboLayout.Id,
                        self.updateLayout)
        self.hbox.Add(self.TextLayout, 0, border=3, flag=flags)
        self.hbox.Add(self.ComboLayout, 0, border=3, flag=flags)

        self.TextSizer = wx.StaticText(self, wx.ID_ANY, label='Amplitude:')
        self.ComboAmplitude = wx.ComboBox(
            self, style=wx.CB_READONLY,
            choices=['750%', '500%', '400%', '300%', '200%', '150%',
                     '125%', '100%', '90%', '80%', '70%', '60%',
                     '50%', '40%', '30%', '20%', '10%', '5%'])
        self.ComboAmplitude.SetSelection(7)
        wx.EVT_COMBOBOX(self.ComboAmplitude, self.ComboAmplitude.Id,
                        self.updateSize)
        self.hbox.Add(self.TextSizer, 0, border=3, flag=flags)
        self.hbox.Add(self.ComboAmplitude, 0, border=3, flag=flags)

        self.TextPages = wx.StaticText(self, wx.ID_ANY, label='Page: 0/0 ')
        self.goLeftButton = wx.Button(self, wx.ID_ANY, "<<")
        self.goRightButton = wx.Button(self, wx.ID_ANY, ">>")
        wx.EVT_BUTTON(self.goLeftButton, self.goLeftButton.Id,
                      self.shiftViewLeft)
        wx.EVT_BUTTON(self.goRightButton, self.goRightButton.Id,
                      self.shiftViewRight)
        self.hbox.Add(self.TextPages, 0, border=3, flag=flags)
        self.hbox.Add(self.goLeftButton, 0, border=3, flag=flags)
        self.hbox.Add(self.goRightButton, 0, border=3, flag=flags)

        self.CheckboxEpochs = wx.CheckBox(self, wx.ID_ANY,
                                          'Outliers only')
        self.CheckboxEpochs.SetValue(True)
        self.hbox.Add(self.CheckboxEpochs, 0, border=3, flag=flags)
        wx.EVT_CHECKBOX(
            self.CheckboxEpochs, self.CheckboxEpochs.Id, self.updateFigure)

        self.CheckboxMarkers = wx.CheckBox(self, wx.ID_ANY,
                                           'All Markers')
        self.CheckboxMarkers.SetValue(True)
        self.hbox.Add(self.CheckboxMarkers, 0, border=3, flag=flags)
        wx.EVT_CHECKBOX(
            self.CheckboxMarkers, self.CheckboxMarkers.Id, self.updateFigure)

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


"""
TODO:

VISUAL:
blinks should only be in 3rd quadrant of channels
perhaps check that blink periods are at least xx elements long?
check that "Channel Overview" displays the right values if markers are hidden
Bridges are not shown in Epoch - Detailed
make sure that right number of epochs are shown in GFP_Detailed
make sure that right epochs are shown in Epoch_Detailed
double click to select or deselect epochs (decide which color it should be shown in overview?)


OUTLIER:
ceate a sliding view window or a popup "Manual Rejection"? - [r] for reject or unreject and change size of window etc.?
how is impedence calculated?
https://sites.google.com/site/cartoolcommunity/user-s-guide/analysis/artefacts-rejection-single-subjects-averages
Cardiac artifact - http://www.slideshare.net/SudhakarMarella/eeg-artifacts-15175461
Pulse artefact
pop of electrode
Electrode movement artifact (oscillation)
flat electordes (perhaps if STD is very low or almost zero?)
muscle artifact (perhaps high STD over certain time period)
perhaps something like common movement - if suddenly all electrodes spike in a same way

OUTPUT
write eph, marker and tva files (also marker for origin)
write or load tvas
"""
