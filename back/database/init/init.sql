DO SLEEP(10);

CREATE DATABASE IF NOT EXISTS secdb;
USE secdb;

CREATE TABLE IF NOT EXISTS User_roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  role VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS Users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) UNIQUE,
  email VARCHAR(255),
  role_id INT,
  salt VARCHAR(255),
  hash VARCHAR(255),
  FOREIGN KEY (role_id) REFERENCES User_roles(id)
);

CREATE TABLE IF NOT EXISTS Incident_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  type VARCHAR(255) UNIQUE,
  default_priority VARCHAR(255) CHECK (default_priority IN ('Normal', 'High'))
);

CREATE TABLE IF NOT EXISTS Incident_location_groups (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location_group VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS Incident_locations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location VARCHAR(255) UNIQUE,
  location_group_id INT,
  latitude DECIMAL(12,9),
  longitude DECIMAL(12,9),
  is_residence BOOLEAN,
  FOREIGN KEY (location_group_id) REFERENCES Incident_location_groups(id)
);

CREATE TABLE IF NOT EXISTS Incidents (
  id INT AUTO_INCREMENT PRIMARY KEY,
  description TEXT,
  location_id INT,
  incident_type_id INT,
  FOREIGN KEY (location_id) REFERENCES Incident_locations(id),
  FOREIGN KEY (incident_type_id) REFERENCES Incident_types(id)
);

CREATE TABLE IF NOT EXISTS Incident_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  incident_id INT,
  status VARCHAR(255) CHECK (status IN ('Open', 'Close')),
  priority VARCHAR(255) CHECK (priority IN ('Normal', 'High')),
  time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  user_id INT,
  notes TEXT,
  FOREIGN KEY (incident_id) REFERENCES Incidents(id),
  FOREIGN KEY (user_id) REFERENCES Users(id),
  UNIQUE (incident_id,time,status)
);
