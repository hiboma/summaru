shell:
	poetry shell

test:
	pytest

run:
	python bot.py

dev/run:
	jurigged --poll 1 -i bot.py

watch:
	ptw

docker/up:
	docker compose up --build

docker/test:
	docker compose build
	docker compose run summaru pytest

prerelease:
	git pull origin main --tag
	ghch -w -N ${VER}
	git add CHANGELOG.md
	git commit -m'Bump up version number'
	git tag ${VER}

release:
	git push origin main --tag
