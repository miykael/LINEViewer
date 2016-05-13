==========
LINEViewer
==========

.. |logo| image:: lineviewer/static/favicon_256.ico
   :width: 256pt

.. |introText| replace:: LINEViewer is a python based EEG analysis toolbox that helps you to get a first impression of your data. The softwares is very fast in analysing your data and can compute subject averages of hour long datasets within seconds. You have all the preprocessing options that you know from other EEG analysis softwares.

+-------------+--------+
| |introText| | |logo| |
+-------------+--------+


Installation
-------------

LINEViewer is distributed via https://github.com/miykael/LINEViewer/. You can download the newest version under `releases <https://github.com/miykael/LINEViewer/releases>`_.

The software has the following dependencies:

* `python 2.7 <https://www.python.org/download/releases/2.7/>`_
* `matplotlib <http://matplotlib.org/>`_: version 1.5 or higher
* `numpy <http://www.numpy.org/>`_: version 1.9 or higher
* `scipy <http://www.scipy.org/>`_: version 0.16 or higher
* `wxpython <http://wiki.wxpython.org/How%20to%20install%20wxPython>`_: version 3.0 or higher

Full distributions like `Anaconda <https://www.continuum.io/why-anaconda>`_ provide all those packages, except `wxpython v3.0 <http://wiki.wxpython.org/How%20to%20install%20wxPython>`_.

Windows
*******
1. Download and install the `newest Anaconda distribution that includes Python 2.7 <https://www.continuum.io/downloads>`_.
2. Download and install the `current release of LINEViewer_install.exe <https://github.com/miykael/LINEViewer/releases/download/0.2.02/LINEViewer_install.exe>`_.
3. Download the `current release of LINEViewer.exe <https://github.com/miykael/LINEViewer/releases/download/0.2.02/LINEViewer.exe>`_, put it on your Desktop and open it to run LINEViewer on your system.

Alternatively, you can also use the installation instruction for Linux / iOS on a Windows machine - as long as you have `Anaconda <https://www.continuum.io/why-anaconda>`_ on your system.

Linux / iOS
***********

1. Download and install the `newest Anaconda distribution that includes Python 2.7 <https://www.continuum.io/downloads>`_.
2. Install newest version of wxpython on your system with ``conda install -y wxpython``
3. Update all dependencies to the newest version with ``conda update -y matplotlib numpy scipy wxpython``
4. Install LINEViewer with the command ``pip install --upgrade lineviewer``
5. Start LINEViewer on your system with the command ``ipython --c "import lineviewer; lineviewer.gui()"``


LINEViewer structure
--------------------

* ``bin/``: Contains the executables for Windows, as well as the corresponding batch files
* ``lineviewer/``: Contains the source code
* ``LICENSE``: LINEViewer license terms
* ``README``: This document
* ``setup.py``: Script for building and installing LINEViewer


License information
-------------------

The full license is in the file ``LICENSE``. The image of the brain in the logo was created with `MRIcroGL <http://www.mccauslandcenter.sc.edu/mricrogl/>`_ and the font used is called Ethnocentric Regular, created and licensed by Ray Larabie (http://typodermicfonts.com/).
