import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import evaluate
st.set_page_config(layout="wide")
conn = sqlite3.connect(os.path.join(os.curdir,'identifier.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT DISTINCT location from sensors')
rooms = [e[0] for e in cursor.fetchall()]
st.header('传感器数据')
room = st.selectbox('请选择要查看的房间',rooms)
sensor_data = pd.read_sql_query(f"""with cur_data as
    (select max(data_id),sensor_id,data from sensor_data GROUP BY sensor_id)
select location,sensor_type,cur_data.sensor_id,cur_data.data from sensors,cur_data  where sensors.sensor_id == cur_data.sensor_id AND location = '{room}'
;""", conn)
sensor_data['evaluate'] = sensor_data.apply(evaluate,axis=1)
sensor_data.set_index('sensor_type',inplace=True)
temperature,pressure,tilt_x,tilt_y,humidity,light,vibration = st.columns(7)
col = [temperature,pressure,tilt_x,tilt_y,humidity,light,vibration]
for i,c in enumerate(['Temperature','Pressure','Tilt','Tilt','Humidity','Light','Vibration']):
    with col[i]:
        if c not in sensor_data.index:
            st.text(f"该房间尚未部署类型为'{c}'的传感器！")
        else:
            data = sensor_data.loc[c,'data']
            if c in ['Temperature', 'Pressure', 'Humidity', 'Light', 'Vibration']:
                data = float(data.split(':')[-1])
                st.metric(c, data,delta=sensor_data.loc[c,'evaluate'],delta_color='normal' if sensor_data.loc[c,'evaluate']=='Normal' else 'inverse')
            elif c == 'Tilt' and i ==2 :
                data = data.split(',')
                TX = float(data[0].split(':')[-1])
                TY = float(data[1].split(':')[-1])
                st.metric(c, TX,delta=sensor_data.loc[c,'evaluate'],delta_color='normal' if sensor_data.loc[c,'evaluate']=='Normal' else 'inverse')
            else:
                data = data.split(',')
                TX = float(data[0].split(':')[-1])
                TY = float(data[1].split(':')[-1])
                st.metric(c, TY,delta=sensor_data.loc[c,'evaluate'],delta_color='normal' if sensor_data.loc[c,'evaluate']=='Normal' else 'inverse')

for c in sensor_data.index:
    st.subheader(c)
    sensor_id = sensor_data.loc[c,'sensor_id']
    history = pd.read_sql_query(f"""
    SELECT timestamp,data from sensor_data where sensor_id = '{sensor_id}' ORDER BY timestamp DESC LIMIT 50
    """,conn)
    if c != 'Tilt':
        history.data = history.data.apply(lambda x:float(x.split(':')[-1]))
        history.rename(columns={'data':c},inplace=True)
        st.line_chart(history, x='timestamp', y=c)
    else:
        history['data_X'] = history.data.apply(lambda x:float(x.split(',')[0].split(':')[-1]))
        history['data_Y'] = history.data.apply(lambda x:float(x.split(',')[1].split(':')[-1]))
        history.rename(columns={'data_X':"Tilt_X",'data_Y':"Tilt_Y"},inplace=True)
        st.line_chart(history, x='timestamp', y='Tilt_X')
        st.line_chart(history, x='timestamp', y='Tilt_Y')


conn.close()
