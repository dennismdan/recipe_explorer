import os
import sklearn

from run_time_constants import *
from src.ui import streamlit_ui

def runpycharm():
    os.system('streamlit run __main__.py')
    return

runpycharm()