"""
TermUN: UN Terminology checker and corrector for parallel texts
"""

__version__ = '0.1.0'

# Expose getCandidates directly at the top level
from .src import getCandidates

# Import and expose the main functions
from .src import *