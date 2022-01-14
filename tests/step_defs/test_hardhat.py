import re
import subprocess

from pytest_bdd import given, scenarios, then, when

scenarios("../features/hardhat.feature")


@given(
    "I deploy a flipper contract using hardhat",
    target_fixture="flipper_contract_initial_state",
)
def flipper_deploy(reef_local_net):
    result = subprocess.run(
        "docker-compose -f tests/assets/hardhat.yaml run hardhat_examples npx hardhat run scripts/flipper/deploy.js".split(),
        capture_output=True,
        text=True,
    )
    result = re.compile(r"\x1b[^m]*m").sub("", result.stdout)
    address = result.split("flipper_contract_address: '")[1].split("'")[0][2:]
    initial_value = result.split("New value: ")[1].split("\n")[0] == "true"
    return {"address": address, "value": initial_value}


@when(
    "I call the flip method on the contract",
    target_fixture="flipper_contract_final_state",
)
def flip_flipper(flipper_contract_initial_state):
    result = subprocess.run(
        f"docker-compose -f tests/assets/hardhat.yaml run -e FLIPPER_ADDRESS={flipper_contract_initial_state['address']} hardhat_examples npx hardhat run scripts/flipper/flip.js".split(),
        capture_output=True,
        text=True,
    )
    final_value = (
        re.compile(r"\x1b[^m]*m")
        .sub("", result.stdout)
        .split("New value after flip(): ")[1]
        .split("\n")[0]
        == "true"
    )
    return final_value


@then("I receive the opposite result")
def assert_flipped(flipper_contract_initial_state, flipper_contract_final_state):
    assert flipper_contract_initial_state["value"] != flipper_contract_final_state
