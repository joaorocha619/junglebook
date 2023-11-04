from datetime import date, datetime

from junglebook.utils import convert_date_to_datetime, dict_merge


class TestUtils:

    def test_convert_date_to_datetime(self):
        dates_list = [date(2021, 3, 1), date(2020, 5, 17)]

        actual_result = convert_date_to_datetime(dates_list)
        expected_result = [datetime(2021, 3, 1), datetime(2020, 5, 17)]

        assert actual_result == expected_result

    def test_dict_merge(self):
        dct_a = {'a': 0}
        dct_b = {'b': 1}

        dict_merge(dct_a, dct_b)

        expected_result = {'a': 0,
                           'b': 1}
        actual_result = dct_a

        assert actual_result == expected_result
