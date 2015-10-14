import numpy as np
from scipy.signal import butter, filtfilt
from scipy.interpolate import NearestNDInterpolator


class Results():

    def __init__(self, MainFrame):

        # Specify relevant variables
        self.MainFrame = MainFrame

    def updateAll(self):

        # Get Specifications
        PanelSpecs = self.MainFrame.PanelSpecs
        self.newReference = PanelSpecs.DropDownNewRef.GetValue()
        self.average = PanelSpecs.CheckboxAverage.GetValue()
        self.removeDC = PanelSpecs.CheckboxDC.GetValue()

        try:
            self.highcut = float(PanelSpecs.HighPass.GetValue())
        except ValueError:
            self.highcut = 0.1
            PanelSpecs.HighPass.SetValue(str(self.highcut))
        try:
            self.lowcut = float(PanelSpecs.LowPass.GetValue())
        except ValueError:
            self.lowcut = 80.0
            PanelSpecs.LowPass.SetValue(str(self.lowcut))
        try:
            self.preEpoch = float(PanelSpecs.PreEpoch.GetValue())
        except ValueError:
            self.preEpoch = 100.0
            PanelSpecs.PreEpoch.SetValue(str(self.preEpoch))
        try:
            self.postEpoch = float(PanelSpecs.PostEpoch.GetValue())
        except ValueError:
            self.postEpoch = 500.0
            PanelSpecs.PostEpoch.SetValue(str(self.postEpoch))
        try:
            self.notchValue = float(PanelSpecs.Notch.GetValue())
        except ValueError:
            self.notchValue = 50.0
            PanelSpecs.Notch.SetValue(str(self.notch))

        self.doNotch = PanelSpecs.CheckboxNotch.GetValue()
        self.sampleRate = self.MainFrame.Datasets[0].sampleRate
        self.preFrame = int(np.round(self.preEpoch * self.sampleRate * 0.001))
        self.postFrame = int(
            np.round(self.postEpoch * self.sampleRate * 0.001))
        self.channels2Interpolate = PanelSpecs.channels2Interpolate

        # Filter Channel Signal
        for i, d in enumerate(self.MainFrame.Datasets):
            dataset = np.copy(d.rawdata)

            # Average or specific reference
            if self.average:
                dataset -= dataset.mean(axis=0)
            elif self.newReference != '':
                electrodeID = np.where(d.labelsChannel == self.newReference)[0]
                dataset -= dataset[electrodeID]

            # Remove DC
            if self.removeDC:
                dataset = butter_bandpass_filter(dataset,
                                                 d.sampleRate,
                                                 DC=True)

            # Notch Filter
            if self.doNotch:
                dataset = butter_bandpass_filter(dataset,
                                                 d.sampleRate,
                                                 notch=self.notchValue)

            # Run Butterworth Low-, High- or Bandpassfilter
            if self.lowcut != 0 and self.highcut != 0:
                dataset = butter_bandpass_filter(dataset,
                                                 d.sampleRate,
                                                 highcut=self.highcut,
                                                 lowcut=self.lowcut)

            # Create epochs
            epochs = np.array([dataset[:, m - self.preFrame:m + self.postFrame]
                               for m in d.markerTime])

            # accumulate datasets
            if i == 0:
                self.epochs = epochs
                self.markers = d.markerValue
                self.labelsChannel = d.labelsChannel
            else:
                self.epochs = np.vstack((self.epochs, epochs))
                self.markers = np.hstack((self.markers, d.markerValue))

            del dataset

        # Interpolate channels in epochs
        if self.channels2Interpolate != []:
            interpolateChannels(self, '../biosemi_128.xyz')

        # Update epochs
        self.updateEpochs()

    def updateEpochs(self):

        PanelSpecs = self.MainFrame.PanelSpecs

        # Get Specifications
        self.baselineCorr = PanelSpecs.CheckboxBaseline.GetValue()
        try:
            self.threshold = float(PanelSpecs.ThreshValue.GetValue())
        except ValueError:
            self.threshold = 80.0
            PanelSpecs.ThreshValue.SetValue(str(self.threshold))
        try:
            self.window = float(PanelSpecs.ThreshWindow.GetValue())
        except ValueError:
            self.window = 100.0
            PanelSpecs.ThreshWindow.SetValue(str(self.window))
        self.thresholdEpochs = PanelSpecs.CheckboxThreshold.GetValue()
        self.excludeChannel = PanelSpecs.channels2exclude

        # Copy epoch and marker values
        epochs = np.copy(self.epochs)
        markers = np.copy(self.markers)

        # Baseline Correction
        if self.baselineCorr:
            for e in epochs:
                baselineAvg = [[c] for c in
                               np.mean(e[:, :self.preFrame], axis=1)]
                e -= baselineAvg

        # Threshold epochs
        if self.thresholdEpochs:

            # Exclude Channels
            if self.excludeChannel != []:
                channelID = [
                    i for i, e in enumerate(self.labelsChannel)
                    if e not in self.excludeChannel]
            else:
                channelID = range(self.labelsChannel.shape[0])

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

            # Drop bad Epochs
            epochs = epochs[self.okID]
            markers = markers[self.okID]

        # Create average epochs
        self.uniqueMarkers = np.unique(markers)
        avgEpochs = [epochs[np.where(markers == u)].mean(axis=0)
                     for u in self.uniqueMarkers]
        self.avgGFP = [calculateGFP(a) for a in avgEpochs]

        self.MainFrame.GFPDetailed.update(self)
        self.MainFrame.GFPSummary.update(self)


def butter_bandpass_filter(data, fs, highcut=0, lowcut=0,
                           order=2, notch=-1.0, DC=False):

    # Why these formulas work is complicated
    N = np.log2(fs)
    divisorHigh = float(2**(N - 1) + 2**(N - 3))
    divisorLow = float(2**(N - 2) + 2**(N - 3) + 2**(N - 5))

    if DC:
        b, a = butter(order, 1. / divisorHigh, btype='high')
    elif notch > 0:
        b, a = butter(order, [(notch / divisorHigh) - 1. / divisorHigh,
                              (notch / divisorLow) + 1. / divisorLow],
                      btype='bandstop')
    else:
        if lowcut == 0:
            b, a = butter(order, highcut / divisorHigh, btype='high')
        elif highcut == 0:
            b, a = butter(order, lowcut / divisorLow, btype='low')
        else:
            b, a = butter(order, [highcut / divisorHigh, lowcut / divisorLow],
                          btype='band')
    return filtfilt(b, a, data)


def calculateGFP(dataset):
    # Global Field Potential
    return dataset.std(axis=0)


def interpolateChannels(self, xyz):

    with open(xyz) as f:
        content = f.readlines()
        xyz = []
        labels = []
        for i, e in enumerate(content):
            if i != 0:
                coord = e.split()
                xyz.append([float(coord[0]),
                            float(coord[1]),
                            float(coord[2])])
                labels.append(coord[3])
        xyz = np.array(xyz)
        labels = np.array(labels)

    id2interp = sorted([np.where(labels == c)[0][0]
                        for c in self.channels2Interpolate],
                       reverse=True)

    for epoch in self.epochs:

        newSignal = []
        for i in range(epoch.shape[1]):
            values = np.delete(epoch[:, i], id2interp)
            points = np.delete(xyz, id2interp, axis=0)
            coord = xyz[id2interp]
            interpolate = NearestNDInterpolator(points, values)
            newSignal.append(interpolate(coord))

        for i, channelID in enumerate(id2interp):
            epoch[channelID] = np.array(newSignal)[:, i]
