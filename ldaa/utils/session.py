import secrets

def generate_session_id() -> str:
    """
    Generate a random session ID as an 8-digit hexadecimal string.
    Returns:
        str: A random 8-character hex string (e.g., 'a1b2c3d4').
    """
    return secrets.token_hex(4) 