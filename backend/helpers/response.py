def success_response(data=None, message="Success"):
    """
    Standardizes successful API responses.
    """
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(code: str, message: str):
    """
    Standardizes error API responses.
    """
    return {
        "success": False,
        "message": message,
        "error_code": code  # Keeping code for internal mapping, but message is top-level
    }
