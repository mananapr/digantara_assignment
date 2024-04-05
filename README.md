## Task 1: Schema Design
![schema](schema.png)

Code for the same can be found in the file `1_init.py`.

## Task 2: SQL Query
Code for this task is available in the file `2_sql_query.py`.

### 1. Pentagon Problem
- Random points selected are stored in the table `task_2_a_input`.
- Input values selected are also printed on the docker compose log.
- All the objects within the pentagon are stored in the table `task_2_a_output`.

### 2. Nearest Point Problem
- Random object selected can be seen in the table `task_2_b_input`.
- Data for the nearest object is stored in the table `task_2_b_output`.

## Task 3: Optimize Database Schema and Query Performance


## Setup
Setup and intial execution is handled by the Makefile.
1. `make build`: Builds the docker image. Only needs to be run once.
2. `make up`: Runs the containers for PostGIS, PgAdmin and Digantara (as defined in the Dockerfile).
3. `make down`: Stops the containers

*Note:* The extracted `Assignment data` folder should be present in the same directory.
