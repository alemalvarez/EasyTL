#!/bin/zsh

# Change to the 'docs' directory
cd "$(dirname "$0")"

# Install the package
cd ..
pip install .
cd docs

# Run sphinx-apidoc on the '../src' directory and output to 'source'
sphinx-apidoc ../src -o source

# Run 'make clean' and 'make html'
make clean
make html