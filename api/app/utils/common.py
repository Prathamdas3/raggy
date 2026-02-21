import bcrypt


class HandlePassword:
    """Password hashing and verification"""

    def get_hashed_password(self, password: str) -> str:
        # Bcrypt requires bytes
        password_bytes = password.encode("utf-8")

        # Truncate to 72 bytes if necessary
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Return as string
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            password_bytes = plain_password.encode("utf-8")

            # Truncate to 72 bytes if necessary
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]

            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False
