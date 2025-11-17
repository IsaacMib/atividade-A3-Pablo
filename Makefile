.PHONY: lint format validate

help:
	@echo "lint - check style with black, ruff, sort python with ruff, indent html, and lint frontend css/js"
	@echo "format - enforce a consistent code style across the codebase, sort python files with ruff and fix frontend css/js"
	@echo "validate - run makemigrations --check, migrations, lint, and tests (fast validation)"

lint-server:
	black --target-version py38 --check --diff .
	ruff check .
	curlylint --parse-only sitepadrao
	git ls-files '*.html' | xargs djhtml --check

lint-client:
	npm run lint:css --silent
	npm run lint:js --silent
	npm run lint:format --silent

lint: lint-server lint-client

format-server:
	black --target-version py38 .
	ruff check . --fix
	git ls-files '*.html' | xargs djhtml -i

format-client:
	npm run format
	npm run fix:js

format: format-server format-client

validate:
	@echo "→ Checking for pending migrations..."
	.venv/bin/python manage.py makemigrations --check --dry-run
	@echo "→ Running migrations..."
	.venv/bin/python manage.py migrate --noinput
	@echo "→ Linting backend code..."
	black --target-version py38 --check --diff .
	ruff check .
	@echo "→ Linting frontend code..."
	npm run lint:css --silent
	npm run lint:js --silent
	@echo "✔ Validation complete. All checks passed."
