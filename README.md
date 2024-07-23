# Link Scraper

Link Scraper is a Django-based web application that allows users to scrape and store links from web pages. It uses Celery for asynchronous task processing and Docker for containerization.

https://github.com/user-attachments/assets/eb37eccc-f76e-47ce-bf03-bfed833f404d

## Features

- User registration and authentication
- Web page scraping
- Link storage and management
- Asynchronous processing with Celery
- PostgreSQL database
- Redis for Celery backend
- Jupyter notebook integration for experimenting

## Prerequisites

- Docker
- Docker Compose

## Setup

1. Clone the repository:
```shell
git clone https://github.com/LucasDavid1/web-link-extraction.git
```
2. Create a `.env` file in the project root with the following content:
```json
DEBUG=True
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=testPassword
POSTGRES_HOST=db
POSTGRES_PORT=5432
JUPYTER_TOKEN=testPassword
```
3. Build and start the Docker containers:
```shell
make up
```
4. Apply database migrations:
```shell
make migrate
```

## Usage

- Access the web application at `http://localhost:8000`
- (OPTIONAL) Access Jupyter Lab at `http://localhost:8888` (use the token specified in `.env`)

## Run tests
```shell
make test
```


## Stop containers
```shell
make down
```

## Restart containers
```shell
make restart
```

## Project Structure

- `users`: Django app for user management
- `scraper`: Django app for web scraping functionality
- `link_scraper`: Main Django project directory

## API Endpoints

### Users App
- `/users/register/`: User registration
- `/users/login/`: User login
- `/users/logout/`: User logout

### Scraper App
- `/`: Page list
- `/page/<int:page_id>/`: Page detail
- `/add/`: Add new page for scraping
- `/page-detail/<uuid:page_id>/`: Page detail (UUID)
- `/get_link_count/<uuid:page_id>/`: Get link count for a page
- `/delete_page/<uuid:page_id>/`: Delete a scraped page
