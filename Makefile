.PHONY: help build up logs down

SERVICE ?= streamlit

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the streamlit service (usage: make build [SERVICE=service_name])
	docker compose build $(SERVICE)

up: ## Start all services in daemon mode
	docker compose up -d

logs: ## Show logs for a service (usage: make logs [SERVICE=service_name])
	docker compose logs -f $(SERVICE)

build: ## Force build a service without cache (usage: make build [SERVICE=service_name])
	docker compose build --no-cache $(SERVICE)
	docker compose up -d $(SERVICE)

down: ## Stop all services
	docker compose down
