
# ------------------------------------------------------------------
# Author:           jcy
# Created:          2024/09/20
# Description:      Main Function:    简单的爬虫程序获取指定网址的天气信息  
# Function List:    
# History:
#       <author>        <version>       <time>      <desc>
# Else:         爬虫也有更加高明的方式，可爬取具有更加详细的网址，敬请尝试
# ------------------------------------------------------------------

import requests
import re
import json

city_codes = {
    '北京': '101010100',
    '上海': '101020100',
    '成都': '101270101',
    '嘉定': '101020500',
    # 其他城市代码
}

# 互联网数据获取
def get_weather_from_internet(city):
    if city not in city_codes:
        raise ValueError(f"City code for {city} not found")
    
    city_code = city_codes[city]
    url = f'http://www.weather.com.cn/weather1d/{city_code}.shtml'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    timeout = 10
    response = requests.get(url, headers=headers, stream=True, timeout=timeout)
    
    if response.status_code != 200:
        raise ValueError("Failed to retrieve content")

    pattern = re.compile(r'var observe24h_data = (.*?);')
    match = pattern.search(response.text)
    
    if match:
        json_str = match.group(1)
        data = json.loads(json_str)
        latest_data = data['od']['od2'][0]
        temperature = latest_data['od22']
        humidity = latest_data['od27']
        weather = 1  # 0 sunny, 1 cloudy, 2 ... # 这个后面可以自己修改成类似的定义，或者从爬取内容中获取
        return weather, temperature, humidity
    else:
        print("未找到温湿度信息")
        return None, None

city = '嘉定'
   
weather, temperature, humidity = get_weather_from_internet(city)
if temperature and humidity:
    print(f'The temperature in {city} is {temperature}, humidity is {humidity}, weather is {weather}')
else:
    print(f"Failed to retrieve temperature and humidity for {city}")