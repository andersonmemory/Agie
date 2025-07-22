# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Setting up the path
import sys
from pathlib import Path

sys.path.insert(0, str(Path('..').resolve()))
sys.path.insert(0, str(Path('..', 'src').resolve()))
sys.path.insert(0, str(Path('..', 'src/utils').resolve()))
sys.path.insert(0, str(Path('..', 'src/cogs').resolve()))

# Define the 'coro' substitution for async functions
rst_epilog = """
.. |coro| replace:: :py:obj:`async`
"""

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Agie'
copyright = '2025, andersonmemory'
author = 'andersonmemory'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'press'
html_static_path = ['_static']
