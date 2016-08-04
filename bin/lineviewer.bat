conda create -y -n lineviewer-2.7 python=2.7 pip ipython matplotlib numpy scikit-learn scipy wxpython
call activate lineviewer-2.7
conda clean -yiltp
pip install --upgrade lineviewer
python -c "import lineviewer; lineviewer.gui()"