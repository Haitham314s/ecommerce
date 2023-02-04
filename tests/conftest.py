import pytest
import asyncio
import os
from tortoise import Tortoise, run_async


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    async def _init_db():
        await Tortoise.init(
            db_url='sqlite://:memory:',
            modules={'models': ['models']}
        )
        await Tortoise.generate_schemas()

    run_async(_init_db)


@pytest.fixture(autouse=True)
async def clear_db():
    await Tortoise.close_connections()
    for name, adapter in Tortoise._connections.items():
        adapter.drop_all_tables()
