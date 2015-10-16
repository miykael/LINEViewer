import numpy as np
from scipy.signal import butter, filtfilt
from scipy.interpolate import NearestNDInterpolator


class Results():

    def __init__(self):
        """EMPTY INITIATION"""

    def updateAll(self, Data):

        # Get Specifications
        self.newReference = Data.Specs.DropDownNewRef.GetValue()
        self.average = Data.Specs.CheckboxAverage.GetValue()
        self.removeDC = Data.Specs.CheckboxDC.GetValue()

        try:
            self.highcut = float(Data.Specs.HighPass.GetValue())
        except ValueError:
            self.highcut = 0.1
            Data.Specs.HighPass.SetValue(str(self.highcut))
        try:
            self.lowcut = float(Data.Specs.LowPass.GetValue())
        except ValueError:
            self.lowcut = 80.0
            Data.Specs.LowPass.SetValue(str(self.lowcut))
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
        try:
            self.notchValue = float(Data.Specs.Notch.GetValue())
        except ValueError:
            self.notchValue = 50.0
            Data.Specs.Notch.SetValue(str(self.notch))

        self.doPass = Data.Specs.CheckboxPass.GetValue()
        self.doNotch = Data.Specs.CheckboxNotch.GetValue()
        self.sampleRate = Data.Datasets[0].sampleRate
        self.preFrame = int(np.round(self.preEpoch * self.sampleRate * 0.001))
        self.postFrame = int(
            np.round(self.postEpoch * self.sampleRate * 0.001))

        # Data object to save original epoch information
        Data.Orig = type('Orig', (object,), {})()

        # Filter Channel Signal
        for i, d in enumerate(Data.Datasets):
            dataset = np.copy(d.rawdata)

            # Average or specific reference
            if self.average:
                dataset -= dataset.mean(axis=0)
            elif self.newReference != '':
                electrodeID = np.where(d.labelsChannel == self.newReference)[0]
                dataset -= dataset[electrodeID]

            # Remove DC
            if self.removeDC:
                # TODO: Check which approach is correct
                # dataset = butter_bandpass_filter(dataset,
                #                                  d.sampleRate,
                #                                  DC=True)
                dataset = np.array([channel - channel.mean()
                                    for channel in dataset])

            # Notch Filter
            if self.doNotch:
                dataset = butter_bandpass_filter(dataset,
                                                 d.sampleRate,
                                                 notch=self.notchValue)

            # Run Butterworth Low-, High- or Bandpassfilter
            if self.doPass:
                if self.lowcut != 0 and self.highcut != 0:
                    dataset = butter_bandpass_filter(dataset,
                                                     d.sampleRate,
                                                     highcut=self.highcut,
                                                     lowcut=self.lowcut)

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
        self.thresholdEpochs = Data.Specs.CheckboxThreshold.GetValue()
        self.excludeChannel = Data.Specs.channels2exclude

        # Copy epoch and marker values
        epochs = np.copy(Data.Orig.epochs)
        markers = np.copy(Data.Orig.markers)

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


def interpolateChannels(self, Data, xyz):

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
                        for c in Data.Specs.channels2Interpolate],
                       reverse=True)

    for epoch in Data.Orig.epochs:

        newSignal = []
        for i in range(epoch.shape[1]):
            values = np.delete(epoch[:, i], id2interp)
            points = np.delete(xyz, id2interp, axis=0)
            coord = xyz[id2interp]
            interpolate = NearestNDInterpolator(points, values)
            newSignal.append(interpolate(coord))

        for i, channelID in enumerate(id2interp):
            epoch[channelID] = np.array(newSignal)[:, i]
