from reefinterface import Keypair, ReefInterface


def get_balance(reef_interface: ReefInterface, keypair: Keypair):
    account = get_account(reef_interface=reef_interface, keypair=keypair)
    return account["data"]["free"] if account else None


def get_account(reef_interface: ReefInterface, keypair: Keypair):
    return reef_interface.query(
        module="System", storage_function="Account", params=[keypair.public_key]
    ).value
