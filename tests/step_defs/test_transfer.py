from pytest import approx
from pytest_bdd import given, scenarios, then, when
from reefinterface import ReefInterface
from reefinterface.base import Keypair

from tests.config import TOLERANCE
from tests.utils import get_balance

scenarios("../features/transfer.feature")


@given("We have balances for Alice and Bob", target_fixture="initial_balances")
def accounts(reef_local_net, reef, alice_key, bob_key):
    return {"alice": get_balance(reef, alice_key), "bob": get_balance(reef, bob_key)}


@when("Alice sends 100000 REEF to Bob", target_fixture="transaction_fee")
def alice_sends_reef_to_bob(reef: ReefInterface, alice_key: Keypair, bob_key: Keypair):
    call = reef.compose_call(
        call_module="Balances",
        call_function="transfer",
        call_params={"dest": bob_key.public_key, "value": 100000 * 10 ** 18},
    )
    extrinsic = reef.create_signed_extrinsic(call=call, keypair=alice_key)
    receipt = reef.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    return receipt.total_fee_amount


@then(
    "Alices balance decreases by 100000 REEF + fees and Bobs balance increases by 100000 REEF"
)
def balance_change(reef, alice_key, bob_key, initial_balances, transaction_fee):
    assert get_balance(reef, alice_key) == approx(
        initial_balances["alice"] - (100000 * 10 ** 18) - transaction_fee, abs=TOLERANCE
    )
    assert get_balance(reef, bob_key) == approx(
        initial_balances["bob"] + (100000 * 10 ** 18), abs=TOLERANCE
    )
