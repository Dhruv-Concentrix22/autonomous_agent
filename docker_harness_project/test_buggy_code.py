import pytest
from buggy_code import calculate_totals

def test_empty_items():
    assert calculate_totals([]) == 0.0

def test_single_item_no_discount():
    # subtotal = 100.0, tax 5% -> 105.0
    assert calculate_totals([100.0], tax_rate=0.05, discount_percent=0.0) == 105.0

def test_with_discount():
    # subtotal = 200.0, 10% discount -> 180.0 subtotal, 5% tax -> 189.0
    # BUGGY CODE DOES: 200.0 - 10.0 = 190.0 * 1.05 = 199.5 (FAILS)
    assert calculate_totals([200.0], tax_rate=0.05, discount_percent=10.0) == 189.0

def test_multiple_items_with_discount():
    # subtotal = 150.0 + 50.0 = 200.0, 20% discount -> 160.0 subtotal, 10% tax -> 176.0
    # BUGGY CODE DOES: 200.0 - 20.0 = 180.0 * 1.10 = 198.0 (FAILS)
    assert calculate_totals([150.0, 50.0], tax_rate=0.10, discount_percent=20.0) == 176.0
