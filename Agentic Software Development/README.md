*For detailed journal do refer to JOURNAL.md*
# Task 1: Database Setup with Docker Compose
### Reflection:
Its better to use .env file because it protects the sentitive information from being exposed and keeping this file in .ignore prevets it from being pushed to the repository or log in git/docker.

Database is treated as a seprate service so that in future if we want to switch to another database service or scale we can do it without modifying the code for the api or rest of the application. 

Docker makes production and development environments consistent as it uses same setup, dependencies and configurations. To run a service inside a docker we don't manually have to install dependencies or set up the environment.
