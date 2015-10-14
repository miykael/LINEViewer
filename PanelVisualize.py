import wx
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar


def newFigure(self):
    self.figure = plt.figure(facecolor=(0.95, 0.95, 0.95))
    self.canvas = FigureCanvas(self, wx.ID_ANY, self.figure)
    self.toolbar = NavigationToolbar(self.canvas)

    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
    self.sizer.Add(self.toolbar, 0, wx.EXPAND)
    self.SetSizer(self.sizer)
    self.Fit()


def findSquare(number):
    s1 = int(np.round(np.sqrt(number)))
    s2 = int(np.ceil(1.0 * number / s1))
    return s1, s2


def getXaxis(Results):
    stepSize = (Results.preEpoch + Results.postEpoch) / \
        (Results.preFrame + Results.postFrame)
    xaxis = [int(i * stepSize - Results.preEpoch)
             for i in range(Results.preFrame + Results.postFrame)]
    return xaxis


class GFPDetailed(wx.Panel):

    def __init__(self, ParentFrame, MainFrame):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.MainFrame = MainFrame
        newFigure(self)

    def update(self, Results):

        if self.MainFrame.Datasets == []:
            newFigure(self)
        else:
            self.figure.clear()
            figureShape = findSquare(Results.uniqueMarkers.shape[0])
            xaxis = getXaxis(Results)
            for i, g in enumerate(Results.avgGFP):
                axes = self.figure.add_subplot(figureShape[0],
                                               figureShape[1],
                                               i + 1)
                axes.plot(xaxis, Results.avgGFP[i])
                nMarkers = np.where(
                    Results.markers == Results.uniqueMarkers[i])[0].shape[0]
                axes.title.set_text(
                    'Marker: %s [N=%s]' % (Results.uniqueMarkers[i], nMarkers))
                axes.grid(True)
            self.figure.subplots_adjust(left=0.03,
                                        bottom=0.03,
                                        right=0.98,
                                        top=0.97,
                                        wspace=0.20,
                                        hspace=0.24)
            self.canvas.draw()


class GFPSummary(wx.Panel):

    def __init__(self, ParentFrame, MainFrame):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=ParentFrame, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.MainFrame = MainFrame
        newFigure(self)

    def update(self, Results):
        if self.MainFrame.Datasets == []:
            newFigure(self)
        else:
            self.figure.clear()
            xaxis = getXaxis(Results)
            plt.plot(xaxis, np.transpose(Results.avgGFP))
            plt.xlabel('time [ms]')
            plt.ylabel('GFP')
            plt.title('GFP Overview')
            plt.legend(Results.uniqueMarkers)
            self.figure.subplots_adjust(left=0.03,
                                        bottom=0.04,
                                        right=0.98,
                                        top=0.97)
            plt.grid(True)
            self.canvas.draw()

    """
    a1 = epochs[:,0,:]
    a1Mean=a1.mean(axis=0)
    a1STD=a1.std(axis=0)
    #plt.figure()
    plt.plot(a1Mean, 'b')
    plt.fill_between(range(a1Mean.shape[0]),
                           a1Mean-2*a1STD,
                           a1Mean+2*a1STD,
                           color='b',
                           alpha=0.2)
    plt.show()
    """
