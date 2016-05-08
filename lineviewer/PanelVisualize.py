import wx
import numpy as np
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
            labelsChannel = np.copy(self.Data.labelsChannel)
            if hasattr(self.Data.Results, 'collapsedMarkers'):
                markers = self.Data.Results.collapsedMarkers
            else:
                markers = np.copy(self.Data.Results.markers)

            # Correct for selected epochs
            matrixSelected = np.copy(self.Data.Results.matrixSelected)

            # Disregard outliers if they are selected as being ok
            self.Data.Results.matrixBridge[
                np.where(matrixSelected == 'ok_bridge')[0]] = False
            self.Data.Results.matrixBlink[
                np.where(matrixSelected == 'ok_blink')[0]] = False
            self.Data.Results.matrixThreshold[
                np.where(matrixSelected == 'ok_thresh')[0]] = False

            matrixBridge = np.copy(self.Data.Results.matrixBridge)
            matrixBlink = np.copy(self.Data.Results.matrixBlink)
            matrixThreshold = np.copy(self.Data.Results.matrixThreshold)

            # Check for broken Epochs; if 25% of channels are over threshold
            brokenID = np.where(matrixThreshold.sum(axis=1) >
                                matrixThreshold.shape[1] * 0.9)[0]
            matrixThreshold[brokenID] *= False
            matrixBridge[brokenID] *= False
            matrixBlink[brokenID] *= False

            # Get distribution of channels
            distChannelSelected = []
            distChannelBroken = []
            distChannelBlink = []
            distChannelThreshold = []
            distChannelBridge = []
            badChannelsLabel = []

            # Disregard any epochs of hidden markers
            markers2hide = [True if m in self.Data.markers2hide else False
                            for m in markers]
            brokenID = [b for b in brokenID
                        if b not in np.where(markers2hide)[0]]
            matrixSelected[np.where(markers2hide)] = 'ok_normal'
            unhiddenEpochID = np.where(np.invert(markers2hide))[0].tolist()

            matrixBad = matrixThreshold + matrixBridge
            badChannelsID = np.where(matrixBad[unhiddenEpochID].sum(axis=0))[0]

            tmpThreshold = matrixThreshold[:, badChannelsID]
            tmpThreshold = tmpThreshold[unhiddenEpochID]
            tmpBridge = matrixBridge[:, badChannelsID]
            tmpBridge = tmpBridge[unhiddenEpochID]

            # Count how many acceptable epochs are selected as outliers
            nSelectedOutliers = np.in1d(matrixSelected, 'selected').sum()

            if nSelectedOutliers != 0:
                distChannelSelected.extend([nSelectedOutliers])
                distChannelBroken.extend([0])
                distChannelBlink.extend([0])
                distChannelThreshold.extend([0])
                distChannelBridge.extend([0])
                badChannelsLabel.extend(['Outliers'])
            if len(brokenID) != 0:
                distChannelSelected.extend([0])
                distChannelBroken.extend([len(brokenID)])
                distChannelBlink.extend([0])
                distChannelThreshold.extend([0])
                distChannelBridge.extend([0])
                badChannelsLabel.extend(['Broken'])
            if matrixBlink.sum() != 0:
                distChannelSelected.extend([0])
                distChannelBroken.extend([0])
                distChannelBlink.extend([matrixBlink.sum()])
                distChannelThreshold.extend([0])
                distChannelBridge.extend([0])
                badChannelsLabel.extend(['Blink'])

            distChannelThreshold.extend(tmpThreshold.sum(axis=0))
            distChannelBridge.extend(tmpBridge.sum(axis=0))
            distChannelBroken.extend([0] * len(badChannelsID))
            distChannelBlink.extend([0] * len(badChannelsID))
            distChannelSelected.extend([0] * len(badChannelsID))
            badChannelsLabel.extend(labelsChannel[badChannelsID])

            # Get distribution of markers
            markerIDBroken = list(brokenID)
            markerIDThreshold = list(
                np.where(matrixThreshold.sum(axis=1).astype('bool'))[0])
            markerIDBridge = list(
                np.where(matrixBridge.sum(axis=1).astype('bool'))[0])
            markerIDBridge = [
                m for m in markerIDBridge if m not in markerIDThreshold]
            markerIDBlink = list(
                np.where(matrixBlink.sum(axis=1).astype('bool'))[0])
            markerIDBlink = [
                m for m in markerIDBlink
                if m not in markerIDThreshold + markerIDBridge]
            markerIDSelected = list(np.where(matrixSelected == 'selected')[0])

            uniqueMarkers = np.array(
                [m for m in np.unique(markers)
                 if m not in self.Data.markers2hide])

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
            distMarkerSelected = [
                list(markers[markerIDSelected]).count(u)
                for u in uniqueMarkers]
            distMarkerOK = [
                [m for i, m in enumerate(markers)
                 if i not in markerIDThreshold + markerIDBridge +
                 markerIDBlink + markerIDBroken].count(u)
                for u in uniqueMarkers]
            distMarkerOK = [m - distMarkerSelected[i]
                            for i, m in enumerate(distMarkerOK)]
            self.distMarkerOK = distMarkerOK

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
            axes.bar(nChannels, distChannelSelected, 0.75, color='#ff8c00',
                     label='Broken', alpha=0.5)

            distOutliersChannel = np.vstack([distChannelThreshold,
                                             distChannelBridge,
                                             distChannelBroken,
                                             distChannelBlink,
                                             distChannelSelected]).sum(axis=0)

            # Needed for verbose file
            self.Data.Results.OoutlierChannels = int(sum(distOutliersChannel))

            axes.title.set_text(
                'Channel Overview - %s Epochs Total (%s Outliers)'
                % (markers.shape[0], int(sum(distOutliersChannel))))

            axes.grid(True, axis='y')
            axes.set_ylabel('Epochs')
            axes.set_xticks(nChannels + .75 / 2)
            axes.set_xticklabels(badChannelsLabel, rotation=90)

            # Write percentage of outliers in channel overview plot
            distOutliersChannel = 1. * distOutliersChannel / markers.shape[0]
            ticks = axes.get_xticks()
            for i, d in enumerate(distOutliersChannel):
                percentage = np.round(distOutliersChannel[i] * 100., 1)
                if percentage != 0:
                    axes.text(
                        ticks[i], 0.8,
                        '{0}%'.format(str(percentage)),
                        horizontalalignment='center',
                        verticalalignment='bottom', rotation=90)

            # Y-axis should only use integers
            yticks = axes.get_yticks().astype('int')
            axes.set_yticks(np.unique(yticks))

            # Create bad marker histogram
            axes = self.figure.add_subplot(2, 1, 2)
            axes.clear()

            nMarker = np.arange(uniqueMarkers.shape[0])
            axes.bar(nMarker, distMarkerOK, 0.75, color='g',
                     label='OK', alpha=0.5)
            axes.bar(nMarker, distMarkerSelected, 0.75, color='#ff8c00',
                     bottom=distMarkerOK, label='Outliers', alpha=0.5)
            axes.bar(nMarker, distMarkerThreshold, 0.75, color='r',
                     bottom=np.sum(np.vstack((distMarkerOK,
                                              distMarkerSelected)), axis=0),
                     label='Threshold', alpha=0.5)
            axes.bar(nMarker, distMarkerBridge, 0.75, color='b',
                     bottom=np.sum(np.vstack((distMarkerOK,
                                              distMarkerSelected,
                                              distMarkerThreshold)), axis=0),
                     label='Bridge', alpha=0.5)
            axes.bar(nMarker, distMarkerBlink, 0.75, color='m',
                     bottom=np.sum(np.vstack((distMarkerOK,
                                              distMarkerSelected,
                                              distMarkerThreshold,
                                              distMarkerBridge)), axis=0),
                     label='Blink', alpha=0.5)
            axes.bar(nMarker, distMarkerBroken, 0.75, color='c',
                     bottom=np.sum(np.vstack((distMarkerOK,
                                              distMarkerSelected,
                                              distMarkerThreshold,
                                              distMarkerBridge,
                                              distMarkerBlink)), axis=0),
                     label='Broken', alpha=0.5)

            percentageBad = 1 - float(
                sum(distMarkerOK)) / self.Data.Results.okID.shape[0]
            nOutliers = int(
                self.Data.Results.okID.shape[0] - sum(distMarkerOK))
            axes.title.set_text(
                'Marker Overview - {0} Outliers [{1}%]'.format(
                    nOutliers, round(percentageBad * 100, 1)))
            axes.grid(True, axis='y')
            axes.set_ylabel('Epochs')
            axes.set_xticks(nMarker + .75 / 2)
            axes.set_xticklabels(uniqueMarkers.astype('str'))

            # Write percentage of outliers in marker overview plot
            distOutliersMarker = np.vstack([distMarkerThreshold,
                                            distMarkerBridge,
                                            distMarkerBroken,
                                            distMarkerBlink,
                                            distMarkerSelected]).sum(axis=0)
            distOutliersMarker = np.divide(
                distOutliersMarker.astype('float'),
                distOutliersMarker + distMarkerOK)

            ticks = axes.get_xticks()
            for i, d in enumerate(distOutliersMarker):
                percentage = 100 - np.round(distOutliersMarker[i] * 100., 1)
                axes.text(
                    ticks[i], 0.8,
                    '{0}%'.format(str(percentage)),
                    horizontalalignment='center',
                    verticalalignment='bottom', rotation=90)

            # Adjust and draw histograms
            self.figure.tight_layout()
            self.canvas.draw()

            # Save distributions for latter access
            dist = self.Data.Results
            dist.OnSelectedOutliers = nSelectedOutliers
            dist.OdistChannelThreshold = distChannelThreshold
            dist.OdistChannelBridge = distChannelBridge
            dist.OBroken = len(brokenID)
            dist.OBlink = matrixBlink.sum()
            dist.OpercentageChannels = distOutliersChannel
            dist.OxaxisChannel = labelsChannel[badChannelsID]

            dist.OoutlierEpochs = nOutliers
            dist.OdistMarkerOK = distMarkerOK
            dist.OdistMarkerThreshold = distMarkerThreshold
            dist.OdistMarkerBridge = distMarkerBridge
            dist.OdistMarkerBroken = distMarkerBroken
            dist.OdistMarkerBlink = distMarkerBlink
            dist.OdistMarkerSelected = distMarkerSelected
            dist.OpercentageMarker = distOutliersMarker
            dist.OxaxisMarker = uniqueMarkers.astype('str')


class GFPSummary(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        self.ParentFrame = ParentFrame
        newFigure(self, showGrid=True)

        # Figure events
        self.canvas.mpl_connect('button_press_event', self.gotoDetailGFP)

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

            # Which markers to show
            markers2show = np.array(
                [True if m not in self.Data.markers2hide else False
                 for m in Results.uniqueMarkers])

            plt.plot(xaxis, np.transpose(avgGFP[markers2show]))
            plt.xlabel('time [ms]')
            plt.ylabel('GFP')
            plt.title('GFP Overview')
            plt.legend(Results.uniqueMarkers[markers2show])
            self.figure.tight_layout()
            plt.grid(self.CheckboxGrid.IsChecked())
            self.canvas.draw()

    def gotoDetailGFP(self, event):
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
        else:
            self.canvas.ReleaseMouse()

    def updateFigure(self, event):
        if self.Data.Datasets != []:
            self.Data.Overview.update(self)
            self.update(self.Data.Results)
            self.Data.ERPSummary.update([])
            self.Data.EpochsDetail.update([])
        event.Skip()


class GFPDetail(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        self.ParentFrame = ParentFrame
        newFigure(self, showGrid=True, showGFP=True, showGMD=True)

        # Figure events
        self.canvas.mpl_connect('button_press_event', self.zoomInDetailGFP)

    def update(self, Results):

        if self.Data.Datasets == []:
            newFigure(self, showGrid=True, showGFP=True, showGMD=True)
        else:
            self.figure.clear()
            xaxis = getXaxis(Results)
            avgGFP = np.array(Results.avgGFP)[
                :, Results.preCut - Results.preFrame:Results.preCut +
                Results.postFrame]
            avgGMD = np.array(Results.avgGMD)[
                :, Results.preCut - Results.preFrame:Results.preCut +
                Results.postFrame]

            # Which markers to show
            markers2show = np.array(
                [True if m not in self.Data.markers2hide else False
                 for m in Results.uniqueMarkers])
            avgGFP = avgGFP[markers2show]
            avgGMD = avgGMD[markers2show]
            results2show = [r for i, r in enumerate(Results.avgGFP)
                            if markers2show[i]]
            shownMarkers = Results.uniqueMarkers[markers2show]

            figureShape = findSquare(len(shownMarkers))

            for i, g in enumerate(results2show):
                axes = self.figure.add_subplot(figureShape[0],
                                               figureShape[1],
                                               i + 1)
                if self.CheckboxGFP.IsChecked():
                    axes.plot(xaxis, avgGFP[i], 'b')
                if self.CheckboxGMD.IsChecked():
                    axes.plot(xaxis, avgGMD[i], 'r')
                nMarkers = self.Data.Overview.distMarkerOK[i]

                axes.title.set_text(
                    'Marker: %s [N=%s]' % (shownMarkers[i], nMarkers))
                axes.grid(self.CheckboxGrid.IsChecked())
            self.figure.tight_layout()
            self.canvas.draw()

    def updateFigure(self, event):
        if self.Data.Datasets != []:
            self.update(self.Data.Results)
        event.Skip()

    def zoomInDetailGFP(self, event):
        ax = event.inaxes
        if ax is None:
            return
        if event.dblclick:
            # On left click, zoom the selected axes
            if event.button is 1:
                subplotID = event.inaxes.get_subplotspec().num1
                markerID = self.Data.Results.uniqueMarkers[subplotID]
                self.Data.ERPSummary.update(markerID)

                comboMarker = self.Data.EpochsDetail.ComboMarkers
                selectionID = int(np.where(np.array(
                    comboMarker.GetItems()) == str(markerID))[0])
                comboMarker.SetSelection(selectionID)

                self.Data.EpochsDetail.update(markerID)
                self.ParentFrame.SetSelection(3)
            self.canvas.ReleaseMouse()


class ERPSummary(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        newFigure(self, showSummaryEpochs=True)

        # Figure events
        self.canvas.callbacks.connect('pick_event', self.onPick)

    def update(self, markerValue=[], shiftView=0):
        self.figure.clear()
        self.shiftView = shiftView
        self.markerValue = markerValue

        # Set correct markerList and selection
        self.allMarker = np.unique([
            m for m in self.Data.Results.markers
            if m not in self.Data.markers2hide])
        markerList = ['All   '] + self.allMarker.astype('str').tolist()
        self.ComboMarkers.SetItems(markerList)

        if self.markerValue == []:
            self.ComboMarkers.SetSelection(0)
        else:
            markerID = markerList.index(str(markerValue))
            self.shiftView = markerID - 1
            self.ComboMarkers.SetSelection(markerID)
            self.ComboLayout.SetValue('1x1')

        # Prepare Visualization
        self.labelsChannel = self.Data.Datasets[0].labelsChannel
        Results = self.Data.Results
        samplingPoints = Results.epochs.shape[2]
        preStimuli = 1000. / (float(Results.sampleRate) /
                              Results.preCut)
        postStimuli = 1000. / (float(Results.sampleRate) /
                               Results.postCut)
        xaxis = [int(float(i) * (preStimuli + postStimuli) /
                     samplingPoints - preStimuli)
                 for i in range(samplingPoints)]

        # Get Visualization layout
        layout = self.ComboLayout.GetValue()
        vPlots = int(layout[-1])
        hPlots = int(layout[0])
        self.tiles = vPlots * hPlots

        # Draw the average epochs
        for k, i in enumerate(range(self.shiftView,
                                    self.tiles + self.shiftView)):
            axes = self.figure.add_subplot(vPlots, hPlots, k + 1)

            if i < len(Results.avgEpochs):
                markerID = self.allMarker[i]
                epoch = Results.avgEpochs[i]
                sizer = np.sqrt(
                    np.sum(np.ptp(epoch, axis=1) / epoch.shape[0])) * 2
                modulator = float(self.ComboAmplitude.GetValue()[:-1])
                sizer *= modulator / 100.

                # Draw single channels
                minmax = [0, 0]
                for j, c in enumerate(epoch):
                    if self.ComboOverlay.GetValue() == 'Overlay':
                        delta = 0
                    else:
                        delta = j
                    color = 'gray'
                    lines = axes.plot(xaxis, c / sizer - delta, color,
                                      picker=1)
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
                axes.title.set_text('Marker %s' % markerID)
                axes.vlines(0, minmax[0], minmax[1], linestyles='dotted')

        currentPage = (self.shiftView / self.tiles) + 1
        totalPage = (len(Results.avgEpochs) - 1) / self.tiles + 1
        if totalPage == 0:
            currentPage = 0

        self.TextPages.SetLabel('Page: %s/%s   ' % (currentPage, totalPage))

        self.figure.tight_layout()
        self.canvas.draw()

    def onPick(self, event):

        # Only do something if left double click
        if event.mouseevent.dblclick and event.mouseevent.button == 1:

            # Print Line name and color it black if requested
            if event.artist.get_picker() == 1:
                event.artist.set_color('black')
                linenumber = int(event.artist.get_label()[5:])
                xValue = 1000. * self.Data.Results.postCut / \
                    self.Data.Results.sampleRate + 1
                yValue = event.artist.get_data()[1][-1]
                event.artist.axes.text(xValue, yValue,
                                       self.labelsChannel[linenumber],
                                       color='black')

            self.canvas.draw()
        if event.mouseevent.name == 'button_press_event':
            self.canvas.ReleaseMouse()

    def updateLayout(self, event):
        if hasattr(self, 'markerValue'):
            self.update([])
            self.ComboMarkers.SetSelection(0)
        event.Skip()

    def updateSize(self, event):
        if hasattr(self, 'markerValue'):
            self.update(self.markerValue, self.shiftView)
        event.Skip()

    def updateFigure(self, event):
        if self.Data.Datasets != []:
            markerList = self.ComboMarkers.GetItems()
            marker = markerList[self.ComboMarkers.GetSelection()]
            if 'All' in marker:
                markerValue = []
            else:
                markerValue = str(marker)
            self.update(markerValue)
        event.Skip()

    def shiftViewLeft(self, event):
        if self.Data.Datasets != []:
            if self.shiftView != 0:
                viewShift = self.shiftView - self.tiles
                if viewShift < 0:
                    viewShift = 0

                markerList = self.ComboMarkers.GetItems()
                if self.markerValue == []:
                    marker = []
                else:
                    markerID = markerList.index(str(self.markerValue)) - 1
                    if markerID < 1:
                        marker = []
                    else:
                        marker = markerList[markerID]

                self.update(marker, viewShift)
        event.Skip()

    def shiftViewRight(self, event):
        if self.Data.Datasets != []:
            if self.shiftView + self.tiles \
                    < len(self.allMarker):
                viewShift = self.shiftView + self.tiles

                markerList = self.ComboMarkers.GetItems()
                if self.markerValue == []:
                    marker = []
                else:
                    markerID = markerList.index(str(self.markerValue)) + 1
                    if markerID >= len(markerList):
                        markerID = len(markerList) - 1
                    marker = markerList[markerID]

                self.update(marker, viewShift)
        event.Skip()

    def updateOverlay(self, event):
        if hasattr(self, 'markerValue'):
            self.update(self.markerValue)
        event.Skip()


class EpochsDetail(wx.Panel):

    def __init__(self, ParentFrame, Data):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        newFigure(self, showDetailEpochs=True)

        # Figure events
        self.canvas.callbacks.connect('pick_event', self.onPick)

        # To record button presses
        self.canvas.Bind(wx.EVT_CHAR, self.keyDown)

    def keyDown(self, event):
        """Interact with the figure canvas if keyboard is used"""

        if self.Data.Datasets != []:

            key = event.KeyCode

            if key == 49:
                self.keySelect(1)
            elif key == 50:
                self.keySelect(2)
            elif key == 51:
                self.keySelect(3)
            elif key == 52:
                self.keySelect(4)
            elif key == 53:
                self.keySelect(5)
            elif key == 54:
                self.keySelect(6)

            # Shift view
            elif key == 113:
                # Key: 'Q'
                self.shiftViewLeft(event)
            elif key == 101:
                # Key: 'E'
                self.shiftViewRight(event)

        event.Skip()

    def keySelect(self, figID):

        subPlots = self.canvas.figure.get_axes()

        if figID <= len(subPlots):

            selectedID = subPlots[figID - 1].get_title()

            children = subPlots[figID - 1].get_children()
            textChildren = np.array(
                [[i, i.get_text()]
                 for i in children
                 if 'matplotlib.text.Text' in str(type(i))])
            titleObject = textChildren[
                np.where(textChildren[:, 1] == selectedID)[0]][0][0]

            selectedID = int(selectedID[selectedID.find('Epoch') + 6:]) - 1
            selectedType = self.Data.Results.matrixSelected[selectedID]

            # If Epoch is already selected as an outlier
            if selectedType in ['selected', 'threshold', 'blink',
                                'bridge']:
                color = 'black'
                titleObject.set_fontweight('normal')
                if self.ComboOutliers.GetSelection() <= 2:
                    self.shiftView -= 1

                if selectedType == 'selected':
                    self.Data.Results.matrixSelected[
                        selectedID] = 'ok_normal'
                elif selectedType == 'threshold':
                    self.Data.Results.matrixSelected[
                        selectedID] = 'ok_thresh'
                elif selectedType == 'blink':
                    self.Data.Results.matrixSelected[
                        selectedID] = 'ok_blink'
                elif selectedType == 'bridge':
                    self.Data.Results.matrixSelected[
                        selectedID] = 'ok_bridge'

            else:
                titleObject.set_fontweight('bold')
                if self.ComboOutliers.GetSelection() <= 2:
                    self.shiftView += 1

                if selectedType == 'ok_normal':
                    color = '#ff8c00'
                    self.Data.Results.matrixSelected[
                        selectedID] = 'selected'
                elif selectedType == 'ok_thresh':
                    color = 'r'
                    self.Data.Results.matrixSelected[
                        selectedID] = 'threshold'
                elif selectedType == 'ok_blink':
                    color = 'm'
                    self.Data.Results.matrixSelected[
                        selectedID] = 'blink'
                elif selectedType == 'ok_bridge':
                    color = 'b'
                    self.Data.Results.matrixSelected[
                        selectedID] = 'bridge'

            titleObject.set_color(color)
            for ax in titleObject.axes.spines:
                titleObject.axes.spines[ax].set_color(color)
            self.Data.Results.updateAnalysis = True

            self.canvas.draw()

    def update(self, markerValue=[], shiftView=0):
        self.figure.clear()
        self.shiftView = shiftView
        self.markerValue = markerValue

        markerList = [
            m for m in self.Data.Results.markers
            if m not in self.Data.markers2hide]
        markerList = ['All   '] + np.unique(
            markerList).astype('str').tolist()
        self.ComboMarkers.SetItems(markerList)

        if self.markerValue == []:
            self.id2Show = []
        else:
            self.id2Show = np.where(
                self.Data.Results.markers == self.markerValue)[0]

        if self.markerValue == []:
            self.ComboMarkers.SetSelection(0)
            self.id2Show = np.arange(self.Data.Results.markers.shape[0])

        # Only show unhidden markers
        self.id2Show = np.array(
            [i for i, m in enumerate(self.Data.Results.markers)
             if m not in self.Data.markers2hide and i in self.id2Show])

        if self.ComboOutliers.GetSelection() == 0:
            restrictedList = [
                i for i, m in enumerate(self.Data.Results.matrixSelected)
                if 'ok_' not in m]
            self.id2Show = [r for r in restrictedList if r in self.id2Show]

        elif self.ComboOutliers.GetSelection() == 1:
            restrictedList = [
                i for i, m in enumerate(self.Data.Results.matrixSelected)
                if 'ok_' in m]
            self.id2Show = [r for r in restrictedList if r in self.id2Show]

        self.labelsChannel = self.Data.Datasets[0].labelsChannel
        Results = self.Data.Results
        samplingPoints = Results.epochs.shape[2]
        preStimuli = 1000. / (float(Results.sampleRate) /
                              Results.preCut)
        postStimuli = 1000. / (float(Results.sampleRate) /
                               Results.postCut)
        xaxis = [int(float(i) * (preStimuli + postStimuli) /
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
                epoch = self.Data.Results.epochs[epochID]
                idSelected = self.Data.Results.matrixSelected[epochID]

                sizer = np.sqrt(
                    np.sum(np.ptp(epoch, axis=1) / epoch.shape[0])) * 2
                modulator = float(self.ComboAmplitude.GetValue()[:-1])
                sizer *= modulator / 100.

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
                        for ax in axes.spines:
                            axes.spines[ax].set_color(color)

                # Draw single channels
                minmax = [0, 0]
                for j, c in enumerate(epoch):
                    if self.ComboOverlay.GetValue() == 'Overlay':
                        delta = 0
                    else:
                        delta = j
                    if isBroken:
                        color = 'c'
                        axes.title.set_fontweight('bold')
                        axes.title.set_color(color)
                        for ax in axes.spines:
                            axes.spines[ax].set_color(color)
                    elif Results.matrixThreshold[epochID][j]:
                        color = 'r'
                        axes.text(postStimuli + 1, c[-1] / sizer - delta,
                                  self.labelsChannel[j], color=color)
                        axes.title.set_fontweight('bold')
                        axes.title.set_color(color)
                        for ax in axes.spines:
                            axes.spines[ax].set_color(color)
                    elif Results.matrixBridge[epochID][j]:
                        color = 'b'
                        axes.text(postStimuli + 1, c[-1] / sizer - delta,
                                  self.labelsChannel[j], color=color)
                        axes.title.set_fontweight('bold')
                        axes.title.set_color(color)
                        for ax in axes.spines:
                            axes.spines[ax].set_color(color)
                    else:
                        color = 'gray'

                    lines = axes.plot(xaxis, c / sizer - delta, color,
                                      picker=1)
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
                axes.title.set_picker(5)
                axes.vlines(0, minmax[0], minmax[1], linestyles='dotted')

                if idSelected == 'selected':
                    color = '#ff8c00'
                    axes.title.set_fontweight('bold')
                    axes.title.set_color(color)
                    for ax in axes.spines:
                        axes.spines[ax].set_color(color)
                elif 'ok_' in idSelected:
                    color = 'k'
                    axes.title.set_fontweight('normal')
                    axes.title.set_color(color)
                    for ax in axes.spines:
                        axes.spines[ax].set_color(color)

        currentPage = (self.shiftView / self.tiles) + 1
        totalPage = (len(self.id2Show) - 1) / self.tiles + 1
        if totalPage == 0:
            currentPage = 0

        self.TextPages.SetLabel('Page: %s/%s   ' % (currentPage, totalPage))

        self.figure.tight_layout()
        self.canvas.draw()

    def updateFigure(self, event):
        if self.Data.Datasets != []:
            markerSelection = self.ComboMarkers.GetSelection()
            if markerSelection == 0:
                self.markerValue = []
            else:
                self.markerValue = str(self.ComboMarkers.GetValue())
            self.update(self.markerValue)
        event.Skip()

    def shiftViewLeft(self, event):
        if self.Data.Datasets != []:
            if self.shiftView != 0:
                viewShift = self.shiftView - self.tiles
                if viewShift < 0:
                    viewShift = 0
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
        # Only do something if left double click
        if event.mouseevent.dblclick and event.mouseevent.button == 1:

            # Print Line name and color it black if requested
            if event.artist.get_picker() == 1:
                event.artist.set_color('black')
                linenumber = int(event.artist.get_label()[5:])
                xValue = 1000. * self.Data.Results.postCut / \
                    self.Data.Results.sampleRate + 1
                yValue = event.artist.get_data()[1][-1]
                event.artist.axes.text(xValue, yValue,
                                       self.labelsChannel[linenumber],
                                       color='black')

            # Select or Deselect an Epoch as an Outlier
            elif event.artist.get_picker() == 5:
                selectedID = event.artist.get_text()
                selectedID = int(selectedID[selectedID.find('Epoch') + 6:]) - 1
                selectedType = self.Data.Results.matrixSelected[selectedID]

                # If Epoch is already selected as an outlier
                if selectedType in ['selected', 'threshold', 'blink',
                                    'bridge']:
                    color = 'black'
                    event.artist.set_fontweight('normal')
                    if self.ComboOutliers.GetSelection() <= 2:
                        self.shiftView -= 1

                    if selectedType == 'selected':
                        self.Data.Results.matrixSelected[
                            selectedID] = 'ok_normal'
                    elif selectedType == 'threshold':
                        self.Data.Results.matrixSelected[
                            selectedID] = 'ok_thresh'
                    elif selectedType == 'blink':
                        self.Data.Results.matrixSelected[
                            selectedID] = 'ok_blink'
                    elif selectedType == 'bridge':
                        self.Data.Results.matrixSelected[
                            selectedID] = 'ok_bridge'

                else:
                    event.artist.set_fontweight('bold')
                    if self.ComboOutliers.GetSelection() <= 2:
                        self.shiftView += 1

                    if selectedType == 'ok_normal':
                        color = '#ff8c00'
                        self.Data.Results.matrixSelected[
                            selectedID] = 'selected'
                    elif selectedType == 'ok_thresh':
                        color = 'r'
                        self.Data.Results.matrixSelected[
                            selectedID] = 'threshold'
                    elif selectedType == 'ok_blink':
                        color = 'm'
                        self.Data.Results.matrixSelected[
                            selectedID] = 'blink'
                    elif selectedType == 'ok_bridge':
                        color = 'b'
                        self.Data.Results.matrixSelected[
                            selectedID] = 'bridge'

                event.artist.set_color(color)
                for ax in event.artist.axes.spines:
                    event.artist.axes.spines[ax].set_color(color)
                self.Data.Results.updateAnalysis = True

            self.canvas.draw()

        if event.mouseevent.name == 'button_press_event':
            self.canvas.ReleaseMouse()

    def updateLayout(self, event):
        if hasattr(self, 'markerValue'):
            self.update(self.markerValue)
        event.Skip()

    def updateSize(self, event):
        if hasattr(self, 'markerValue'):
            self.update(self.markerValue, self.shiftView)
        event.Skip()

    def updateOverlay(self, event):
        if hasattr(self, 'markerValue'):
            self.update(self.markerValue)
        event.Skip()


def newFigure(self, showGrid=False, showGFP=False, showGMD=False,
              showDetailEpochs=False, showSummaryEpochs=False):
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

    if showDetailEpochs:
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

        self.TextMarker = wx.StaticText(self, wx.ID_ANY, label='Marker:')
        self.hbox.Add(self.TextMarker, 0, border=3, flag=flags)

        self.ComboMarkers = wx.ComboBox(self, style=wx.CB_READONLY,
                                        choices=['All   '])
        self.ComboMarkers.SetSelection(0)
        wx.EVT_COMBOBOX(self.ComboMarkers, self.ComboMarkers.Id,
                        self.updateFigure)
        self.hbox.Add(self.ComboMarkers, 0, border=3, flag=flags)

        self.ComboOutliers = wx.ComboBox(
            self, style=wx.CB_READONLY,
            choices=['Outliers', 'Accepted', 'All'])
        self.ComboOutliers.SetSelection(0)
        wx.EVT_COMBOBOX(self.ComboOutliers, self.ComboOutliers.Id,
                        self.updateFigure)
        self.hbox.Add(self.ComboOutliers, 0, border=3, flag=flags)

        self.TextPages = wx.StaticText(self, wx.ID_ANY, label='Page: 0/0 ')
        self.hbox.Add(self.TextPages, 0, border=3, flag=flags)

        self.goLeftButton = wx.Button(self, wx.ID_ANY, "<<", size=(35, 30))
        self.goRightButton = wx.Button(self, wx.ID_ANY, ">>", size=(35, 30))
        wx.EVT_BUTTON(self.goLeftButton, self.goLeftButton.Id,
                      self.shiftViewLeft)
        wx.EVT_BUTTON(self.goRightButton, self.goRightButton.Id,
                      self.shiftViewRight)
        self.hbox.Add(self.goLeftButton, 0, border=3, flag=flags)
        self.hbox.Add(self.goRightButton, 0, border=3, flag=flags)

    if showSummaryEpochs:
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

        self.TextMarker = wx.StaticText(self, wx.ID_ANY, label='Marker:')
        self.hbox.Add(self.TextMarker, 0, border=3, flag=flags)

        self.ComboMarkers = wx.ComboBox(self, style=wx.CB_READONLY,
                                        choices=['All   '])
        self.ComboMarkers.SetSelection(0)
        wx.EVT_COMBOBOX(self.ComboMarkers, self.ComboMarkers.Id,
                        self.updateFigure)
        self.hbox.Add(self.ComboMarkers, 0, border=3, flag=flags)

        self.TextPages = wx.StaticText(self, wx.ID_ANY, label='Page: 0/0 ')
        self.hbox.Add(self.TextPages, 0, border=3, flag=flags)

        self.goLeftButton = wx.Button(self, wx.ID_ANY, "<<", size=(35, 30))
        self.goRightButton = wx.Button(self, wx.ID_ANY, ">>", size=(35, 30))
        wx.EVT_BUTTON(self.goLeftButton, self.goLeftButton.Id,
                      self.shiftViewLeft)
        wx.EVT_BUTTON(self.goRightButton, self.goRightButton.Id,
                      self.shiftViewRight)
        self.hbox.Add(self.goLeftButton, 0, border=3, flag=flags)
        self.hbox.Add(self.goRightButton, 0, border=3, flag=flags)

    if showDetailEpochs or showSummaryEpochs:
        self.ComboOverlay = wx.ComboBox(
            self, style=wx.CB_READONLY,
            choices=['Spread', 'Overlay'])
        self.ComboOverlay.SetSelection(0)
        wx.EVT_COMBOBOX(self.ComboOverlay, self.ComboOverlay.Id,
                        self.updateOverlay)
        self.hbox.Add(self.ComboOverlay, 0, border=3, flag=flags)

    self.sizer.Add(self.hbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)

    self.sizer.Add(self.toolbar, 0, wx.EXPAND)
    self.SetSizer(self.sizer)
    self.Fit()


def findSquare(number):
    if number == 0:
        return 1, 1
    else:
        s1 = int(np.round(np.sqrt(number)))
        s2 = int(np.ceil(float(number) / s1))
        return s1, s2


def getXaxis(Results):
    stepSize = (Results.preEpoch + Results.postEpoch) / \
        (Results.preFrame + Results.postFrame)
    xaxis = [int(i * stepSize - Results.preEpoch)
             for i in range(Results.preFrame + Results.postFrame)]
    return xaxis
