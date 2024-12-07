import sqlite3
import os
import pandas as pd
import streamlit as st
st.set_page_config(layout="wide")
st.header('传感器日志')
conn = sqlite3.connect(os.path.join(os.curdir, 'identifier.sqlite'))
sensors = pd.read_sql('select sensor_id from sensors', conn)
sensor = st.selectbox('请选择要查看的传感器',sensors.sensor_id.tolist())
df = pd.read_sql_query(f"SELECT * from log WHERE sensor_id == '{sensor}' ORDER BY log_id DESC",conn)
conn.close()
st.subheader('传感器历史状态')
st.line_chart(df.iloc[:50,:],x='time',y='status')
st.subheader('传感器日志记录')
st.write(df)

