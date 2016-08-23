#!/bin/bash

# Replace the version number in all files
sed -i 's/0\.2\.06/0\.2\.07/g' \
    ../setup.py \
    ../README.rst \
    ../lineviewer/__init__.py \
    ../lineviewer/Interface.py

cd ..
python setup.py sdist
twine register dist/LINEViewer-*  -r pypi
twine upload dist/LINEViewer-* -r pypi
rm -rf dist/ LINEViewer.egg-info/
