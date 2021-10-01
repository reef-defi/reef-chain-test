# reef-test

Reef Integration Test Suite

## Description 

This application is concerned with integration testing of reef components.
The application leverages pytest-bdd which is a behaviour driven development
plugin for pytest.  Many of the reef components are not python based and therefore
docker is leveraged as the virtualisation layer for non-python component execution.

## Installation

This repo supports installation via poetry or pip.

poetry:
```bash
make poetry-install
```

pip:
```bash
make pip-install
```

## Execution

```bash
make test
```

## Configuration
### Versioning
Non python component versions can be specified by updating the docker build context
reference in the `.env` file in the root of the repository.  python component 
versions are managed via the `pyproject.toml` / `requirmenets.txt`.

## Features

The following features are covered by this test suite.  Feature coverage will be increased incrementally.

- hardhat contract deployment and interaction
- REEF transfer and fee accounting
- pallet_staking bonding and nomination
