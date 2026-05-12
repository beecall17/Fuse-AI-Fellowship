# Task 1: Database Setup with Docker Compose

In this task, I set up a PostgreSQL database using Docker Compose. I have created following files as the environment setup:
- docker-compose.yml
- .env
- scripts/seed.sql

along with these to secure the system i have created
- .gitignore
- .dockerignore
which ignores the .env file to protect the sensitive information.
and .yml file retrives the data from the .env file. 

Its better to use .env file because it protects the sentitive information from being exposed and keeping this file in .ignore prevets it from being pushed to the repository or log in git/docker.

Database is treated as a seprate service so that in future if we want to switch to another database service or scale we can do it without modifying the code for the api or rest of the application. 

Docker makes production and development environments consistent as it uses same setup, dependencies and configurations. To run a service inside a docker we don't manually have to install dependencies or set up the environment.


### Verification:
- docker exec -it bc1f6c81c6ab /bin/bash
- psql -U app_user -d classicmodels  (With incorrect user or db name throws and does not exit)
- \dt (listed all the tables)
- select count(*) from customers; (returned 122 customers)

Or similar approach with 
With the help of 'docker exec -it bc1f6c81c6ab psql -U app_user -d classicmodels' and \dt commands, I have verified the sucessful creation of tables in the database inside docker.

- docker exec -it -e TEST_VAR=hello_from_cmd bc1f6c81c6ab bash
- echo $TEST_VAR
- Result: hello_from_cmd

This showed the flexibility of docker exec command to pass environment variables to the container.

# Task 2: API Development with FastAPI

## Issue 1 - Port Miss-matched:
First issue i ran was the classic port mapping. The docker and host machine both set their ports on standard 5432. But my host machine was already connected to local postgresql on that port so while running the app, the app tried to connect to port 5432 but failed. So, with the help of netstat -ano | findstr :5432 found that two different PID were lisiting on that port. The database was in docker but app tired to find in the local host machine. 
### Solution: 
I changed the port and URL on .env file. 
Also found, the AI code on .yml had default value (set to the real crediential) along with binding from .env file, and removed that default value. 
Checked port with docker ps, and injecting print(Debug..) statement in the session.py to see the variables gatherd by the app.

## Issue 2 - PostgreSQL Version Syntax: 
In the code by AI, the code was written in v1, where the strings were passed directly in async engine.begin functions.

### Solution: 
Changed the code to use v2 syntax where the strings are passed as wrapped in the text() function to the async engine.begin functions. Also, found that we need to import txt from sqlalchemy. 

## Issue 3 - Circular Dependency / Mapping error:
Since in this task, we are only building the customer api, the relationships between customer with other tables i.e., order and payment were causing circular dependency and mapping errors. So, I commented out the relationships in the customer model. 

And did the Test on /docs endpoint. It worked with listing the customers with their details and get customer by customer id. Other CRUD operations are pending due to their dependency on other tables, which will be implemented in later tasks.


# Task 3: Concurrency (Twelve-Factor App)
In  this task, created all the endpoints for the remaining tables. As well as fixed the issues with the previous task. The CRUD operations for customer table is now working fine. 

No hard issues in this task. Just few database foreign key constrains issues while creating records in the models. 