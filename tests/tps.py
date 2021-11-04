import logging
from time import sleep

from docopt import docopt
from reefinterface import Keypair, ReefInterface

from .config import REEF_DECIMALS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TPS test util")

PARSER = """
TPS test util.

Usage:
  tps.py execute [--rpc=<rpc> --seed=<seed> --target=<target> --tx-count=<tx> --pool-limit=<pool-limit>]

Options:
  -h --help                   Show this screen.
  --rpc=<rpc>                 rpc connection string [default: ws://localhost:9944]
  --seed=<seed>               seed phrase for origin account [default: //Alice]
  --target=<target>           ss58 address of target account - default == //Bob [default: 5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty]
  --tx-count=<tx>             number of transactions to submit [default: 10000]
  --pool-limit=<pool-limit>   pool limit [default: 8000]
"""


def cli():
    args = docopt(PARSER)
    logger.info(f"args: {args}")

    if args["execute"]:
        submit_extrinsics(
            args["--rpc"],
            args["--seed"],
            args["--target"],
            int(args["--tx-count"]),
            int(args["--pool-limit"]),
        )
    else:
        raise Exception("Command not supported!")


def submit_extrinsics(rpc: str, seed: str, target: str, tx_count: int, pool_limit: int):
    # create reef client and keypair
    reef = ReefInterface(rpc)
    origin = Keypair.create_from_uri(seed)

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
                    sleep(10)
                    continue

            # save result, decrement pool counter and break
            results[nonce] = result
            pool_space -= 1
            break

    return results


if __name__ == "__main__":
    cli()
