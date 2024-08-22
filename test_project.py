from project import validate_money, format_money, get_history


def test_validate_money():
    assert validate_money("123")
    assert validate_money("1,23") == False
    assert validate_money("123456")
    assert validate_money("123,456")
    assert validate_money("123.456") == False
    assert validate_money("123,456.") == False
    assert validate_money("123,456.0")
    assert validate_money("123,456.00")


def test_format_money():
    assert format_money(123) == "$ 123.00"
    assert format_money(123456.1) == "$ 123,456.10"


def test_get_history():
    assert get_history(history_file="test_history.csv", filter={}) == """\
╒══════════════╤══════════╤════════════╤════════════════╕
│ Amount       │ Type     │ Category   │ Timestamp      │
╞══════════════╪══════════╪════════════╪════════════════╡
│ $ 50,000.00  │ Withdraw │ -          │ 24-08-20 19:18 │
│ $ 100,000.00 │ Withdraw │ -          │ 24-08-20 19:10 │
│ $ 200,000.00 │ Deposit  │ -          │ 24-08-20 19:10 │
│ $ 500,000.00 │ Income   │ Job        │ 24-08-20 19:10 │
╘══════════════╧══════════╧════════════╧════════════════╛"""

    assert get_history(history_file="test_history.csv", filter={"Withdraw"}) == """\
╒══════════════╤══════════╤════════════╤════════════════╕
│ Amount       │ Type     │ Category   │ Timestamp      │
╞══════════════╪══════════╪════════════╪════════════════╡
│ $ 50,000.00  │ Withdraw │ -          │ 24-08-20 19:18 │
│ $ 100,000.00 │ Withdraw │ -          │ 24-08-20 19:10 │
╘══════════════╧══════════╧════════════╧════════════════╛"""

    assert get_history(history_file="test_history.csv", filter={"Income"}) == """\
╒══════════════╤════════╤════════════╤════════════════╕
│ Amount       │ Type   │ Category   │ Timestamp      │
╞══════════════╪════════╪════════════╪════════════════╡
│ $ 500,000.00 │ Income │ Job        │ 24-08-20 19:10 │
╘══════════════╧════════╧════════════╧════════════════╛"""

    assert get_history(history_file="test_history.csv", filter={"Income", "Withdraw"}) == """\
╒══════════════╤══════════╤════════════╤════════════════╕
│ Amount       │ Type     │ Category   │ Timestamp      │
╞══════════════╪══════════╪════════════╪════════════════╡
│ $ 50,000.00  │ Withdraw │ -          │ 24-08-20 19:18 │
│ $ 100,000.00 │ Withdraw │ -          │ 24-08-20 19:10 │
│ $ 500,000.00 │ Income   │ Job        │ 24-08-20 19:10 │
╘══════════════╧══════════╧════════════╧════════════════╛"""