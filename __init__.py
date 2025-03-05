"""
TermUN: UN Terminology checker and corrector for parallel texts
"""

__version__ = '0.1.0'

# Import and expose the main functions
from .src import *

# Expose getCandidates directly at the top level
from .src import getCandidates
