# solarmatch-server/utils/helpers.py
import re
import random

def generate_username(full_name, role):
    """Generate a friendly, role-based username."""
    first_name = re.sub(r'[^A-Za-z]', '', full_name.split()[0].capitalize())
    random_digits = random.randint(1000, 9999)

    if role == "customer":
        prefix = "CUS"
    elif role == "installer":
        prefix = "INS"
    elif role == "admin":
        prefix = "ADM"
    else:
        prefix = "USR"

    return f"{prefix}-{first_name}-{random_digits}"