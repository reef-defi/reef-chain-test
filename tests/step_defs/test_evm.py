from pytest_bdd import given, scenarios, then, when
from reefinterface import ExtrinsicReceipt, Keypair, ReefInterface

from tests.utils import get_balance

scenarios("../features/evm.feature")


@given("I have a funded account")
def assert_account_funded(reef: ReefInterface, alice_key: Keypair):
    assert get_balance(reef, alice_key) > 0


@when(
    "I deploy a contract using the Evm Create call",
    target_fixture="erc20_create_receipt",
)
def create_contract_call(
    reef: ReefInterface, alice_key: Keypair, erc20_deployment_bytecode: str
):
    call = reef.compose_call(
        call_module="EVM",
        call_function="create",
        call_params={
            "init": erc20_deployment_bytecode,
            "value": 0,
            "gas_limit": 5000000,
            "storage_limit": 50000,
        },
    )
    extrinsic = reef.create_signed_extrinsic(call, alice_key)
    receipt = reef.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    return receipt


@then(
    "I receive an Event with the contract address",
    target_fixture="erc20_contract_address",
)
def assert_contract_created(erc20_create_receipt: ExtrinsicReceipt):
    created_event = [
        event.value
        for event in erc20_create_receipt.triggered_events
        if event.value["module_id"] == "EVM" and event.value["event_id"] == "Created"
    ]
    assert erc20_create_receipt.is_success
    assert len(created_event) == 1
    assert created_event[0]["params"][0]["type"] == "EvmAddress"
    return created_event[0]["params"][0]["value"]


@given("Bob has a funded account")
def assert_bob_account_funded(reef: ReefInterface, bob_key: Keypair):
    assert get_balance(reef, bob_key) > 0


@when("bob claims the default EVM account")
def bob_claim_default_evm_account(reef: ReefInterface, bob_key: Keypair):
    call = reef.compose_call(
        call_module="EvmAccounts", call_function="claim_default_account"
    )
    extrinsic = reef.create_signed_extrinsic(call, bob_key)
    reef.submit_extrinsic(extrinsic, wait_for_inclusion=True)


@then("the account is assinged to bob", target_fixture="bob_evm_address")
def assert_bob_erc20(reef: ReefInterface, bob_key: Keypair):
    bob_evm_address = reef.query("EvmAccounts", "EvmAddresses", [bob_key.public_key])
    assert bob_evm_address is not None
    return bob_evm_address


# @given("I have an erc20 contract deployed")
# def assert_contract_exists(erc20_contract_address):
#     assert erc20_contract_address is not None
#
#
# @when("I transfer 200 units to Bob")
# def transfer_200_to_bob(reef: ReefInterface, alice_key: Keypair, bob_evm_address: str, erc20_contract_address: str):
#     call_input = f"0xa9059cbb000000000000000000000000{bob_evm_address[2:]}00000000000000000000000000000000000000000000000000000000000000c8"
#     call = reef.compose_call(call_module="EVM", call_function="call", call_params={"target": erc20_contract_address, "input": call_input, "value": 0, "gas_limit": 500000, "storage_limit": 5000})
#     extrinsic = reef.create_signed_extrinsic(call, alice_key)
#     receipt = reef.submit_extrinsic(extrinsic, wait_for_inclusion=True)
#
#
# @then("Bobs erc20 balance increases by 200")
# def bobs_balance_increases_200(reef: ReefInterface, bob_evm_address: str):
#     pass
