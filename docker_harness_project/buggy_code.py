def calculate_totals(items: list[float], tax_rate: float = 0.05, discount_percent: float = 0.0) -> float:
    """
    Calculates total price for a list of item prices.
    Applies discount percentage to subtotal before tax, then adds tax.

    BUG: Subtracts discount as a raw flat amount instead of a percentage!
    """
    if not items:
        return 0.0
    
    subtotal = sum(items)
    
    # BUG HERE: subtracting raw discount_percent instead of calculating percentage (subtotal * discount_percent / 100)
    discounted_subtotal = subtotal - discount_percent
    
    total = discounted_subtotal * (1 + tax_rate)
    return round(total, 2)
