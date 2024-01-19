from data.provider import DataProvider
def test_get_date():
    provider = DataProvider()
    provider.get_data("2021-01-01", "2021-01-02")
