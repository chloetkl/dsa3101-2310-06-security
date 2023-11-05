## Table of Contents 

* [Start Database]
* [Container Information]
  

## Start Database

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


