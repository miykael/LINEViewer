#!/bin/bash

# Replace the version number in all files
sed -i 's/0\.1\.11/0\.1\.12/g' \
    ../setup.py \
    ../README.rst \
    ../lineviewer/__init__.py \
    ../lineviewer/Interface.py

cd ..
python setup.py sdist
twine register dist/LINEViewer-*  -r pypi
twine upload dist/LINEViewer-* -r pypi
rm -rf dist/ LINEViewer.egg-info/
