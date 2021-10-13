import logging

import pandas as pd
from reefinterface import Keypair, ReefInterface
from reefinterface.base import QueryMapResult

logger = logging.getLogger(__name__)


def get_balance(reef_interface: ReefInterface, keypair: Keypair):
    account = get_account(reef_interface=reef_interface, keypair=keypair)
    return account["data"]["free"] if account else None


def get_account(reef_interface: ReefInterface, keypair: Keypair):
    return reef_interface.query(
        module="System", storage_function="Account", params=[keypair.public_key]
    ).value


def dump_storage(reef: ReefInterface, block_hash: str = None, block_number: int = None):
    block_hash = reef.get_block_hash(block_number) if block_number else block_hash
    storage_metadata = reef.get_metadata_storage_functions(block_hash)
    data = {}
    for storage_item in storage_metadata:
        try:
            if storage_item["type_class"] == "MapType":
                data[
                    f"{storage_item['module_id']}.{storage_item['storage_name']}"
                ] = normalise_map(
                    reef.query_map(
                        storage_item["module_id"], storage_item["storage_name"]
                    )
                )
            elif storage_item["type_class"] == "PlainType":
                result = reef.query(
                    storage_item["module_id"], storage_item["storage_name"]
                ).value
                try:
                    result = pd.DataFrame(result)
                except Exception:
                    pass
                data[
                    f"{storage_item['module_id']}.{storage_item['storage_name']}"
                ] = result
        except Exception:
            logger.error(
                f"Unable to fetch storage item: {storage_item['module_id']}.{storage_item['storage_name']} - TypeClass: {storage_item['type_class']}"
            )
    return data


class QueryDataException(Exception):
    pass


def normalise_map(raw_map_result: QueryMapResult) -> pd.DataFrame:
    data = [{"id": x[0].value, "result": x[1].value} for x in raw_map_result]
    return pd.json_normalize(data)
