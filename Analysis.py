import wx
import numpy as np
from FileHandler import ReadXYZ
from scipy.signal import butter, filtfilt
from scipy.interpolate import NearestNDInterpolator


class Results():

    def __init__(self):
        """EMPTY INITIATION"""

    def updateAll(self, Data):

        # Get Specifications
        self.removeDC = Data.Specs.CheckboxDC.GetValue()
        self.average = Data.Specs.CheckboxAverage.GetValue()
        self.newReference = Data.Specs.DropDownNewRef.GetValue()
        self.doPass = Data.Specs.CheckboxPass.GetValue()
        try:
            self.lowcut = float(Data.Specs.LowPass.GetValue())
        except ValueError:
            self.lowcut = 80.0
            Data.Specs.LowPass.SetValue(str(self.lowcut))
        try:
            self.highcut = float(Data.Specs.HighPass.GetValue())
        except ValueError:
            self.highcut = 0.1
            Data.Specs.HighPass.SetValue(str(self.highcut))
        self.doNotch = Data.Specs.CheckboxNotch.GetValue()
        try:
            self.notchValue = float(Data.Specs.Notch.GetValue())
        except ValueError:
            self.notchValue = 50.0
            Data.Specs.Notch.SetValue(str(self.notch))
        try:
            self.preEpoch = float(Data.Specs.PreEpoch.GetValue())
        except ValueError:
            self.preEpoch = 100.0
            Data.Specs.PreEpoch.SetValue(str(self.preEpoch))
        try:
            self.postEpoch = float(Data.Specs.PostEpoch.GetValue())
        except ValueError:
            self.postEpoch = 500.0
            Data.Specs.PostEpoch.SetValue(str(self.postEpoch))
        self.sampleRate = Data.Datasets[0].sampleRate
        self.preFrame = int(np.round(self.preEpoch * self.sampleRate * 0.001))
        self.postFrame = int(
            np.round(self.postEpoch * self.sampleRate * 0.001))

        # Data object to save original epoch information
        Data.Orig = type('Orig', (object,), {})()

        # Filter Channel Signal
        for i, d in enumerate(Data.Datasets):
            dataset = np.copy(d.rawdata)

            # Remove DC
            if self.removeDC:
                dataset = np.array([channel - channel.mean()
                                    for channel in dataset])

            # Average or specific reference
            if self.average:
                dataset -= dataset.mean(axis=0)
            elif self.newReference != '':
                electrodeID = np.where(d.labelsChannel == self.newReference)[0]
                dataset -= dataset[electrodeID]

            # Run Butterworth Low-, High- or Bandpassfilter
            if self.doPass:
                if self.lowcut != 0 and self.highcut != 0:
                    dataset = butter_bandpass_filter(dataset,
                                                     d.sampleRate,
                                                     highcut=self.highcut,
                                                     lowcut=self.lowcut)

            # Notch Filter
            if self.doNotch:
                dataset = butter_bandpass_filter(dataset,
                                                 d.sampleRate,
                                                 notch=self.notchValue)

            # Create epochs
            epochs = np.array([dataset[:, m - self.preFrame:m + self.postFrame]
                               for m in d.markerTime])

            # Accumulate epoch information
            if i == 0:
                Data.Orig.epochs = epochs
                Data.Orig.markers = d.markerValue
                Data.Orig.labelsChannel = d.labelsChannel
            else:
                Data.Orig.epochs = np.vstack((Data.Orig.epochs, epochs))
                Data.Orig.markers = np.hstack((Data.Orig.markers,
                                               d.markerValue))

            del dataset

        self.interpolationCheck(Data)

    def interpolationCheck(self, Data):

        if Data.Specs.channels2Interpolate != []:
            interpolateChannels(self, Data, Data.Specs.xyzFile)

        self.updateEpochs(Data)

    def updateEpochs(self, Data):

        # Get Specifications
        self.baselineCorr = Data.Specs.CheckboxBaseline.GetValue()
        self.bridgeCorr = Data.Specs.CheckboxBridge.GetValue()
        self.alphaCorr = Data.Specs.CheckboxAlpha.GetValue()
        self.thresholdCorr = Data.Specs.CheckboxThreshold.GetValue()
        try:
            self.threshold = float(Data.Specs.ThreshValue.GetValue())
        except ValueError:
            self.threshold = 80.0
            Data.Specs.ThreshValue.SetValue(str(self.threshold))
        try:
            self.window = float(Data.Specs.ThreshWindow.GetValue())
        except ValueError:
            self.window = 100.0
            Data.Specs.ThreshWindow.SetValue(str(self.window))
        self.excludeChannel = Data.Specs.channels2exclude

        # Copy epoch and marker values
        epochs = np.copy(Data.Orig.epochs)
        if not hasattr(self, 'collapsedMarkers'):
            markers = np.copy(Data.Orig.markers)
        else:
            markers = self.collapsedMarkers

        # Hide Markers
        if Data.markers2hide != []:
            for h in Data.markers2hide:
                epochs = np.delete(epochs, np.where(markers == h), axis=0)
                markers = np.delete(markers, np.where(markers == h))

        # Baseline Correction
        if self.baselineCorr:
            for e in epochs:
                baselineAvg = [[c] for c in
                               np.mean(e[:, :self.preFrame], axis=1)]
                e -= baselineAvg

        # Threshold epochs
        if self.thresholdCorr:

            # Exclude Channels
            if self.excludeChannel != []:
                channelID = [
                    i for i, e in enumerate(Data.Orig.labelsChannel)
                    if e not in self.excludeChannel]
            else:
                channelID = range(Data.Orig.labelsChannel.shape[0])

            # Check threshold in selected channels
            windowSteps = int(self.window * self.sampleRate / 1000.)
            self.badID = []
            for i, e in enumerate(epochs):
                for j in range(e[channelID].shape[1] - windowSteps):
                    if np.sum(np.ptp(e[:, j:j + windowSteps],
                                     axis=1) > self.threshold) != 0:
                        self.badID.append(i)
                        break

            # Check threshold in selected channels
            self.okID = [
                i for i in range(epochs.shape[0]) if i not in self.badID]
        else:
            self.okID = [i for i in range(epochs.shape[0])]

        # Drop bad Epochs
        self.epochs = epochs[self.okID]
        self.markers = markers[self.okID]

        # Create average epochs
        self.uniqueMarkers = np.unique(self.markers)
        self.avgEpochs = [self.epochs[np.where(self.markers == u)].mean(axis=0)
                          for u in self.uniqueMarkers]
        self.avgGFP = [calculateGFP(a) for a in self.avgEpochs]
        Data.GFPDetailed.update(self)
        Data.GFPSummary.update(self)


def butter_bandpass_filter(data, fs, highcut=0, lowcut=0,
                           order=2, notch=-1.0):

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    notch = notch / nyq

    if notch > 0:
        b, a = butter(order, [notch - 1. / nyq, notch + 1. / nyq],
                      btype='bandstop')
    else:
        if lowcut == 0:
            b, a = butter(order, high, btype='high')
        elif highcut == 0:
            b, a = butter(order, low, btype='low')
        else:
            b, a = butter(order, [high, low], btype='band')
    return filtfilt(b, a, data)


def calculateGFP(dataset):
    # Global Field Potential
    return dataset.std(axis=0)


def interpolateChannels(self, Data, xyz):

    xyz = ReadXYZ(xyz)

    id2interp = sorted([np.where(xyz.labels == c)[0][0]
                        for c in Data.Specs.channels2Interpolate],
                       reverse=True)

    # Create Progressbar for interpolation
    progressMax = Data.Orig.epochs.shape[0]
    dlg = wx.ProgressDialog(
        "Interpolation Progress", "Time remaining", progressMax,
        style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_SMOOTH)

    for count, epoch in enumerate(Data.Orig.epochs):

        newSignal = []
        for i in range(epoch.shape[1]):
            values = np.delete(epoch[:, i], id2interp)
            points = np.delete(xyz.coord, id2interp, axis=0)
            coord = xyz.coord[id2interp]
            interpolate = NearestNDInterpolator(points, values)
            newSignal.append(interpolate(coord))

        for i, channelID in enumerate(id2interp):
            epoch[channelID] = np.array(newSignal)[:, i]

        dlg.Update(count)

    dlg.Destroy()
