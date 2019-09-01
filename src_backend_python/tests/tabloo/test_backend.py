import pytest

import datetime

import pandas as pd
import numpy as np

from tabloo.backend import Backend, to_json, convert_column


@pytest.fixture
def df_simple():
    df = pd.DataFrame({
        "A": [1, 3, 2],
        "B": [6, 5, 4],
    })
    df = df[sorted(df.columns)]
    return df


@pytest.fixture
def df_with_custom_column_types(df_simple):
    df = pd.DataFrame({
        "A": [1, None, 3],
        "B": [np.array([1, 2, 3]), np.array([2, 3, 4]), np.array([3, 4, 5])],
        "C": [pd.Series([1, 2, 3]), pd.Series([2, 3, 4]), pd.Series([3, 4, 5])],
        "D": [df_simple, df_simple, df_simple],
        "E": [{"a": 1}, {"b": 2}, {"c": 3}],
        "F": [None, None, None],
        "G": [
            datetime.datetime.utcfromtimestamp(0),
            datetime.datetime.utcfromtimestamp(1e9),
            datetime.datetime.utcfromtimestamp(1e10),
        ]
    })
    df = df[sorted(df.columns)]
    return df


def test_backend__basic(df_simple):
    backend = Backend(df_simple)

    assert backend.get_columns() == ["A", "B"]

    assert backend.get_data(
        filter=None,
        sort_column=None,
        sort_kind=0,
        page=None,
        pagination_size=None,
    ) == [
        {'columnName': 'A', 'sortKind': 0, 'values': [1, 3, 2]},
        {'columnName': 'B', 'sortKind': 0, 'values': [6, 5, 4]},
    ]

    assert backend.get_data(
        filter=None,
        sort_column="A",
        sort_kind=1,
        page=None,
        pagination_size=None,
    ) == [
        {'columnName': 'A', 'sortKind': 1, 'values': [1, 2, 3]},
        {'columnName': 'B', 'sortKind': 0, 'values': [6, 4, 5]},
    ]

    assert backend.get_data(
        filter=None,
        sort_column="A",
        sort_kind=-1,
        page=None,
        pagination_size=None,
    ) == [
        {'columnName': 'A', 'sortKind': -1, 'values': [3, 2, 1]},
        {'columnName': 'B', 'sortKind': 0, 'values': [5, 4, 6]},
    ]


def test_backend__json_convertability(df_with_custom_column_types):
    backend = Backend(df_with_custom_column_types)

    data = backend.get_data(
        filter=None,
        sort_column=None,
        sort_kind=0,
        page=None,
        pagination_size=None,
    )

    data_json_string = to_json(data)

    assert data_json_string == '[' \
        '{"columnName": "A", "sortKind": 0, "values": [1.0, null, 3.0]}, ' \
        '{"columnName": "B", "sortKind": 0, "values": [[1, 2, 3], [2, 3, 4], [3, 4, 5]]}, ' \
        '{"columnName": "C", "sortKind": 0, "values": [{"0": 1, "1": 2, "2": 3}, {"0": 2, "1": 3, "2": 4}, {"0": 3, "1": 4, "2": 5}]}, ' \
        '{"columnName": "D", "sortKind": 0, "values": [{"A": [1, 3, 2], "B": [6, 5, 4]}, {"A": [1, 3, 2], "B": [6, 5, 4]}, {"A": [1, 3, 2], "B": [6, 5, 4]}]}, ' \
        '{"columnName": "E", "sortKind": 0, "values": [{"a": 1}, {"b": 2}, {"c": 3}]}, ' \
        '{"columnName": "F", "sortKind": 0, "values": [null, null, null]}, ' \
        '{"columnName": "G", "sortKind": 0, "values": ["1970-01-01 00:00:00", "2001-09-09 01:46:40", "2286-11-20 17:46:40"]}' \
        ']'

    # Maybe change to deserialized check based on extracting individual values
    # def get(col):
    #     return [row["values"] for row in data_json if row["columnName"] == col][0]


def test_convert_column():
    c = pd.Series([1, 2, 3])
    assert convert_column(c) == [1, 2, 3]

    c = pd.Series([1, 2, 3], index=[30, 20, 10])
    assert convert_column(c) == [1, 2, 3]

    c = pd.Series([None, "1", 2])
    assert convert_column(c) == [None, "1", 2]

    c = pd.Series([1, None, 2])
    assert convert_column(c) == [1, None, 2]

    c = pd.Series([1, np.nan, 2])
    assert convert_column(c) == [1, None, 2]

    c = pd.Series([1, np.inf, 2])
    assert convert_column(c) == [1, "inf", 2]

    c = pd.Series([1, -np.inf, 2])
    assert convert_column(c) == [1, "-inf", 2]
