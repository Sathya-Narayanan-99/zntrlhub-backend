# zntrlhub-backend

Welcome to zntrlhub-backend! This repository contains the backend code for the ZntrlHub project.

## Getting Started

### Prerequisites
Before getting started, ensure you have Docker installed on your machine. You can download the latest version of Docker from [https://download.docker.com/mac/stable/Docker.dmg]().

### Setup

1. Clone this repository and navigate to the `zntrlhub-backend` folder.
2. Run the command `docker-compose build` to build the Docker images. This process may take some time.
3. Once the build is complete, run `docker-compose up -d` to start the required services specified in the Docker Compose file.
4. To tail the logs of the web server, you can use the command `docker logs --follow zntrlhub-web`.

## Usage

Once the containers are up and running, you can start using the zntrlhub-backend project. Here are some additional details to help you get started:

- Access the web server at `http://localhost:8000`.
- Access the API documentation at `http://localhost:8000/redoc`. This provides detailed information about the available endpoints and how to interact with the API.
- To perform any necessary configuration, check the respective configuration files or environment variables.

## Filters

This project uses `dj-rql` to provide RQL filtering support for the API endpoints. `dj-rql` seamlessly integrates with Django REST framework and allows for complex filtering and querying of data using RQL.

For more details on RQL syntax and available filter options, you can refer to the RQL documentation at [https://django-rql.readthedocs.io/en/latest/]().