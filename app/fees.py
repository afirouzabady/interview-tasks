PLATFORM_FEE_RATE = 0.029
PLATFORM_FEE_FIXED = 0.30


def platform_fee(amount):
    """Fee charged by Acme Pay on a capture."""
    return amount * PLATFORM_FEE_RATE + PLATFORM_FEE_FIXED
