import logging

import pandas as pd
from deepdiff import DeepDiff
from docopt import docopt
from reefinterface import ReefInterface
from reefinterface.base import QueryMapResult
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Chain storage util")

PARSER = """
Chain storage util.

Usage:
  storage.py compare <block_a> <block_b> [--rpc=<rpc>]
  storage.py to_postgres [--rpc=<rpc> --db=<db> --block=<block>]

Options:
  -h --help     Show this screen.
  --rpc=<rpc>   rpc connection string [default: ws://localhost:9944]
  --db=<db>     postgres db connection string [default: postgresql://test:test@localhost:5432/storage]
  --block=<block>       block number [default: ]
"""


def cli():
    args = docopt(PARSER)
    logger.info(f"args: {args}")

    reef = ReefInterface(args["--rpc"])
    if args["compare"]:
        compare_storage(reef, int(args["<block_a>"]), int(args["<block_b>"]))
    elif args["to_postgres"]:
        to_postgres(
            create_engine(args["--db"]),
            reef,
            args["--block>"] if args["--block"] else None,
        )


def dump_storage(reef: ReefInterface, block_hash: str = None, block_number: int = None):
    block_hash = reef.get_block_hash(block_number) if block_number else block_hash
    storage_metadata = reef.get_metadata_storage_functions(block_hash)
    key = (
        lambda storage_item: f"{storage_item['module_id']}.{storage_item['storage_name']}"
    )
    data = {
        key(storage_item): process_storage_item(block_hash, reef, storage_item)
        for storage_item in storage_metadata
    }
    return data


def process_storage_item(block_hash, reef, storage_item):
    try:
        if storage_item["type_class"] == "MapType":
            return normalise_map(
                reef.query_map(
                    storage_item["module_id"],
                    storage_item["storage_name"],
                    block_hash=block_hash,
                )
            )
        elif storage_item["type_class"] == "PlainType":
            return reef.query(
                storage_item["module_id"],
                storage_item["storage_name"],
                block_hash=block_hash,
            ).value
    except Exception:
        logger.warning(
            f"Unable to fetch storage item: {storage_item['module_id']}.{storage_item['storage_name']} for block hash: {block_hash} - TypeClass: {storage_item['type_class']}"
        )


def normalise_map(raw_map_result: QueryMapResult) -> pd.DataFrame:
    data = [
        {"id": x[0].value if x[0] else None, "result": x[1].value if x[1] else None}
        for x in raw_map_result
    ]
    return pd.json_normalize(data) if data else None


def write_storage(storage: dict, engine: Engine):
    for key, value in storage.items():
        if type(value) == pd.DataFrame:
            try:
                value.to_sql(key, engine)
            except Exception:
                logger.exception(f"Failed to write to db: {key}")


def diff_storage(a: dict, b: dict):
    logger.info("Storage items diff:")
    logger.info(f"{DeepDiff(a.keys(), b.keys(), ignore_order=True)}\n")
    return {
        storage_item: diff_storage_item(a, b, storage_item)
        for storage_item in set(a.keys()).intersection(set(b.keys()))
    }


def diff_storage_item(a, b, storage_item):
    if not isinstance(a[storage_item], type(b[storage_item])):
        logger.warning(f"Data types do not match for storage item {storage_item}\n")
        return None

    if isinstance(a[storage_item], pd.DataFrame):
        diff = a[storage_item].compare(b[storage_item])
    else:
        diff = DeepDiff(a[storage_item], b[storage_item], ignore_order=True)

    if (isinstance(diff, pd.DataFrame) and not diff.empty) or (
        isinstance(diff, dict) and diff
    ):
        logger.info(f"{storage_item} diff:\n{diff}\n")
        return diff

    return None


def compare_storage(reef: ReefInterface, block_a: int, block_b: int):
    storage_a = dump_storage(reef, block_number=block_a)
    storage_b = dump_storage(reef, block_number=block_b)
    return diff_storage(storage_a, storage_b)


def to_postgres(db: Engine, reef: ReefInterface, block_number: int = None):
    storage = dump_storage(reef, block_number=block_number)
    write_storage(storage, db)


if __name__ == "__main__":
    cli()
