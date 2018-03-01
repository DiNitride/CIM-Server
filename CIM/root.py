"""
This file serves no purpose other than to set the server directory as a system enviroment variable.
Wherever this root.py file is located will be the root directory, which should always be in the CIM root server file.
"""

import os

ROOT = os.path.dirname(__file__)
os.environ["CIM_ROOT"] = ROOT
