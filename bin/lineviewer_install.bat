conda install -y wxpython
conda update -y matplotlib numpy scipy wxpython
pip install --upgrade pip
pip install --upgrade lineviewer
ipython --c "import lineviewer; lineviewer.gui()"