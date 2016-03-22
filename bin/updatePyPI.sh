#!/bin/bash

# Replace the version number in all files
sed -i 's/0\.1\.10/0\.1\.11/g' \
    ../setup.py \
    ../lineviewer/__init__.py \
    ../lineviewer/Interface.py

cd ..
python setup.py sdist
twine register dist/LINEViewer-*  -r pypi
twine upload dist/LINEViewer-* -r pypi
rm -rf dist/ LINEViewer.egg-info/
