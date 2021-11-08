import logging
import subprocess
import time

import pytest
from reefinterface import Keypair, ReefInterface

from tests.config import ERC2_DEPLOYMENT_BYTECODE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def reef_local_net():
    logger.info("Starting local network ")
    subprocess.run("make local-net".split())
    logger.info("Sleeping 5 seconds to wait for local network to start up")
    time.sleep(5)
    yield
    subprocess.run("make down".split())


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


@pytest.fixture(scope="session")
def erc20_deployment_bytecode():
    """
    // SPDX-License-Identifier: GPL-3.0

    pragma solidity >=0.7.0 <0.9.0;

    import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

    /**
     * @title ERC20Contract
     * @dev Very simple ERC20 Token example, where all tokens are pre-assigned to the creator.
     * Note they can later distribute these tokens as they wish using transfer and other
     * ERC20 functions.
     * Based on https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v2.5.1/contracts/examples/SimpleToken.sol
     */
    contract ERC20Contract is ERC20 {
        /**
         * @dev Constructor that gives msg.sender all of existing tokens.
         */
        constructor(
            uint256 initialSupply
        ) ERC20('ERC20Contract','ERC20C') {
            _mint(msg.sender, initialSupply);
        }
    }
    """
    return ERC2_DEPLOYMENT_BYTECODE
