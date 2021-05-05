from datetime import timedelta

import pandas as pd
import pytest
import streamlit as st
from streamlit_prophet.lib.dataprep.split import (
    get_cv_cutoffs,
    raise_error_cv_dates,
    raise_error_train_val_dates,
)
from streamlit_prophet.lib.utils.load import load_config
from tests.samples.dict import make_dates_test

config, _ = load_config("config_streamlit.toml", "config_readme.toml")


@pytest.mark.parametrize(
    "train_start, train_end, val_start, val_end, freq",
    [
        ("2015-01-01", "2019-12-31", "2020-01-01", "2023-01-01", "Y"),
        ("2015-01-01", "2019-12-31", "2020-01-01", "2020-01-15", "M"),
        ("2020-01-01", "2020-01-15", "2021-01-01", "2021-01-15", "D"),
        ("2020-01-01", "2020-12-31", "2021-01-01", "2021-01-01", "D"),
        ("2020-01-01", "2020-12-31", "2021-01-01", "2021-01-05", "W"),
        ("2020-01-01 00:00:00", "2020-01-01 12:00:00", "2021-01-01", "2021-01-05", "H"),
    ],
)
def test_raise_error_train_val_dates(train_start, train_end, val_start, val_end, freq):
    train = pd.date_range(start=train_start, end=train_end, freq=freq)
    val = pd.date_range(start=val_start, end=val_end, freq=freq)
    with pytest.raises(st.script_runner.StopException):
        raise_error_train_val_dates(val, train, config=config)


@pytest.mark.parametrize(
    "dates",
    [
        (
            make_dates_test(
                train_start="2020-01-01",
                train_end="2021-01-01",
                n_folds=12,
                folds_horizon=30,
                freq="D",
            )
        ),
        (
            make_dates_test(
                train_start="2020-01-01",
                train_end="2021-01-01",
                n_folds=5,
                folds_horizon=3,
                freq="4D",
            )
        ),
        (
            make_dates_test(
                train_start="2020-01-01",
                train_end="2021-01-01",
                n_folds=50,
                folds_horizon=1,
                freq="W",
            )
        ),
        (
            make_dates_test(
                train_start="2020-01-01",
                train_end="2020-01-02",
                n_folds=7,
                folds_horizon=3,
                freq="H",
            )
        ),
    ],
)
def test_raise_error_cv_dates(dates):
    with pytest.raises(st.script_runner.StopException):
        raise_error_cv_dates(dates, resampling={"freq": dates["freq"]}, config=config)


@pytest.mark.parametrize(
    "dates",
    [
        (
            make_dates_test(
                train_start="1900-01-01",
                train_end="2021-01-01",
                n_folds=5,
                folds_horizon=3,
                freq="Y",
            )
        ),
        (
            make_dates_test(
                train_start="1950-01-01",
                train_end="2021-01-01",
                n_folds=5,
                folds_horizon=4,
                freq="Q",
            )
        ),
        (
            make_dates_test(
                train_start="1970-01-01",
                train_end="2021-01-01",
                n_folds=5,
                folds_horizon=6,
                freq="M",
            )
        ),
        (make_dates_test(freq="W")),
        (make_dates_test(freq="D")),
        (
            make_dates_test(
                train_start="2021-01-01",
                train_end="2021-01-30",
                n_folds=5,
                folds_horizon=12,
                freq="H",
            )
        ),
    ],
)
def test_get_cv_cutoffs(dates):
    output = sorted(get_cv_cutoffs(dates, freq=dates["freq"][-1]))
    assert len(output) == dates["n_folds"]
    assert max(output) + timedelta(days=(output[-1] - output[-2]).days) <= dates["train_end_date"]
