"""
LINEViewer: Python based EEG analysis tool to give you a rough data overview

See: https://github.com/miykael/LINEViewer
"""

# Always prefer setuptools over distutils
from setuptools import setup

if __name__ == "__main__":
    setup(
        name='LINEViewer',
        packages=['lineviewer'],
        version='0.1.6',
        description='Python based EEG analysis tool for a rough data overview',
        long_description="""
        Python based EEG analysis tool to give you a rough data overview""",
        license='GNU GENERAL PUBLIC LICENSE',
        author='Michael Notter',
        author_email='michaelnotter@hotmail.com',
        url='https://github.com/miykael/LINEViewer',
        download_url='https://github.com/miykael/LINEViewer/releases/tag/0.1.6',
        keywords=['LINE', 'LINEViewer', 'EEG'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU Affero General Public License v3',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: OS Independent',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.7',
            'Topic :: Scientific/Engineering'],
        install_requires=[
            'matplotlib>=1.4', 'numpy>=1.9', 'scipy>=0.16', 'wxpython>=3.0'],
    )
