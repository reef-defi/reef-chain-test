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

## Storage Inspection
### To postgres
It is often of value to have visibility of the state of runtime storage.  Querying and analysing data via rpc can often 
be limiting and awkward. To improve query and analysis capabilities I have built a connector that allows for runtime 
storage to be dumped into a postgres database for analysis using SQL.  

Start a postgres database:
```bash
make postgres
```

Dump runtime storage:
```bash
python tests/storage.py to_postgres --rpc=wss://rpc-testnet.reefscan.com/ws
```

Connect to postgres server with client of your choice using connection string: 
`postgresql://test:test@localhost:5432/storage`

### Storage Comparison
It is often of interest to understand how runtime storage has changed between two
blocks.  For example during a runtime upgrade we would like a report of changes.  To this end
a utility has been developed to produce these reports:
```bash
python tests/storage.py compare <block_a> <block_b> [--rpc=<rpc>]
```

## TPS Benchmark
To assess the TPS of the reef chain network we have developed a script that saturates that transaction
pool such that there are sufficient extrinsics to saturate blocks.  This script can be
invoked via the following command:
```bash
python -m tests.tps.py execute [--rpc=<rpc> --seed=<seed> --target=<target> --tx-count=<tx> --pool-limit=<pool-limit> --mnemonic=<mnemonic> --type=<type>]
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
