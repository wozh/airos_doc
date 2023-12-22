# Configuration file for the Sphinx documentation builder.

# -- Project information
from recommonmark.parser import CommonMarkParser

project = '智路OS路侧操作系统开发手册'
copyright = '2023 Baidu, Inc. All Rights Reserved'
author = 'wuzhaoheng'

release = '1.0'
version = '1.0.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'recommonmark', 'sphinx_markdown_tables'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

source_parsers = {
  '.md': CommonMarkParser,
}
source_suffix = ['.rst', '.md']