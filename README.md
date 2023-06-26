# Social network API

A simple REST API based social network in Django where Users can sign up and create text posts, as well as view, like, and unlike other Users’ posts.

## Tech Stack

The project is built using the following technologies:

- Python: The programming language used to develop the Django project.
- Django: A high-level Python web framework that provides a clean and pragmatic design for building web applications.
- Django REST Framework (DRF): A powerful and flexible toolkit for building Web APIs in Django.
- PostgreSQL: The preferred database system used for data persistence.
- Docker: The project is containerized using Docker, which allows for easy setup and deployment of the development environment.
- Docker Compose: Used for defining and running tests and the API.

## Libraries

The project incorporates the following libraries and packages:

- django-filter: A Django package that provides a simple way to filter down the queryset based on parameters passed via the query string.
- djangorestframework: A Django package that provides a set of REST API endpoints.
- djangorestframework-simplejwt: A Django package that provides JWT authentication.
- django-cors-headers: A Django package that adds Cross-Origin Resource Sharing (CORS) headers to responses, allowing your API to be accessed by different domains.
- Pillow: A Python Imaging Library (PIL) fork used for image processing.
- requests: A Python library used for making HTTP requests to external APIs.
- celery: A distributed task queue system for asynchronous processing.
- redis: An in-memory data structure store used as a broker for Celery in this project.

## Setup and Installation

### Clone the repository

```shell
git clone https://github.com/NoahNsimbe/social-network-backend.git
```

### Third party APIs

Create an abstract API key. Refer to <https://www.abstractapi.com/>

### Create a `.env` file

Execute the following command to create a .env file with required content.

```bash
chmod +x create-env.sh
./create-env.sh
```

## Running tests

Execute the following command in your terminal

```bash
chmod +x run-tests.sh
./run-tests.sh
```

## Start the server

Execute the following command in your terminal

```bash
chmod +x run-web.sh
./run-web.sh
```

Access the APIs by visiting <http://localhost:8000> in your web browser.
