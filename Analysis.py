import wx
import numpy as np
from FileHandler import ReadXYZ
from scipy.signal import butter, filtfilt


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

        if Data.Specs.channels2interpolate != []:
            Data = interpolateChannels(self, Data, Data.Specs.xyzFile)

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

        # Exclude Channels
        if self.excludeChannel != []:
            channelID = [
                i for i, e in enumerate(Data.Orig.labelsChannel)
                if e not in self.excludeChannel]
        else:
            channelID = range(Data.Orig.labelsChannel.shape[0])

        # Correct epochs for threshold, bridges or alpha waves
        self.badEpochThreshold = []
        self.badEpochBridge = []
        self.badEpochAlpha = []

        if self.thresholdCorr or self.bridgeCorr or self.alphaCorr:

            # Go through all the epochs
            for i, e in enumerate(epochs):

                badThresholds = np.zeros(epochs[0].shape[0], dtype=int)
                badBridges = np.zeros(epochs[0].shape[0], dtype=int)
                badAlpha = np.zeros(epochs[0].shape[0], dtype=int)

                # correct for threshold
                if self.thresholdCorr:
                    windowSteps = int(self.window * self.sampleRate / 1000.)
                    for j in range(e[channelID].shape[1] - windowSteps):
                        channelThresholdOff = np.ptp(
                            e[:, j:j + windowSteps], axis=1) > self.threshold
                        if np.sum(channelThresholdOff) != 0:
                            badThresholds += channelThresholdOff

                # correct for bridges
                if self.bridgeCorr:
                    corrMatrix = np.where(np.corrcoef(e) > .99999)
                    if e.shape[0] != corrMatrix[0].shape[0]:
                        corrID = np.unique(
                            [corrMatrix[0][m]
                             for m in range(corrMatrix[0].shape[0])
                             if corrMatrix[0][m] != corrMatrix[1][m]])
                        badBridges[corrID] += 1

                # correct for alpha
                if self.alphaCorr:
                    ps = np.abs(np.fft.rfft(e))**2  # **2 for power specturm
                    freq = np.linspace(0, Data.Results.sampleRate / 2,
                                       ps.shape[1])
                    alphaFreq = [
                        a for a in [b for b, f in enumerate(freq) if f > 7.5]
                        if freq[a] < 12.5]
                    alphaPower = ps[:, alphaFreq].sum(axis=1)
                    alphaID = np.where(
                        alphaPower > alphaPower.mean() +
                        alphaPower.std() * 10)[0]
                    if alphaID.shape[0] != 0:
                        badAlpha[alphaID] += 1

                # Add information of bad channels
                self.badEpochThreshold.append(badThresholds != 0)
                self.badEpochBridge.append(badBridges.astype('bool'))
                self.badEpochAlpha.append(badAlpha.astype('bool'))

            # Turn channel information into numpy arrays
            self.badEpochThreshold = np.array(self.badEpochThreshold)
            self.badEpochBridge = np.array(self.badEpochBridge)
            self.badEpochAlpha = np.array(self.badEpochAlpha)

            # Create list of epochs that should be kept
            self.okID = []
            self.badID = []
            for i in range(epochs.shape[0]):
                if not np.any(self.badEpochThreshold[i] == 1) and \
                        not np.any(self.badEpochBridge[i] == 1) and \
                        not np.any(self.badEpochAlpha[i] == 1):
                    self.okID.append(i)
                else:
                    self.badID.append(i)
        else:
            self.okID = [i for i in range(epochs.shape[0])]
            self.badID = []

        # Drop bad Epochs
        self.epochs = epochs[self.okID]
        self.markers = markers[self.okID]

        # Create average epochs
        self.uniqueMarkers = np.unique(self.markers)
        self.avgEpochs = [self.epochs[np.where(self.markers == u)].mean(axis=0)
                          for u in self.uniqueMarkers]
        self.avgGFP = [calculateGFP(a) for a in self.avgEpochs]
        self.avgGMD = [calculateGMD(a) for a in self.avgEpochs]

        Data.Overview.update(self)
        Data.GFPSummary.update(self)
        Data.GFPDetailed.update(self)
        Data.EpochDetail.update([])


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


def calculateGMD(dataset):
    # Global Map Dissimilarity
    GFP = calculateGFP(dataset)
    unitaryStrength = dataset / GFP
    GMD = np.diff(unitaryStrength).std(axis=0)
    return np.insert(GMD, 0, 0)


def interpolateChannels(self, Data, xyz):

    xyz = ReadXYZ(xyz)
    channels2interpolate = Data.Specs.channels2interpolate

    id2interp = [i for i, e in enumerate(xyz.labels)
                 if e in channels2interpolate]
    id2keep = [i for i, e in enumerate(xyz.labels)
               if e not in channels2interpolate]

    matriceE = np.array([np.insert(e, 0, 1)
                         for e in xyz.coord[id2keep]])
    matriceK = np.zeros((len(id2keep), len(id2keep)))
    for i, r1 in enumerate(xyz.coord[id2keep]):
        for j, r2 in enumerate(xyz.coord[id2keep]):
            if i == j:
                matriceK[i, j] = 0
            else:
                Diff = (np.square(r1 - r2)).sum()
                matriceK[i, j] = Diff * np.log(Diff)
    matrice = np.concatenate((matriceK, matriceE), axis=1)
    addZeros = np.concatenate((matriceE.T, np.zeros((4, 4))), axis=1)
    matrice = np.concatenate((matrice, addZeros), axis=0)
    matriceInv = np.linalg.inv(matrice)

    # Create Progressbar for interpolation
    progressMax = Data.Orig.epochs.shape[0]
    dlg = wx.ProgressDialog(
        "Interpolation Progress", "Time remaining", progressMax,
        style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_SMOOTH)

    for count, epoch in enumerate(Data.Orig.epochs):

        signal = np.copy(epoch.T)

        Coef = []
        potential = np.concatenate((signal[:, id2keep],
                                    np.zeros((signal.shape[0], 4))),
                                   axis=1)
        for v in potential:
            Coef.append(np.dot(matriceInv, v))
        Coef = np.array(Coef)

        for b in id2interp:
            xyzInter = xyz.coord[b]
            Q = np.insert(xyzInter, 0, 1)
            CorrectCoord = xyz.coord[id2keep]
            Diff = np.array([np.square(xyzInter - c).sum()
                             for c in CorrectCoord])
            K = Diff * np.log(Diff)
            K[np.isnan(K)] = 0
            IntData = np.dot(Coef, np.concatenate((K, Q), axis=0))
            signal[:, b] = IntData
        Data.Orig.epochs[count] = signal.T

        dlg.Update(count)

    dlg.Destroy()

    return Data
