shell:
	poetry shell

test:
	pytest

run:
	python bot.py

watch:
	ptw

docker/up:
	docker compose up --build

docker/test:
	docker compose build
	docker compose run summaru pytest
