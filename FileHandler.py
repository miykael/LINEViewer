import tables
import numpy as np
from os import makedirs
from os.path import exists, basename, join


class ReadBDF:

    def __init__(self, filename):

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
        self.startDate = startDate
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


class SaveH5:

    def __init__(self, filename, bdffiles):

        with tables.open_file(filename, 'w') as outputfile:

            for b in bdffiles:

                name = basename(b)[:-3]

                with tables.open_file(b, 'r') as f:

                    outputfile.create_group('/', name)
                    outputfile.create_array('/%s' % name, 'startDate',
                                            f.root.startDate.read())
                    outputfile.create_array('/%s' % name, 'startTime',
                                            f.root.startTime.read())
                    outputfile.create_array('/%s' % name, 'dataRecorded',
                                            f.root.dataRecorded.read())
                    outputfile.create_array('/%s' % name, 'durationRecorded',
                                            f.root.durationRecorded.read())
                    outputfile.create_array('/%s' % name, 'labelsChannel',
                                            f.root.labelsChannel.read())
                    outputfile.create_array('/%s' % name, 'sampleRate',
                                            f.root.sampleRate.read())
                    outputfile.create_array('/%s' % name, 'sampleEqual',
                                            f.root.sampleEqual.read())
                    outputfile.create_array('/%s' % name, 'rawdata',
                                            f.root.rawdata.read())
                    outputfile.create_array('/%s' % name, 'markerTime',
                                            f.root.markerTime.read())
                    outputfile.create_array('/%s' % name, 'markerValue',
                                            f.root.markerValue.read())


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


class SaveTVA:

    def __init__(self, data):

        dataSize = [e.markerValue.shape[0]
                    for i, e in enumerate(data.Datasets)]
        tvaMarker = [1 if 'ok_' in m else 0
                     for m in data.Results.matrixSelected]

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
