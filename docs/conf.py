# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from datetime import date

import requests

year = date.today().strftime("%Y")

sys.path.insert(0, os.path.abspath("."))

# Get a Bibtex reference file from the Zotero group for referencing
url = "https://api.zotero.org/groups/4846265/collections/M9ZRDX2U/items/"
params = {"format": "bibtex", "style": "apa", "limit": 100}

r = requests.get(url=url, params=params)
with open("references.bib", mode="w") as file:
    file.write(r.text)

# Get a Bibtex reference file from the Zotero group for publications list
url = "https://api.zotero.org/groups/4846265/collections/UR7PHVDK/items/"
params = {"format": "bibtex", "style": "apa", "limit": 100}

r = requests.get(url=url, params=params)
with open("publications.bib", mode="w") as file:
    file.write(r.text)

# -- Project information -----------------------------------------------------

project = "pyet"
copyright = "{}, M. Vremec, R.A. Collenteur".format(year)
author = "M. Vremec, R.A. Collenteur"

# The full version, including alpha/beta/rc tags
release = "2020"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "IPython.sphinxext.ipython_console_highlighting",  # lowercase didn't work
    "sphinx.ext.autosectionlabel",
    "sphinxcontrib.bibtex",
    "myst_nb",
    "numpydoc",
    "sphinx_design",
]

# Create custom bracket style with round brackets
# From https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html

from dataclasses import dataclass, field
import sphinxcontrib.bibtex.plugin

from sphinxcontrib.bibtex.style.referencing import BracketStyle
from sphinxcontrib.bibtex.style.referencing.author_year import AuthorYearReferenceStyle


def bracket_style() -> BracketStyle:
    return BracketStyle(
        left="(",
        right=")",
    )


@dataclass
class MyReferenceStyle(AuthorYearReferenceStyle):
    bracket_parenthetical: BracketStyle = field(default_factory=bracket_style)
    bracket_textual: BracketStyle = field(default_factory=bracket_style)
    bracket_author: BracketStyle = field(default_factory=bracket_style)
    bracket_label: BracketStyle = field(default_factory=bracket_style)
    bracket_year: BracketStyle = field(default_factory=bracket_style)


sphinxcontrib.bibtex.plugin.register_plugin(
    "sphinxcontrib.bibtex.style.referencing", "author_year_round", MyReferenceStyle
)

bibtex_bibfiles = ["references.bib", "publications.bib"]
bibtex_reference_style = "author_year_round"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "**.ipynb_checkpoints"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "pydata_sphinx_theme"
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_logo = "_static/logo.png"
html_use_smartypants = True
html_show_sourcelink = True

html_theme_options = {
    "use_edit_page_button": True,
    "header_links_before_dropdown": 6,
    "icon_links": [
        {
            "name": "GitHub",  # Label for this link
            "url": "https://github.com/pyet-org/pyet",  # required
            "icon": "fab fa-github-square",
            "type": "fontawesome",  # Default is fontawesome
        }
    ],
}

autosummary_generate = True
numpydoc_show_class_members = False

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
}

# -- myst_nb options ------------------------------------------------------------------

nb_execution_allow_errors = True  # Allow errors in notebooks, to see the error online
nb_execution_mode = "auto"

# Enable specific MyST extensions, such as "dollarmath" for math rendering
myst_enable_extensions = [
    "dollarmath",
]

# -- Numpydoc settings ----------------------------------------------------------------

numpydoc_class_members_toctree = True
numpydoc_show_class_members = False
