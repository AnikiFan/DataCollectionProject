import streamlit as st
from utils import evaluate
import pandas as pd
import sqlite3
conn = sqlite3.connect('identifier.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sensors")
sensors_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(DISTINCT location) FROM sensors")
rooms_count = cursor.fetchone()[0]
st.set_page_config(layout="wide")
sensors = pd.read_sql_query("select max(log_id),sensor_id,location,status from log GROUP BY sensor_id ;", conn)
sensor_data = pd.read_sql_query("""with cur_data as
    (select max(data_id),sensor_id,data from sensor_data GROUP BY sensor_id)
select location,sensor_type,cur_data.data from sensors,cur_data  where sensors.sensor_id == cur_data.sensor_id
;""", conn)
evaluation = sensor_data.assign(evaluation=sensor_data.apply(evaluate,axis=1).map({"Normal":0,'Warning':1,'Danger':2})).groupby('location')[['evaluation']].sum()
warning_count = ((evaluation.evaluation>=3)&(evaluation.evaluation<5)).sum()
danger_count = (evaluation.evaluation>=5).sum()
normal_count = len(evaluation) - warning_count - danger_count
header1,header2 = st.columns(2)
evaluation['status'] = evaluation.evaluation.apply(lambda x: 'Danger' if x>=5 else ('Warning' if x >=3 else 'Normal'))
with header1:
    st.header('建筑结构安全监控系统')
with header2:
    st.metric('Location','上海嘉定区')
st.subheader('总体信息')
c1,c2,c3,c4=st.columns(4)
with c1:
    st.metric('#Room',rooms_count)
    st.metric('#Normal',normal_count)
    st.metric('#Warning',warning_count)
    st.metric('#Danger',danger_count)
with c2:
    st.metric('#Sensor', sensors_count)
    st.metric('#Normal', sum(sensors.status=='Normal'))
    st.metric('#Warning',sum(sensors.status=='Warning'))
    st.metric('#Fault',sum(sensors.status=='Fault'))
with c3:
    st.write('房间列表',evaluation.loc[:,['status']])
with c4:
    st.write('传感器列表',sensors.iloc[:,1:].set_index('sensor_id'))

with st.expander('传感器数据生成方法'):
    st.code("""
        @staticmethod
    def generate_random_sensor_data(sensor_type):
        if sensor_type == "Temperature":
            return {
                "temperature": round(random.uniform(25, 5), 2)
            }
        elif sensor_type == "Pressure":
            return {
                "pressure": max(round(random.gauss(200, 50), 2),0)
            }
        elif sensor_type == "Tilt":
            return {
                "tilt_x": round(random.gauss(0, 20), 2),
                "tilt_y": round(random.gauss(0, 20), 2)
            }
        elif sensor_type == "Humidity":
            return {
                "humidity": max(round(random.gauss(50, 10), 2),0)
            }
        elif sensor_type == "Light":
            return {
                "light": max(round(random.gauss(500, 200), 2),0)
            }
        elif sensor_type == "Vibration":
            return {
                "vibration": min(max(round(random.gauss(0.5, 0.1), 2),0),1)
            }
        else:
            raise ValueError("Unsupported sensor type")
    """)

with st.expander('健康状态评估方法'):
    st.code("""
def evaluate(row):
    sensor_type = row['sensor_type']
    data = row['data']
    if sensor_type in ['Temperature','Pressure','Humidity','Light','Vibration']:
        data = float(data.split(':')[-1])
    elif sensor_type == 'Tilt':
        data = data.split(',')
        TX = float(data[0].split(':')[-1])
        TY = float(data[1].split(':')[-1])
    if sensor_type == 'Temperature':
        if abs(data-25)<15:
            return 'Normal'
        elif abs(data-25)<20:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Pressure':
        if abs(data-200)<150:
            return 'Normal'
        elif abs(data-200)<200:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Humidity':
        if abs(data-50)<30:
            return 'Normal'
        elif abs(data-50)<40:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Light':
        if abs(data-500)<600:
            return 'Normal'
        elif abs(data-500)<800:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Vibration':
        if abs(data-0.5)<0.3:
            return 'Normal'
        elif abs(data-0.5)<0.4:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Tilt':
        if abs(TX)>80 or abs(TY)>80:
            return 'Danger'
        elif abs(TX)>60 or abs(TY)>60:
            return 'Warning'
        else:
            return 'Danger'def evaluate(row):
    sensor_type = row['sensor_type']
    data = row['data']
    if sensor_type in ['Temperature','Pressure','Humidity','Light','Vibration']:
        data = float(data.split(':')[-1])
    elif sensor_type == 'Tilt':
        data = float(data.split(','))
        TX = data[0].split(':')[-1]
        TY = data[1].split(':')[-1]
    if sensor_type == 'Temperature':
        if abs(data-25)<15:
            return 'Normal'
        elif abs(data-25)<20:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Pressure':
        if abs(data-200)<150:
            return 'Normal'
        elif abs(data-200)<200:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Humidity':
        if abs(data-50)<30:
            return 'Normal'
        elif abs(data-50)<40:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Light':
        if abs(data-500)<600:
            return 'Normal'
        elif abs(data-500)<800:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Vibration':
        if abs(data-0.5)<0.3:
            return 'Normal'
        elif abs(data-0.5)<0.4:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Tilt':
        if abs(TX)>80 or abs(TY)>80:
            return 'Danger'
        elif abs(TX)>60 or abs(TY)>60:
            return 'Warning'
        else:
            return 'Danger' 
    """)

weather = pd.read_sql_query('select * from weather_data ORDER BY timestamp DESC LIMIT 20',conn)
weather_info,weather_chart=st.columns([1.5,4])
with weather_info:
    st.metric('更新时间',weather.loc[0,'timestamp'])
    weather1,weather2,weather3 = st.columns(3)
    with weather1:
        st.metric('当前天气',weather.loc[0,'description'])
    with weather2:
        st.metric('风向',weather.loc[0,'wind_direction'])
    with weather3:
        st.metric('风力',weather.loc[0,'wind_power'])
with weather_chart:
    st.line_chart(weather.set_index('timestamp').loc[:,['temperature','humidity']])
