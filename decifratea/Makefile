.PHONY: help install lint format test run migrate makemigrations shell createsuperuser clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install          - Instala as dependências de desenvolvimento"
	@echo "  make lint             - Verifica a qualidade do código"
	@echo "  make format           - Formata o código automaticamente"
	@echo "  make test             - Executa os testes"
	@echo "  make run              - Inicia o servidor de desenvolvimento"
	@echo "  make migrate          - Aplica as migrações do banco de dados"
	@echo "  make makemigrations   - Cria novas migrações"
	@echo "  make shell            - Abre o shell do Django"
	@echo "  make createsuperuser  - Cria um superusuário"
	@echo "  make clean            - Remove arquivos temporários"

install:
	pip install -r requirements/dev.txt
	pre-commit install

lint:
	@echo "Executando black (check)..."
	black --check .
	@echo "Executando isort (check)..."
	isort --check-only .
	@echo "Executando ruff..."
	ruff check .
	@echo "Executando flake8..."
	flake8 .

format:
	@echo "Formatando com black..."
	black .
	@echo "Organizando imports com isort..."
	isort .
	@echo "Corrigindo com ruff..."
	ruff check . --fix

test:
	pytest

test-cov:
	pytest --cov=. --cov-report=html --cov-report=term-missing

run:
	python manage.py runserver

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

shell:
	python manage.py shell_plus

createsuperuser:
	python manage.py createsuperuser

collectstatic:
	python manage.py collectstatic --noinput

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec web python manage.py shell_plus

docker-migrate:
	docker-compose exec web python manage.py migrate
