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