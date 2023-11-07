## Table of Contents 

* [Start Database]
* [Container Information]
  

## Start Database

Files used: * Indicated scripts
back
   |-- database
   |   |-- add_incidents
   |   |   |-- read_from_csv.py
   |   |-- init
   |   |   |-- init.sql *
   |   |-- populate
   |   |   |-- Incident_location.csv
   |   |   |-- Incident_location_groups.csv
   |   |   |-- Incident_types.txt
   |   |   |-- User_roles.txt
   |   |   |-- Users.csv
   |   |   |-- defaults.py *
   |   |   |-- requirements.txt *
   |-- database_pop_dockerfile *
   |-- docker-compose.yml *

Steps:
1. Run the below in terminal
$ docker compose up --build
2. Head to http://localhost:8080 to check database tables are up
- Container: database
- Database: secdb
- Username: root
- Password: [check with user]

## Container information

There are 3 containers in docker-compose.yml:
1. database
- Creates image of MySQL database 
2. database-manage
- Creates image of adminer on localhost:8080 to manage tables
3. database-pop
- Populates database with users and csv of past incidents
- Subfolders:
  - init: Initialises 7 blank MySQL tables
  - populate: Populates User_roles, Incident_locations, Incident_location_groups, Incident_types
  - add_users: Adds users (to be updated)
  - add_incidents: Adds incidents to Incidents and IncidentLogs


