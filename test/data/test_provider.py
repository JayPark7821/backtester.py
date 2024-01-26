from data.provider import DataProvider
import pytest

async def test_get_date():
    provider = DataProvider()
    result = await provider.get_data("2020-01-01", "2050-01-02")
    print(result)
