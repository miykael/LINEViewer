conda install -y wxpython
conda update conda -y
conda update anaconda -y
conda clean -ay
pip install --upgrade pip
pip install --upgrade lineviewer
python -c "import lineviewer; lineviewer.gui()"