@echo off
rem Obviously ChatGPT translated .sh to .bat so idk if this is correct
rem Change to the 'docs' directory
cd /d "%~dp0"

rem Install the package
cd ..
pip install .
cd docs

rem Run sphinx-apidoc on the '../src' directory and output to 'source'
sphinx-apidoc ../src -o source

rem Run 'make clean' and 'make html'
make clean
make html
