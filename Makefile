# Makefile for Indirect Prompt Tester

.PHONY: help build up down logs shell test clean

help: ## Show this help message
	@echo "Indirect Prompt Tester - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker image
	docker-compose build

up: ## Start the application
	docker-compose up -d
	@echo "Application started! Access at http://localhost:8501"

down: ## Stop the application
	docker-compose down

logs: ## View application logs
	docker-compose logs -f indirect-prompt-tester

shell: ## Open a shell in the container
	docker-compose exec indirect-prompt-tester /bin/bash

cli: ## Run CLI command (usage: make cli CMD="generate --type image --prompt test --output test.png")
	docker-compose exec indirect-prompt-tester python -m indirect_prompt_tester.cli.main $(CMD)

test: ## Run tests (if available)
	docker-compose exec indirect-prompt-tester pytest || echo "No tests configured"

clean: ## Remove containers, volumes, and images
	docker-compose down -v
	docker rmi indirect-prompt-tester 2>/dev/null || true

rebuild: ## Rebuild the image from scratch
	docker-compose build --no-cache

restart: ## Restart the application
	docker-compose restart

status: ## Show container status
	docker-compose ps

