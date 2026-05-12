*For detailed journal do refer to JOURNAL.md*
# Task 1: Database Setup with Docker Compose
### Reflection:
Its better to use .env file because it protects the sentitive information from being exposed and keeping this file in .ignore prevets it from being pushed to the repository or log in git/docker.

Database is treated as a seprate service so that in future if we want to switch to another database service or scale we can do it without modifying the code for the api or rest of the application. 

Docker makes production and development environments consistent as it uses same setup, dependencies and configurations. To run a service inside a docker we don't manually have to install dependencies or set up the environment.


# Task 2: Customer API Development

## Task Overview:
The task was to create a customer API with CRUD operations using FastAPI and PostgreSQL with Docker Compose. Only could retrive the customers list and customer by its id from the database using the API. Other CRUD operations were not implemented due to dependency issues which resulted into Circular Dependency / Mapping error. They will be implemented and tested later on the project.

### Reflection:
Factor II: Dependencies: Encounter an issue with dependencies regarding async. The module was first supposed to work with psycorg2-binary but the code written by AI was requesting asyncpg which is a different module and had different syntax for connecting to the database. 
Had to research and download the correct module for the code to work. 

Factor III: Config Management: The environemnt varibales were wrriten in .env and other all the files retrived the connection strings from there. This made easier as I had to deal with ports mismatched. As, my localhost machine was using and auto loading wih the pc startup postgres on port 5432 whereas, the docker was also listening on the same port. Had to find the reasons, then see which ports were being used at the same time by which services. And changed the port to 5433 in .env file which auto loaded the configs on docker-compose.yml file.

As a result, the application was able to run smoothly without any conflicts. So, if any other users wants to use my app later on then they can simply clone the repo and set the ports according to their host machine using the .env.example file which has the blueprint of the .env file fileds (without credentials).

# Task 3: Concurrency (Twelve-Factor App)
In  this task, created all the endpoints for the remaining tables. As well as fixed the issues with the previous task. The CRUD operations for customer table is now working fine. 

No hard issues in this task. Just few database foreign key constrains issues while creating records in the models. 

All the models or tables are now connected for the future task 4 use where we will be implementing the business logic of creating the CRUD operations for all the tables.