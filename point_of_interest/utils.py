from uuid import UUID


def validate_uuid(uuid_string: str) -> bool:
    """Function responsible to check the uuid input
    Args:
        uuid_string (str): Receives the input string
    Returns:
        bool: Return a boolean with the validation result
    """
    result = True
    try:
        UUID(uuid_string, version=4)
    except ValueError:
        result = False
    return result
