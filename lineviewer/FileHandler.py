import time
import numpy as np
from os import makedirs
from os.path import exists, join, basename


class ReadBDF:

    def __init__(self, filename):

        self.bdfFile = filename
        self.lvFile = filename[:-3] + 'lv'

        with open(filename, 'rb') as f:
            offset = 168
            f.seek(offset)
            startDate = f.read(8).strip()
            startTime = f.read(8).strip()
            offset += 68
            f.seek(offset)
            dataRecorded = int(f.read(8))
            durationRecorded = int(f.read(8))
            nbChannels = int(f.read(4))
            labelsChannel = np.array(
                [f.read(16).strip() for i in range(nbChannels)])

            offset += 20 + 216 * nbChannels
            f.seek(offset)
            sampleRate = [int(f.read(8)) for i in range(nbChannels)]
            sampleEqual = np.unique(sampleRate).shape[0] == 1
            sampleRate = sampleRate[0]

            offset += (40) * nbChannels

        if not exists(self.lvFile):

            with open(filename, 'rb') as f:
                f.seek(offset)
                rawdata = np.fromfile(f, dtype='uint8').reshape(-1, 3)

            zeroarray = np.zeros((rawdata.shape[0], 1), dtype='uint8')
            # 8-bit shift for negative integers
            zeroarray[rawdata[:, 2] >= 128] += 255
            rawdata = np.array(
                np.hstack((rawdata, zeroarray)), dtype='uint8')
            rawdata = (
                rawdata.flatten().view('i4') / 32.).astype('float32')
            rawdata = rawdata.reshape(
                dataRecorded, nbChannels, sampleRate)
            rawdata = np.rollaxis(
                rawdata, 1).reshape(nbChannels, -1)

            lvFile = np.memmap(self.lvFile, mode='w+', dtype='float32',
                               shape=rawdata.shape)
            lvFile[:] = rawdata[:]

        rawdata = np.memmap(self.lvFile, mode='r', dtype='float32',
                            shape=(nbChannels, sampleRate * dataRecorded))

        # Create Marker value and timestamp
        status = rawdata[np.where(labelsChannel == 'Status')][0]
        status = status - np.median(status)
        timepoint = (np.diff(status) != 0).nonzero()[0] + 1
        markerTime = timepoint[np.where(status[timepoint] != 0)]
        markerValue = np.uint8(status[markerTime] * 32)

        # Prepare output
        self.rawdata = rawdata[:-1, :]
        self.startDate = '20%s/%s/%s' % (
            startDate[6:8], startDate[3:5], startDate[:2])
        self.startTime = startTime
        self.dataRecorded = dataRecorded
        self.durationRecorded = durationRecorded
        self.labelsChannel = labelsChannel[:-1]
        self.sampleRate = sampleRate
        self.sampleEqual = sampleEqual
        self.markerTime = markerTime
        self.markerValue = markerValue


class ReadXYZ:

    def __init__(self, filename):

        with open(filename) as f:
            content = f.readlines()
            self.coord = []
            self.labels = []
            for i, e in enumerate(content):
                if i != 0:
                    coord = e.split()
                    self.coord.append([float(coord[0]),
                                       float(coord[1]),
                                       float(coord[2])])
                    self.labels.append(coord[3])
            self.coord = np.array(self.coord)
            self.labels = np.array(self.labels)


class SaveTVA:

    def __init__(self, data, precut, postcut):

        dataSize = [
            len([m for m in e.markerTime
                 if m > precut and m < e.rawdata.shape[1] - postcut])
            for e in data.Datasets]
        tvaMarker = [
            1 if 'ok_' in m else 0 for m in data.Results.matrixSelected]

        # Go through the files and save TVA for each
        counter = 0
        for i, n in enumerate(data.Filenames):
            filename = join(data.DirPath, n + '.lv.tva')

            with open(filename, 'w') as f:

                f.writelines('TV01\n')

                for j in range(dataSize[i]):
                    f.writelines('%d\t0\t%s\n' % (
                        tvaMarker[counter], data.Results.markers[counter]))

                    counter += 1


class SaveEPH:

    def __init__(self, resultsName, resultsPath, results, markers2hide,
                 preFrame):

        # Create output folder if it doesn't exist
        if not exists(resultsPath):
            makedirs(resultsPath)

        # Go through all the markers
        for i, m in enumerate(results.uniqueMarkers):

            # Do nothing if marker was hidden
            if m in markers2hide:
                continue

            # Write GFP data into EPH file
            nTimepoint = results.avgGFP[0].shape[0]
            filename = '%s.Epoch_%.3d.GFP.eph' % (resultsName, m)
            with open(join(resultsPath, filename), 'w') as f:
                f.writelines('{:>15}\t{:>15}\t{:>25}\n'.format(
                    1, nTimepoint, results.sampleRate))
                for tValue in results.avgGFP[i]:
                    f.writelines('{:>15}\n'.format(round(tValue, 7)))

            # Write GFP marker file
            filename += '.mrk'
            with open(join(resultsPath, filename), 'w') as f:
                f.writelines(
                    'TL02\n{:>12}\t{:>12}\t"Origin"\n'.format(preFrame,
                                                              preFrame))

            # Write electrode data into EPH file
            nSignal, nTimepoint = results.avgEpochs[0].shape
            filename = '%s.Epoch_%.3d.eph' % (resultsName, m)
            with open(join(resultsPath, filename), 'w') as f:
                f.writelines('{:>15}\t{:>15}\t{:>25}\n'.format(
                    nSignal, nTimepoint, results.sampleRate))
                for tValues in results.avgEpochs[i].T:
                    formatString = '{:>15}\t' * nSignal
                    formatString = formatString[:-1] + '\n'
                    f.writelines(
                        formatString.format(*np.round(tValues, 7).tolist()))

            # Write EPH marker file
            filename += '.mrk'
            with open(join(resultsPath, filename), 'w') as f:
                f.writelines(
                    'TL02\n{:>12}\t{:>12}\t"Origin"\n'.format(preFrame,
                                                              preFrame))


class SaveFigures:

    def __init__(self, resultsName, resultsPath, figures):

        figures.Overview.figure.savefig(
            join(resultsPath, 'plot_Overview.svg'), bbox_inches='tight')
        figures.GFPSummary.figure.savefig(
            join(resultsPath, 'plot_GFP_Summary.svg'), bbox_inches='tight')
        figures.GFPDetailed.figure.savefig(
            join(resultsPath, 'plot_GFP_Detailed.svg'), bbox_inches='tight')

        markers = figures.EpochSummary.ComboMarkers.GetItems()[1:]
        for m in markers:
            figures.EpochSummary.update(int(m))
            figures.EpochSummary.figure.savefig(
                join(resultsPath, 'plot_Average_Marker_%.3d.svg' % int(m)),
                bbox_inches='tight')


class SaveVerbose:

    def __init__(self, resultsName, resultsPath, data):

        # abbreviation to shorten variable name
        res = data.Results

        # Write Verbose File
        with open(join(resultsPath, '%s.vbs' % resultsName), 'w') as f:
            f.writelines('Verbose File\n============\n\n')
            f.writelines('LINEViewer (Version %s)\n' % data.VERSION)
            f.writelines('%s\n\n\n' % time.strftime('%Y/%m/%d %H:%M:%S'))

            # Information about the preprocessing
            f.writelines(
                'Processing Information:\n-----------------------\n\n')

            f.writelines('DC removed\t\t\t:\t%s\n' % res.removeDC)
            f.writelines('Reference to\t\t:\t%s\n' % res.newReference)
            highcut = res.highcut if res.highcut != 0 else 'None'
            lowcut = res.lowcut if res.lowcut != 0 else 'None'
            f.writelines('High-pass filter\t:\t%s\n' % highcut)
            f.writelines('Low-pass filter\t\t:\t%s\n' % lowcut)
            notch = res.notchValue if res.doNotch else 'None'
            f.writelines('Notch\t\t\t\t:\t%s\n' % notch)
            f.writelines('\n')

            f.writelines('Interpolated ch.\t:\t%s\n' %
                         data.Specs.channels2interpolate)
            xyzFile = data.Specs.xyzFile if data.Specs.xyzFile != '' \
                else 'None'
            f.writelines('XYZ-file path\t\t:\t%s\n' % xyzFile)
            f.writelines('\n')

            f.writelines('Epoch duration pre\t:\t%sms / %s sampling points\n' %
                         (res.preEpoch, res.preFrame))
            f.writelines(
                'Epoch duration post\t:\t%sms / %s sampling points\n' %
                (res.postEpoch, res.postFrame))
            f.writelines('Baseline correction\t:\t%s\n' % res.baselineCorr)
            f.writelines('Blink correction\t:\t%s\n' % res.blinkCorr)
            f.writelines('Bridge correction\t:\t%s\n' % res.bridgeCorr)
            f.writelines('Thresh. correction\t:\t%s\n' % res.thresholdCorr)
            f.writelines('Threshold [mikroV]\t:\t%s\n' % res.threshold)
            f.writelines('Channels excluded\t:\t%s\n' %
                         data.Specs.channels2exclude)
            f.writelines('\n')

            if hasattr(res, 'collapsedTransform'):
                collapsedInfo = [
                    '%s -> %s' % (res.collapsedTransform[e], e)
                    for e in res.collapsedTransform]
                collapsedInfo = ', '.join(collapsedInfo)
            else:
                collapsedInfo = 'None'
            f.writelines('Markers collapsed\t:\t%s\n' % collapsedInfo)
            f.writelines('Markers hidden\t\t:\t%s\n' % data.markers2hide)
            f.writelines('\n\n')

            # Information about the average output
            f.writelines('Average Information:\n--------------------\n\n')

            epochsTotal = res.epochs.shape[0]
            epochsOK = res.okID.sum()
            percentOK = np.round(float(epochsOK) / epochsTotal, 2) * 100
            f.writelines('Channels #\t\t\t:\t%s\n' % res.epochs.shape[1])
            f.writelines('Markers #\t\t\t:\t%s\n' % len(res.uniqueMarkers))
            f.writelines('Marker value\t\t:\t%s\n' %
                         ', '.join(res.uniqueMarkers.astype('str')))
            f.writelines('Epochs total #\t\t:\t%s\n' % epochsTotal)
            f.writelines(
                'Epochs in average\t:\t{0} / {1}%\n'.format(epochsOK,
                                                            percentOK))
            f.writelines('\n')

            selected = len(np.where(res.matrixSelected == 'selected')[0])
            ok_normal = len(np.where(res.matrixSelected == 'ok_normal')[0])
            threshold = len(np.where(res.matrixSelected == 'threshold')[0])
            ok_thresh = len(np.where(res.matrixSelected == 'ok_thresh')[0])
            blink = len(np.where(res.matrixSelected == 'blink')[0])
            ok_blink = len(np.where(res.matrixSelected == 'ok_blink')[0])
            bridge = len(np.where(res.matrixSelected == 'bridge')[0])
            ok_bridge = len(np.where(res.matrixSelected == 'ok_bridge')[0])
            modeInfo = '[automatic detection / manually switched]'
            f.writelines('Epochs accepted\t\t:\t%s / %s %s\n' %
                         (ok_normal, selected, modeInfo))
            f.writelines('Epochs threshold\t:\t%s / %s %s\n' %
                         (threshold, ok_thresh, modeInfo))
            f.writelines('Epochs Blink\t\t:\t%s / %s %s\n' %
                         (blink, ok_blink, modeInfo))
            f.writelines('Epochs Bridge\t\t:\t%s / %s %s\n' %
                         (bridge, ok_bridge, modeInfo))
            f.writelines('\n\n')

            # Information about the channel overview
            f.writelines(
                'Overview Channel Outliers:\n----------------------------\n\n')

            nFaultyChannels = res.OxaxisChannel.shape[0]
            distChannelThreshold = res.OdistChannelThreshold[-nFaultyChannels:]
            distChannelBridge = res.OdistChannelBridge[-nFaultyChannels:]
            percentageChannel = np.round(
                res.OpercentageChannels[-nFaultyChannels:], 3) * 100
            percentageMarker = np.round(res.OpercentageMarker, 3) * 100
            nChannelOutliers = sum(distChannelThreshold) + \
                sum(distChannelBridge)

            f.writelines('Outliers Total #\t:\t%s\n' % nChannelOutliers)
            f.writelines('Outliers Selected\t:\t{0} / {1}%\n'.format(
                res.OnSelectedOutliers, np.round(
                    float(res.OnSelectedOutliers) / epochsTotal, 3) * 100))
            f.writelines('Outliers Broken\t\t:\t{0} / {1}%\n'.format(
                res.OBroken, np.round(
                    float(res.OBroken) / epochsTotal, 3) * 100))
            f.writelines('Outliers Blink\t\t:\t{0} / {1}%\n'.format(
                res.OBlink, np.round(float(res.OBlink) / epochsTotal, 3) * 100))
            f.writelines('\n')

            f.writelines('Channel Name\t\t:%s\n' %
                         ('{:>6}' * nFaultyChannels).format(
                             *res.OxaxisChannel))
            f.writelines('Outliers %\t\t\t:{0}\n'.format(
                ('{:>6}' * nFaultyChannels).format(*percentageChannel)))
            f.writelines('Threshold #\t\t\t:%s\n' % (
                '{:>6}' * nFaultyChannels).format(*distChannelThreshold))
            f.writelines('Bridge #\t\t\t:%s\n' %
                         ('{:>6}' * nFaultyChannels).format(
                             *distChannelBridge))
            f.writelines('\n\n')

            # Information about the marker overview
            f.writelines(
                'Overview Marker Outliers:\n---------------------------\n\n')

            nMarkers = len(res.OxaxisMarker)
            f.writelines('Outliers Total\t\t:\t{0} / {1}%\n'.format(
                res.OoutlierEpochs, np.round(
                    float(res.OoutlierEpochs) / epochsTotal, 3) * 100))
            f.writelines('Marker Name\t\t\t:%s\n' %
                         ('{:>6}' * nMarkers).format(*res.OxaxisMarker))
            f.writelines('Outliers %\t\t\t:{0}\n'.format(
                ('{:>6}' * nMarkers).format(*percentageMarker)))
            f.writelines('OK #\t\t\t\t:%s\n' %
                         ('{:>6}' * nMarkers).format(*res.OdistMarkerOK))
            f.writelines('Selected #\t\t\t:%s\n' %
                         ('{:>6}' * nMarkers).format(*res.OdistMarkerSelected))
            f.writelines('Threshold #\t\t\t:%s\n' %
                         ('{:>6}' * nMarkers).format(
                             *res.OdistMarkerThreshold))
            f.writelines('Bridge #\t\t\t:%s\n' %
                         ('{:>6}' * nMarkers).format(*res.OdistMarkerBridge))
            f.writelines('Blink #\t\t\t\t:%s\n' %
                         ('{:>6}' * nMarkers).format(*res.OdistMarkerBlink))
            f.writelines('Broken #\t\t\t:%s\n' %
                         ('{:>6}' * nMarkers).format(*res.OdistMarkerBroken))
            f.writelines('\n\n')

            # Information about input files
            f.writelines('Input File(s):\n--------------\n\n')
            f.writelines('Number of input file(s):\t%s\n\n' %
                         len(data.Datasets))

            for i, d in enumerate(data.Datasets):

                f.writelines('File #\t\t\t\t:\t%s\n' % i)
                f.writelines('File name\t\t\t:\t%s\n' % basename(d.bdfFile))
                f.writelines('File path\t\t\t:\t%s\n' % d.bdfFile)
                f.writelines('Timestamp\t\t\t:\t%s:%s %s\n' %
                             (d.startTime[:2], d.startTime[3:5], d.startDate))
                duration = round(float(d.dataRecorded) * d.durationRecorded, 1)
                f.writelines('Lenght\t\t\t\t:\t%sm%ss\n' %
                             (int(duration) / 60, int(duration) % 60))
                f.writelines('Sampling freq.\t\t:\t%s Hz\n' % d.sampleRate)
                f.writelines('Sampling points\t\t:\t%s\n' % d.rawdata.shape[1])
                f.writelines('Channels #\t\t\t:\t%s\n' % d.labelsChannel.shape)
                uniqueMarkers = np.unique(d.markerValue)
                f.writelines('Markers #\t\t\t:\t%s\n' % len(uniqueMarkers))
                f.writelines('Marker value\t\t:\t%s\n' %
                             ', '.join(uniqueMarkers.astype('str')))
                f.writelines('\n')
            f.writelines('\n')

            # Information about output files
            f.writelines('Output Files:\n-------------\n\n')
            f.writelines('Folder name\t\t\t:\t%s\n' % resultsName)
            f.writelines('Output path\t\t\t:\t%s\n' % resultsPath)
