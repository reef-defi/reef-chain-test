from pytest_bdd import given, scenarios, then, when
from reefinterface import ReefInterface
from reefinterface.base import Keypair

from tests.utils import get_account, get_balance

scenarios("../features/staking.feature")


@given("Charlie has a funded controller and stash account")
def charlie_stash_and_controller(
    reef_local_net, reef, charlie_stash, charlie_controller
):
    assert get_balance(reef, charlie_stash) > 0
    assert get_balance(reef, charlie_controller) > 0


@when("Charlie bonds 100000 REEF")
def charlie_bonds_reef(
    reef: ReefInterface, charlie_stash: Keypair, charlie_controller: Keypair
):
    call = reef.compose_call(
        call_module="Staking",
        call_function="bond",
        call_params={
            "controller": charlie_controller.public_key,
            "value": 100000 * 10 ** 18,
            "payee": "Stash",
        },
    )
    extrinsic = reef.create_signed_extrinsic(call=call, keypair=charlie_stash)
    reef.submit_extrinsic(extrinsic, wait_for_inclusion=True)


@given("charlie has 100000 REEF bonded")
@then("the staking pallet should reflect charlies bonding")
def bonding_assertions(reef, charlie_stash, charlie_controller):
    # assert controller has been set
    assert (
        reef.query("Staking", "Bonded", [charlie_stash.public_key]).value
        == charlie_controller.ss58_address
    )

    # assert staking ledger has been updated
    expected_ledger_entry = {
        "stash": charlie_stash.ss58_address,
        "total": 100000 * 10 ** 18,
        "active": 100000 * 10 ** 18,
        "unlocking": [],
        "claimedRewards": [],
    }
    assert (
        reef.query("Staking", "Ledger", [charlie_controller.public_key]).value
        == expected_ledger_entry
    )


@then("charlies stash account should have 100000 REEF frozen")
def balance_frozen_assertion(reef, charlie_stash):
    # assert bonded funds are frozen
    assert get_account(reef, charlie_stash)["data"]["feeFrozen"] == 100000 * 10 ** 18


@when("charlie nominates alice")
def charlie_nominates_alice(
    reef: ReefInterface, charlie_controller: Keypair, alice_controller: Keypair
):
    call = reef.compose_call(
        call_module="Staking",
        call_function="nominate",
        call_params={"targets": [alice_controller.public_key]},
    )
    extrinsic = reef.create_signed_extrinsic(call, charlie_controller)
    reef.submit_extrinsic(extrinsic, wait_for_inclusion=True)


@then("the staking pallet should be updated appropriately")
def nomination_assertions(reef, charlie_stash, alice_controller):
    expected_nomination = {
        "targets": [alice_controller.ss58_address],
        "submittedIn": 0,
        "suppressed": False,
    }
    assert (
        reef.query("Staking", "Nominators", [charlie_stash.public_key]).value
        == expected_nomination
    )
