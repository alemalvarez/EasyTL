# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
#import sphinx_book_theme  # For Read the Docs theme

sys.path.insert(0, os.path.abspath('../..')) # We tell Sphinx where to find the code

project = 'EasyTL'
copyright = '2024, Alejandro Mata'
author = 'Alejandro Mata'
release = 'v0.4.0-beta'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc', # Automatically document all the code
]

templates_path = ['_templates']
#exclude_patterns = []

autoclass_content = 'both'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Default theme:
# html_theme = 'alabaster'
# html_static_path = ['_static']

# Read the Docs theme:
html_theme = 'sphinx_book_theme'
#html_theme_path = [sphinx_book_theme.get_html_theme_path()]
