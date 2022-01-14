
test:
	pytest -s -v

poetry-install:
	# TRAVIS_TAG hack around current setup.py configuration of py-reef-interface
	TRAVIS_TAG=0.1.3 poetry install

pip-install:
	TRAVIS_TAG=0.1.3 pip3 install -r requirements.txt

local-net:
	docker-compose -f tests/assets/reef-local-network.yaml up -d

local-explorer:
	NODE_CHAIN_CMD=--dev docker-compose -f tests/assets/reef-explorer/docker-compose.yml -p reef-explorer-dev up -d

local-explorer-down:
	docker-compose -f tests/assets/reef-explorer/docker-compose.yml -p reef-explorer-dev down

postgres:
	docker-compose -f tests/assets/postgres.yaml up -d

down:
	docker-compose -f tests/assets/reef-local-network.yaml down