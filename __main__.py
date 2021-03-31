import os
from run_time_constants import *
from src.ui import streamlit_ui

def main():
    #this is good practice because the whole code base is the application ui is just and entry point.
    streamlit_ui.app()
    return

if __name__ == "__main__":
    main()