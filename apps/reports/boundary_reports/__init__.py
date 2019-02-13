"""
This module handles all the number calculations for Project 1 million reports. Requires specific inputs 
to generate reports. Returns values in a JSON to the HTML templates for rendering.
"""
from .base import *
from .block import *
from .cluster import *
from .district import *
from .school import *
from .gpcontest import *

if __name__ == "__main__":
    r= ReportOne();
    r.get_data
