.PHONY: setup start start-debug stop clean help build logs

# Variables
COMPOSE_FILE = app/dev/docker-compose.yml

help:
	@echo "Available commands:"
	@echo "  make setup      - Setup direnv"
	@echo "  make build      - Build all Docker images"
	@echo "  make start      - Start all services in detached mode"
	@echo "  make start-debug - Start all services in foreground with logs"
	@echo "  make stop       - Stop all containers"
	@echo "  make clean      - Stop containers and remove volumes"
	@echo "  make logs       - Show logs from all containers"
	@echo "  make logs-server - Show logs from server container"
	@echo "  make logs-worker - Show logs from worker container"

setup:
	@echo "Setting up direnv..."
	@if ! command -v direnv &> /dev/null; then \
		echo "direnv not found. Please install it:"; \
		echo "  On macOS: brew install direnv"; \
		echo "  On Linux: sudo apt-get install direnv"; \
		echo "Then add this to your shell config (~/.zshrc or ~/.bashrc):"; \
		echo "  eval \"\$$(direnv hook zsh)\" # for zsh"; \
		echo "  eval \"\$$(direnv hook bash)\" # for bash"; \
	else \
		direnv allow .; \
	fi

build:
	@echo "Building Docker images..."
	docker-compose -f $(COMPOSE_FILE) build

start:
	@echo "Starting all services in detached mode..."
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "Waiting for services to be ready..."
	@until docker-compose -f $(COMPOSE_FILE) exec -T app-psql pg_isready -U saas > /dev/null 2>&1; do \
		echo "Waiting for PostgreSQL..."; \
		sleep 2; \
	done
	@until docker-compose -f $(COMPOSE_FILE) exec -T app-redis redis-cli ping > /dev/null 2>&1; do \
		echo "Waiting for Redis..."; \
		sleep 2; \
	done
	@echo "All services are ready!"
	@echo "API Server is running at http://localhost:8080"
	@echo "Use 'make logs' to see the logs"

start-debug:
	@echo "Starting all services in foreground with logs..."
	docker-compose -f $(COMPOSE_FILE) up

stop:
	@echo "Stopping containers..."
	docker-compose -f $(COMPOSE_FILE) down

clean:
	@echo "Stopping containers and removing volumes..."
	docker-compose -f $(COMPOSE_FILE) down -v

logs:
	@echo "Showing logs from all containers..."
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-server:
	@echo "Showing logs from server container..."
	docker-compose -f $(COMPOSE_FILE) logs -f app-server

logs-worker:
	@echo "Showing logs from worker container..."
	docker-compose -f $(COMPOSE_FILE) logs -f app-worker

all: setup build start-debug
	@echo "Environment is ready!"
	@echo "API Server is running at http://localhost:8080"
	cd "C:\Users\Admin\Downloads\Collate Hiring"