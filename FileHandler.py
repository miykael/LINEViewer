import tables
import numpy as np
from os.path import exists, basename


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
            durationRecorded = int(f.read(8))  # in seconds
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
