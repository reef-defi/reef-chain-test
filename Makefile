test:
	pytest -s -v

poetry-install:
	# TRAVIS_TAG hack around current setup.py configuration of py-reef-interface
	TRAVIS_TAG=0.1.3 poetry install

pip-install:
	TRAVIS_TAG=0.1.3 pip install -r requirements.txt

local-net:
	docker-compose -f tests/assets/reef-local-network.yaml up -d

down:
	docker-compose -f tests/assets/reef-local-network.yaml down