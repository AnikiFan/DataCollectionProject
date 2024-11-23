import re
import ast

# 定义日志文件路径
log_file_path = 'Sensor_TILT_001.log'

# 定义正则表达式来匹配日志条目
log_pattern = re.compile(
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - '  # 时间戳
    r'Sensor_TILT_001 - '  # 传感器名称
    r'INFO - '  # 日志级别
    r'Sensor ID: (\w+), '  # 传感器ID
    r'Sensor Type: (\w+), '  # 传感器类型
    r'Status: (\w+), '  # 状态
    r'Data: ({.*})'  # 数据
)

# 读取日志文件
with open(log_file_path, 'r') as file:
    log_content = file.read()

# 解析日志内容
log_entries = log_pattern.findall(log_content)

# 打印解析后的日志条目
for entry in log_entries:
    timestamp, sensor_id, sensor_type, status, data_str = entry
    data = ast.literal_eval(data_str)
    print(f"Timestamp: {timestamp}")
    print(f"Sensor ID: {sensor_id}")
    print(f"Sensor Type: {sensor_type}")
    print(f"Status: {status}")
    print(f"Data: {data}")
    print("-" * 40)