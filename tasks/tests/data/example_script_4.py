import warnings


def check_age_raising_exception(age):
    if age < 0:
        # Raising an exception with a direct simple string message
        raise ValueError("Age cannot be negative.")
    elif age > 120:
        # Raising an exception with a formatted string message using an f-string
        raise ResourceWarning(f"Age {age} is unusually high for a human.")
    else:
        print(f"Age {age} is valid.")


def check_age_sending_warnings(age):
    if age < 0:
        # Raising an exception with a direct simple string message
        warnings.warn("Age cannot be negative.")
    elif age > 120:
        # Raising an exception with a formatted string message using an f-string
        warnings.warn(f"Age {age} is unusually high for a human.")
    else:
        print(f"Age {age} is valid.")