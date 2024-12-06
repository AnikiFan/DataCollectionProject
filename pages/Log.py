import sqlite3
import os
import pandas as pd
import streamlit as st
st.set_page_config(layout="wide")
conn = sqlite3.connect(os.path.join(os.curdir, 'identifier.sqlite'))
df = pd.read_sql_query("SELECT * from log ORDER BY log_id DESC",conn)
conn.close()
st.header('传感器日志')
st.write(df)

