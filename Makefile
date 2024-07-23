.PHONY: build up up-logs down restart logs shell migrate makemigrations test test-app test-app-class createapp createsuperuser
SERVICE_NAME := web

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting Django application..."
	docker-compose up -d --build
	@echo "Django application started at http://localhost:8000"


down:
	@echo "Stopping Django application..."
	docker-compose down

restart:
	@echo "Restarting Django application..."
	docker-compose down
	docker-compose up -d --build
	@echo "Django application started at http://localhost:8000"

logs:
	@echo "Fetching logs..."
	docker-compose logs -f

shell:
	@echo "Opening shell..."
	docker-compose exec $(SERVICE_NAME) sh

migrate:
	@echo "Applying migrations..."
	docker-compose exec $(SERVICE_NAME) python manage.py migrate

makemigrations:
	@echo "Creating new migrations..."
	docker-compose exec $(SERVICE_NAME) python manage.py makemigrations

test:
	@echo "[TEST]"
	docker-compose exec $(SERVICE_NAME) pytest
	@echo "Done"

test-app:
	@echo "Running tests for $(app_name)..."
	docker-compose exec $(SERVICE_NAME) pytest $(app_name)

test-app-class:
	@echo "Running tests for $(test_path)..."
	docker-compose exec app pytest $(shell find . -path "*/$(subst ::,*,$(test_path)).py")

createapp:
	@echo "Creating new Django app $(app_name)..."
	docker-compose exec $(SERVICE_NAME) python manage.py startapp $(app_name)

createsuperuser:
	@echo "Creating new Django superuser..."
	docker-compose exec $(SERVICE_NAME) python manage.py createsuperuser
