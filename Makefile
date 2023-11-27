admin:
	cd infra && docker compose exec auth_service bash -c "python scripts.py"

start:
	cd infra && docker compose -f docker-compose-dev.yml up --build -d

stop:
	cd infra && docker compose -f docker-compose-dev.yml down -v

