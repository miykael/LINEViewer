import wx
import numpy as np
from os import remove
from os.path import splitext, exists
from FileHandler import ReadXYZ
from scipy.signal import butter, filtfilt


class Results():

    def __init__(self):
        """EMPTY INITIATION"""

    def updateAll(self, Data):

        # Get Specifications
        self.sampleRate = Data.Datasets[0].sampleRate
        self.removeDC = Data.Specs.CheckboxDC.GetValue()
        self.average = Data.Specs.CheckboxAverage.GetValue()
        self.newReference = Data.Specs.DropDownNewRef.GetValue()
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
        self.doPass = Data.Specs.CheckboxPass.GetValue()
        try:
            self.lowcut = float(Data.Specs.LowPass.GetValue())

            # Checks that Lowpass value is below nyquist frequency
            nyquistFreq = self.sampleRate * 0.5
            if self.lowcut > nyquistFreq:
                self.lowcut = nyquistFreq - 0.001
                Data.Specs.LowPass.SetValue(str(self.lowcut))
                dlg = wx.MessageDialog(
                    Data.Overview, "Low pass value was above the nyquist " +
                    "frequency (%s Hz). The value was set to %s Hz." % (
                        nyquistFreq, self.lowcut),
                    "Info", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
        except ValueError:
            self.lowcut = 0
            Data.Specs.LowPass.SetValue(str(self.lowcut))
        try:
            self.highcut = float(Data.Specs.HighPass.GetValue())

            # Checks that Highpass value is above sampling frequency
            minFreq = 1. / int(np.round(
                (self.preEpoch + self.postEpoch) * self.sampleRate * 0.001))
            if self.highcut <= minFreq:
                self.highcut = minFreq
                Data.Specs.HighPass.SetValue(str(self.highcut))
                dlg = wx.MessageDialog(
                    Data.Overview, "High pass value was below minimum " +
                    "Frequency and was adjusted to %.4f Hz." % minFreq,
                    "Info", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
        except ValueError:
            self.highcut = 0
            Data.Specs.HighPass.SetValue(str(self.highcut))
        self.doNotch = Data.Specs.CheckboxNotch.GetValue()
        try:
            self.notchValue = float(Data.Specs.Notch.GetValue())
        except ValueError:
            self.notchValue = 50.0
            Data.Specs.Notch.SetValue(str(self.notch))

        # Calculate number of total iteration steps
        iterations = 1
        iterations += self.removeDC
        iterations += self.average or self.newReference != 'None'
        iterations += self.doPass and self.lowcut != 0 and self.highcut != 0
        iterations += self.doNotch

        # Preprocessing Message
        progText = '\n' * ((1 + iterations) * len(Data.Datasets) - 1)
        nChannels = Data.Datasets[0].rawdata.shape[0]
        progressMax = iterations * len(Data.Datasets) * nChannels
        dlg = wx.ProgressDialog(
            "Data Preprocessing", progText, progressMax,
            style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_SMOOTH)
        counter = 0
        progText = ''

        # Filter Channel Signal
        for i, d in enumerate(Data.Datasets):

            progFileName = Data.Filenames[i]
            progText += 'Preprocessing %s:' % progFileName

            # Load Dataset in memmap file
            tmpFilename = splitext(d.filename)[0] + '.lineviewerTempData'
            tmpDataset = np.memmap(tmpFilename, mode='w+', dtype='float32',
                                   shape=d.rawdata.shape)
            for t in range(nChannels):
                tmpDataset[t] = d.rawdata[t]

                # Update Progress Dialog
                progUpdate = '\nRead Data:\t{:>6}%'.format(
                    np.round(100. * (t + 1) / nChannels, 1))
                dlg.Update(counter, progText + progUpdate)
                counter += 1
            progText += '\nRead Data:\t{:>6}%'.format(100.0)

            # 1. Remove DC
            if self.removeDC:
                dcOffset = np.vstack(tmpDataset.mean(axis=1))
                for t in range(nChannels):
                    tmpDataset[t] -= dcOffset[t]

                    # Update Progress Dialog
                    progUpdate = '\nRemove DC:\t{:>6}%'.format(
                        np.round(100. * (t + 1) / nChannels, 1))
                    dlg.Update(counter, progText + progUpdate)
                    counter += 1
                progText += '\nRemove DC:\t{:>6}%'.format(100.0)

            # 2. Average or specific reference
            if self.average or self.newReference != 'None':

                if self.average:
                    refOffset = tmpDataset.mean(axis=0)
                elif self.newReference != 'None':
                    electrodeID = np.where(
                        d.labelsChannel == self.newReference)[0]
                    if self.newReference != 'Average':
                        refOffset = tmpDataset[electrodeID]
                for t in range(nChannels):
                    tmpDataset[t] -= refOffset[t]

                    # Update Progress Dialog
                    progUpdate = '\nRereference:\t{:>6}%'.format(
                        np.round(100. * (t + 1) / nChannels, 1))
                    dlg.Update(counter, progText + progUpdate)
                    counter += 1
                progText += '\nRereference:\t{:>6}%'.format(100.0)

            # 3. Run Butterworth Low-, High- or Bandpassfilter
            if self.doPass and self.lowcut != 0 and self.highcut != 0:
                b, a = butter_bandpass_param(d.sampleRate,
                                             highcut=self.highcut,
                                             lowcut=self.lowcut)
                for t in range(nChannels):
                    tmpDataset[t] = filtfilt(b, a, tmpDataset[t])

                    # Update Progress Dialog
                    progUpdate = '\nFilter Data:\t{:>6}%'.format(
                        np.round(100. * (t + 1) / nChannels, 1))
                    dlg.Update(counter, progText + progUpdate)
                    counter += 1
                progText += '\nFilter Data:\t{:>6}%'.format(100.0)

            # 4. Notch Filter
            if self.doNotch:
                b, a = butter_bandpass_param(d.sampleRate,
                                             notch=self.notchValue)
                for t in range(nChannels):
                    tmpDataset[t] = filtfilt(b, a, tmpDataset[t])

                    # Update Progress Dialog
                    progUpdate = '\nNotch Filter:\t{:>6}%'.format(
                        np.round(100. * (t + 1) / nChannels, 1))
                    dlg.Update(counter, progText + progUpdate)
                    counter += 1
                progText += '\nNotch Filter:\t{:>6}%'.format(100.0)

            progText += '\n'

            # Create epochs
            self.preFrame = int(
                np.round(self.preEpoch * self.sampleRate * 0.001))
            self.preCut = np.copy(self.preFrame)
            self.postFrame = int(
                np.round(self.postEpoch * self.sampleRate * 0.001))
            self.postCut = np.copy(self.postFrame)

            # Drop markers if there's not enough preFrame or postFrame to cut
            cutsIO = [True if m > self.preCut and m < tmpDataset.shape[
                1] - self.postCut else False for m in d.markerTime]

            epochs = np.array([tmpDataset[:, m - self.preCut:m + self.postCut]
                               for m in d.markerTime[np.where(cutsIO)]])

            # Accumulate epoch information
            if i == 0:
                Data.epochs = epochs
                Data.markers = d.markerValue[np.where(cutsIO)]
                Data.labelsChannel = d.labelsChannel
            else:
                Data.epochs = np.vstack((Data.epochs, epochs))
                Data.markers = np.hstack(
                    (Data.markers, d.markerValue[np.where(cutsIO)]))

            # Clean up of temporary files and variables
            del tmpDataset
            if exists(tmpFilename):
                remove(tmpFilename)

        dlg.Destroy()

        self.updateEpochs(Data)

    def updateEpochs(self, Data):

        # Get Specifications
        self.baselineCorr = Data.Specs.DropDownBase.GetSelection()
        self.bridgeCorr = Data.Specs.CheckboxBridge.GetValue()
        self.blinkCorr = Data.Specs.CheckboxBlink.GetValue()
        self.thresholdCorr = Data.Specs.CheckboxThreshold.GetValue()
        try:
            self.threshold = float(Data.Specs.ThreshValue.GetValue())
        except ValueError:
            self.threshold = 80.0
            Data.Specs.ThreshValue.SetValue(str(self.threshold))
        self.ignoreChannel = Data.Specs.channels2ignore

        # Don't check ignored channels for thresholding
        channel2Check = [i for i, e in enumerate(Data.labelsChannel)
                         if e not in self.ignoreChannel]

        # Copy epoch values
        epochs = np.copy(Data.epochs)

        # Baseline Correction
        if self.baselineCorr:

            for e in epochs:

                # if pre2zero is selected
                if self.baselineCorr == 1:
                    baselineAvg = [[c] for c in np.mean(
                        e[:, self.preCut - self.preFrame:self.preCut], axis=1)]

                # if pre2post is selected
                elif self.baselineCorr == 2:
                    baselineAvg = [[c] for c in e.mean(axis=1)]

                e -= baselineAvg

        # Common parameters
        emptyMatrix = np.zeros(
            (epochs.shape[0], epochs.shape[1])).astype('bool')
        self.matrixThreshold = np.copy(emptyMatrix)
        self.matrixBridge = np.copy(emptyMatrix)
        self.matrixBlink = np.zeros(
            (epochs.shape[0], epochs.shape[2])).astype('bool')

        # Correct Epochs for Threshold, Bridge and Blink outliers
        if self.thresholdCorr or self.bridgeCorr or self.blinkCorr:

            # Create Progressbar for outlier detection
            progressMax = epochs.shape[0]
            dlg = wx.ProgressDialog(
                "Outlier detection progress",
                "Time remaining for Outlier Detection", progressMax,
                style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_SMOOTH)

            # Go through all the epochs
            for i, e_long in enumerate(epochs):

                e_short = epochs[i][:,
                                    self.preCut - self.preFrame:self.preCut +
                                    self.postFrame]

                # Check for Threshold outliers
                badThresholdChannelID = []
                if self.thresholdCorr:
                    badChannels = np.where(
                        ((e_short > self.threshold) |
                         (e_short < -self.threshold)).mean(axis=1))[0]
                    badChannels = [b for b in badChannels
                                   if b in channel2Check]
                    self.matrixThreshold[i][badChannels] = True

                # Check for Bridge outliers
                if self.bridgeCorr:
                    corrMatrix = np.where(np.corrcoef(e_short) > .9999)
                    badBridgeChannelID = np.unique(
                        [corrMatrix[0][m] for m in range(len(corrMatrix[0]))
                         if corrMatrix[0][m] != corrMatrix[1][m]])
                    if badBridgeChannelID.size != 0:
                        self.matrixBridge[i][
                            np.unique(badBridgeChannelID)] = True

                # Check for Blink outliers
                if self.blinkCorr:
                    channels2Check = [j for j in range(e_long.shape[0])
                                      if j not in badThresholdChannelID]
                    stdOverTime = e_long[channels2Check].std(axis=0)
                    stdThresh = 3
                    blinkTimes = stdOverTime > stdOverTime.mean() * stdThresh
                    blinks = np.where(blinkTimes)[0]
                    blinkGroups = np.split(
                        blinks, np.where(np.diff(blinks) != 1)[0] + 1)
                    blinkPhase = [b for b in blinkGroups if b.shape[0] > 10]
                    blinkTimes *= False
                    if blinkPhase != []:
                        blinkTimes[np.hstack(blinkPhase)] = True
                    if blinkTimes.sum() != 0:
                        self.matrixBlink[i][blinkTimes] = True

                dlg.Update(i)
            dlg.Destroy()

            # Specifying ID of good and bad epochs
            badIDs = self.matrixThreshold.sum(axis=1) \
                + self.matrixBridge.sum(axis=1) \
                + self.matrixBlink.sum(axis=1)
            self.badID = badIDs.astype('bool')
            self.okID = np.invert(self.badID)

        # Connect all epochs and markers to self
        self.epochs = epochs
        self.markers = Data.markers

        # Correct for selected outliers
        if not hasattr(self, 'matrixSelected'):
            self.matrixSelected = np.repeat('ok_normal', self.epochs.shape[0])
            self.matrixSelected[np.where(
                self.matrixThreshold.sum(axis=1))[0]] = 'threshold'
            self.matrixSelected[np.where(
                self.matrixBlink.sum(axis=1))[0]] = 'blink'
            self.matrixSelected[np.where(
                self.matrixBridge.sum(axis=1))[0]] = 'bridge'

        else:

            # Check if new datasets were loaded
            if self.matrixSelected.shape[0] < self.markers.shape[0]:
                startID = self.matrixSelected.shape[0]
                newLength = self.markers.shape[0] - startID
                newSelectedMatrix = np.repeat('ok_normal', newLength)
                newSelectedMatrix[np.where(self.matrixThreshold[
                    startID:].sum(axis=1))[0]] = 'threshold'
                newSelectedMatrix[np.where(self.matrixBlink[
                    startID:].sum(axis=1))[0]] = 'blink'
                newSelectedMatrix[np.where(self.matrixBridge[
                    startID:].sum(axis=1))[0]] = 'bridge'
                self.matrixSelected = np.hstack([self.matrixSelected,
                                                 newSelectedMatrix])

            # Correct if correction filters are on
            if self.thresholdCorr:
                self.matrixSelected[
                    [i for i in np.where(self.matrixThreshold.sum(axis=1))[0]
                     if self.matrixSelected[i] == 'ok_normal']] = 'threshold'
            if self.bridgeCorr:
                self.matrixSelected[
                    [i for i in np.where(self.matrixBridge.sum(axis=1))[0]
                     if self.matrixSelected[i] == 'ok_normal']] = 'bridge'
            if self.blinkCorr:
                self.matrixSelected[
                    [i for i in np.where(self.matrixBlink.sum(axis=1))[0]
                     if self.matrixSelected[i] == 'ok_normal']] = 'blink'

        # Make sure that channels are ignored, even in a already loaded dataset
        if self.ignoreChannel != []:
            id2threshold = np.where(self.matrixThreshold.sum(axis=1))[0]
            idSelected = np.where(self.matrixSelected == 'threshold')[0]
            id2Clean = [ic for ic in idSelected if ic not in id2threshold]
            self.matrixSelected[id2Clean] = 'ok_normal'

        # Correct if correction filters are off
        if not self.thresholdCorr:
            self.matrixSelected[
                [i for i, e in enumerate(self.matrixSelected)
                 if 'thresh' in e]] = 'ok_normal'
            self.matrixThreshold *= False
        if not self.bridgeCorr:
            self.matrixSelected[
                [i for i, e in enumerate(self.matrixSelected)
                 if 'bridge' in e]] = 'ok_normal'
            self.matrixBridge *= False
        if not self.blinkCorr:
            self.matrixSelected[
                [i for i, e in enumerate(self.matrixSelected)
                 if 'blink' in e]] = 'ok_normal'
            self.matrixBlink *= False

        # Update List of ok and bad IDs
        self.okID = np.array([True if 'ok_' in e else False
                              for e in self.matrixSelected])
        self.badID = np.invert(self.okID)

        # Drop bad Epochs for average
        goodEpochs = epochs[self.okID]
        goodMarkers = self.markers[self.okID]

        # Create average epochs but weighs collapsed markers accordingly
        if not hasattr(self, 'collapsedMarkers'):
            self.uniqueMarkers = np.unique(goodMarkers)
            self.avgEpochs = [
                goodEpochs[np.where(goodMarkers == u)].mean(axis=0)
                for u in self.uniqueMarkers]
        else:
            # Create average epochs but weigh collapsed markers
            self.avgEpochs = []
            self.uniqueMarkers = np.unique(self.collapsedMarkers[self.okID])

            for i, u in enumerate(self.uniqueMarkers):

                # Weigh collapsed markers to get average
                if len(self.markers[self.markers == u]) == 0:

                    collapseID = [c[1] for c in self.collapsedTransform
                                  if c[0] == u][0]
                    self.avgEpochs.append(
                        np.array([goodEpochs[np.where(
                            goodMarkers == c)[0]].mean(axis=0)
                            for c in collapseID]).mean(axis=0))
                else:
                    self.avgEpochs.append(
                        goodEpochs[np.where(goodMarkers == u)[0]].mean(axis=0))

            self.markers = self.collapsedMarkers

        self.origAvgEpochs = np.copy(self.avgEpochs)
        self.interpolationCheck(Data)

    def interpolationCheck(self, Data):

        # Interpolate channels if necessary
        if Data.Specs.channels2interpolate != []:

            interpolatedEpochs = interpolateChannels(
                np.array(self.origAvgEpochs),
                Data.Specs.channels2interpolate,
                Data.Specs.xyzFile)

            self.avgGFP = [calculateGFP(a) for a in interpolatedEpochs]
            self.avgGMD = [calculateGMD(a) for a in interpolatedEpochs]

            self.avgEpochs = [e for e in interpolatedEpochs]

        else:
            self.avgGFP = [calculateGFP(a) for a in self.origAvgEpochs]
            self.avgGMD = [calculateGMD(a) for a in self.origAvgEpochs]

            self.avgEpochs = np.copy(self.origAvgEpochs)

        Data.Overview.update(self)

        # Don't show more if no epoch survived
        if self.okID.sum() != 0:
            Data.GFPSummary.update(self)
            Data.GFPDetail.update(self)
            Data.EpochsDetail.update([])
            Data.ERPSummary.update([])


def butter_bandpass_param(fs, highcut=0, lowcut=0, order=2, notch=-1.0):

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
    return b, a


def calculateGFP(dataset):
    # Global Field Potential
    return dataset.std(axis=0)


def calculateGMD(dataset):
    # Global Map Dissimilarity
    GFP = calculateGFP(dataset)
    unitaryStrength = dataset / GFP
    GMD = np.diff(unitaryStrength).std(axis=0)
    return np.insert(GMD, 0, 0)


def interpolateChannels(epochs, channels2interpolate, xyz):

    xyz = ReadXYZ(xyz)

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

    for count, epoch in enumerate(epochs):

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
        epochs[count] = signal.T

    return epochs
