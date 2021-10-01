import logging
import subprocess
import time

import pytest
from reefinterface import Keypair, ReefInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def reef_local_net():
    logger.info("Starting local network ")
    subprocess.run(
        ["docker-compose", "-f", "tests/assets/reef-local-network.yaml", "up", "-d"]
    )
    logger.info("Sleeping 5 seconds to wait for local network to start up")
    time.sleep(5)
    yield
    subprocess.run(
        ["docker-compose", "-f", "tests/assets/reef-local-network.yaml", "down"]
    )


@pytest.fixture(scope="session", autouse=True)
def reef(reef_local_net):
    reef = ReefInterface("ws://localhost:9944")
    yield reef
    reef.close()


@pytest.fixture(scope="session")
def alice_key():
    return Keypair.create_from_uri("//Alice")


@pytest.fixture(scope="session")
def alice_controller():
    return Keypair.create_from_uri("//Alice//stash")


@pytest.fixture(scope="session")
def bob_key():
    return Keypair.create_from_uri("//Bob")


@pytest.fixture(scope="session")
def charlie_controller():
    return Keypair.create_from_uri("//Charlie")


@pytest.fixture(scope="session")
def charlie_stash():
    return Keypair.create_from_uri("//Charlie//stash")
