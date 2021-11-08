import logging
from time import sleep

from docopt import docopt
from reefinterface import Keypair, ReefInterface

from .config import ERC2_DEPLOYMENT_BYTECODE, REEF_DECIMALS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TPS test util")

PARSER = """
TPS test util.

Usage:
  tps.py execute [--rpc=<rpc> --seed=<seed> --target=<target> --tx-count=<tx> --pool-limit=<pool-limit> --mnemonic=<mnemonic> --type=<type>]

Options:
  -h --help                   Show this screen.
  --rpc=<rpc>                 rpc connection string [default: ws://localhost:9944]
  --seed=<seed>               seed phrase for origin account [default: //Alice]
  --target=<target>           ss58 / evm address of target account - default == //Bob [default: 5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty]
  --type=<type>               type of transactions to construct (evm / native) [default: native]
  --tx-count=<tx>             number of transactions to submit [default: 10000]
  --pool-limit=<pool-limit>   pool limit [default: 8000]
  --mnemonic=<mnemonic>       mnemonic phrase
"""


def cli():
    args = docopt(PARSER)
    logger.info(f"args: {args}")

    if args["execute"]:
        submit_extrinsics(
            args["--rpc"],
            args["--seed"],
            args["--mnemonic"],
            args["--target"],
            args["--type"],
            int(args["--tx-count"]),
            int(args["--pool-limit"]),
        )
    else:
        raise Exception("Command not supported!")


def submit_extrinsics(
    rpc: str,
    seed: str,
    mnemonic: str,
    target: str,
    tx_type: str,
    tx_count: int,
    pool_limit: int,
):
    # create reef client and keypair
    reef = ReefInterface(rpc)
    origin = (
        Keypair.create_from_mnemonic(mnemonic)
        if mnemonic
        else Keypair.create_from_uri(seed)
    )

    if tx_type == "evm":
        extrinsics = construct_evm_extrinsics(reef, origin, target, tx_count)
    elif tx_type == "native":
        extrinsics = construct_native_extrinsics(reef, origin, target, tx_count)
    else:
        raise Exception(f"tx type not supported! {tx_type}")

    # initialise result store and pool space counter
    results = {}
    pool_space = pool_limit - len(
        reef.rpc_request("author_pendingExtrinsics", [])["result"]
    )

    # submit and saturate transaction pool
    for nonce, extrinsic in extrinsics.items():
        while True:
            # loop until space available in pool
            if pool_space == 0:
                pool_space = pool_limit - len(
                    reef.rpc_request("author_pendingExtrinsics", [])["result"]
                )
                continue

            # retry extrinsic until successful
            try:
                result = reef.rpc_request(
                    "author_submitExtrinsic", [str(extrinsic.data)]
                )
            except Exception as e:
                logger.exception(e)
                logger.info(extrinsic)
                if e.args[0]["code"] != 1010:
                    logger.info("lets retry!")
                    sleep(1)
                    continue

            # save result, decrement pool counter and break
            results[nonce] = result
            pool_space -= 1
            break

    return results


def construct_evm_extrinsics(
    reef: ReefInterface, origin: Keypair, target: str, tx_count: int
) -> dict:
    erc20_contract_address = deploy_erc20_and_return_address(reef, origin)
    call_input = f"0xa9059cbb000000000000000000000000{target[2:]}0000000000000000000000000000000000000000000000000000000000000001"
    call = reef.compose_call(
        call_module="EVM",
        call_function="call",
        call_params={
            "target": erc20_contract_address,
            "input": call_input,
            "value": 0,
            "gas_limit": 500000,
            "storage_limit": 5000,
        },
    )
    initial_nonce = reef.get_account_nonce(origin.ss58_address)
    extrinsics = {
        nonce: reef.create_signed_extrinsic(call=call, keypair=origin, nonce=nonce)
        for nonce in range(initial_nonce, initial_nonce + tx_count)
    }
    return extrinsics


def deploy_erc20_and_return_address(reef: ReefInterface, origin: Keypair):
    call = reef.compose_call(
        call_module="EVM",
        call_function="create",
        call_params={
            "init": ERC2_DEPLOYMENT_BYTECODE,
            "value": 0,
            "gas_limit": 5000000,
            "storage_limit": 50000,
        },
    )
    extrinsic = reef.create_signed_extrinsic(call, origin)
    receipt = reef.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    created_event = [
        event.value
        for event in receipt.triggered_events
        if event.value["module_id"] == "EVM" and event.value["event_id"] == "Created"
    ]
    return created_event[0]["params"][0]["value"]


def construct_native_extrinsics(
    reef: ReefInterface, origin: Keypair, target: str, tx_count: int
) -> dict:
    # construct extrinsics
    initial_nonce = reef.get_account_nonce(origin.ss58_address)
    call = reef.compose_call(
        call_module="Balances",
        call_function="transfer",
        call_params={"dest": target, "value": 0.0001 * REEF_DECIMALS},
    )
    extrinsics = {
        nonce: reef.create_signed_extrinsic(call=call, keypair=origin, nonce=nonce)
        for nonce in range(initial_nonce, initial_nonce + tx_count)
    }
    return extrinsics


if __name__ == "__main__":
    cli()
