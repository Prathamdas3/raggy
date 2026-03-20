"""Common utility functions.

Provides password hashing and verification using bcrypt.
"""

import bcrypt


class HandlePassword:
    """Password hashing and verification utility.

    Uses bcrypt for secure password hashing with configurable salt rounds.
    """

    def get_hashed_password(self, password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password to hash.

        Returns:
            Bcrypt hashed password string.
        """
        password_bytes = password.encode("utf-8")

        # Truncate to 72 bytes if necessary (bcrypt limit)
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Return as string
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash.

        Args:
            plain_password: Plain text password to verify.
            hashed_password: Bcrypt hash to verify against.

        Returns:
            True if password matches, False otherwise.
        """
        try:
            password_bytes = plain_password.encode("utf-8")

            # Truncate to 72 bytes if necessary (bcrypt limit)
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]

            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False
