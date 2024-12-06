DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS sensor_data;
DROP TABLE IF EXISTS log;
DROP TABLE IF EXISTS weather_data;
CREATE TABLE sensors(
    sensor_id VARCHAR(50) PRIMARY KEY ,
    sensor_type VARCHAR(50) NOT NULL,
    location VARCHAR(50) NOT NULL
);
CREATE TABLE sensor_data(
    data_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id VARCHAR(50) REFERENCES sensors(sensor_id),
    timestamp TIMESTAMP NOT NULL DEFAULT  CURRENT_TIMESTAMP,
    data JSON NOT NULL
);
CREATE TABLE log(
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(50) REFERENCES  sensors(sensor_id),
    sensor_type VARCHAR(50) NOT NULL,
    location VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    data JSON NOT NULL
);
CREATE TABLE weather_data(
    timestamp TIMESTAMP NOT NULL ,
    location VARCHAR(100) NOT NULL ,
    description VARCHAR(50) NOT NULL ,
    temperature INT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    wind_direction VARCHAR(10) NOT NULL,
    wind_power VARCHAR(10) NOT NULL,
    humidity INT NOT NULL,
    PRIMARY KEY (timestamp,location)
);