import logging
import json

import asyncio
from websockets import connect
from docopt import docopt
from reefinterface import ReefInterface, Keypair

from tests.config import REEF_DECIMALS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TPS test util")

PARSER = """
TPS test util.

Usage:
  tps.py execute [--rpc=<rpc> --seed=<seed> --target=<target>]

Options:
  -h --help          Show this screen.
  --rpc=<rpc>        rpc connection string [default: ws://localhost:9944]
  --seed=<seed>      seed phrase for origin account [default: //Alice]
  --target=<target>  ss58 address of target account - default == //Bob [default: 5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty]
"""


def cli():
    args = docopt(PARSER)
    logger.info(f"args: {args}")

    if args["execute"]:
        tps_test(args["--rpc"], args["--seed"], args["--target"])
    else:
        raise Exception("Command not supported!")


def tps_test(rpc: str, seed: str, target: str):
    reef = ReefInterface(rpc)
    origin = Keypair.create_from_uri(seed)
    initial_nonce = reef.get_account_nonce(origin.ss58_address)

    call = reef.compose_call(
        call_module="Balances",
        call_function="transfer",
        call_params={"dest": target, "value": 0.0001 * REEF_DECIMALS},
    )
    extrinsics = [reef.create_signed_extrinsic(call=call, keypair=origin, nonce=nonce) for nonce in range(initial_nonce, initial_nonce+1000)]
    payloads = [json.dumps({
            "jsonrpc": "2.0",
            "method": "author_submitExtrinsic",
            "params": [str(extrinsic.data)],
            "id": i
        }) for i, extrinsic in enumerate(extrinsics)]
    print(len(payloads))
    print(payloads[:5])
    asyncio.run(submit_extrinsics(rpc, payloads))
    return extrinsics, payloads


async def submit_extrinsics(rpc: str, payloads: list):
    async with connect(rpc) as websocket:
        coroutines = [websocket.send(payload) for payload in payloads]
        for payload in payloads:
            await websocket.send(payload)
        return await asyncio.gather(*coroutines)


if __name__ == "__main__":
    cli()
