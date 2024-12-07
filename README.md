# 文件说明

1. `init.bat`：运行该文件以启动天气数据采集脚本、传感器模拟器和传感器数据接收器
2. `requirements.txt`：本实验所用环境配置文件
3. `sender.py`：传感器模拟器文件
4. `receiver.py`：传感器数据接受器
5. `get_weather.py`：天气数据采集脚本
6. `utils.py`：辅助函数
7. `identifier.sqlite`：SQLite数据库文件
8. `Dashboard.py`：Streamlit应用主界面文件
9. `pages\`：Streamlit子界面文件夹
10. `configs`:
    1. `init.sql`：用于初始化数据库
    2. `sensors.ini`：传感器配置文件
11. `logs\`：传感器日志输出文件夹

## 特别说明

1. 若想运行`get_weather.py`，应在`configs`文件夹下创建`.env`文件，并添加`KEY`字段，内容为高德地图天气数据API key。