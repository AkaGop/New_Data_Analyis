# app.py
import streamlit as st
from config import CEID_MAP
from log_parser import parse_log_file
from analyzer import analyze_data

st.set_page_config(page_title="Hirata Log Analyzer - Fresh Start", layout="wide")
st.title("Hirata Equipment Log Analyzer - Step 1: Foundation")

st.success("App structure is correct! All modules imported successfully.")

st.subheader("Testing Imports:")
st.write("`config.py` loaded:", "OK" if CEID_MAP else "Failed")

parser_result = parse_log_file(None)
st.write("`log_parser.py` loaded:", "OK" if parser_result else "Failed")

analyzer_result = analyze_data(None)
st.write("`analyzer.py` loaded:", "OK" if analyzer_result else "Failed")

st.info("We have a stable foundation. Ready to proceed to the next step.")
