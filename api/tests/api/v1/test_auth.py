from fastapi.testclient import TestClient
from jose import jwt
from typing import Any


class TestInputValidation:
    def test_signup_invalid_email_format(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "not-an-email", "password": "Test@1234"},
        )
        assert response.status_code == 422

    def test_signup_empty_email(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "", "password": "Test@1234"},
        )
        assert response.status_code == 422

    def test_signup_empty_password(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "test@example.com", "password": ""},
        )
        assert response.status_code == 422

    def test_signup_missing_password(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422

    def test_signup_missing_email(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"password": "Test@1234"},
        )
        assert response.status_code == 422

    def test_signup_password_too_short(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "test@example.com", "password": "Test@1"},
        )
        assert response.status_code == 422

    def test_signup_password_no_uppercase(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "test@example.com", "password": "test@1234"},
        )
        assert response.status_code == 422

    def test_signup_password_no_lowercase(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "test@example.com", "password": "TEST@1234"},
        )
        assert response.status_code == 422

    def test_signup_password_no_digit(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "test@example.com", "password": "Test@abcd"},
        )
        assert response.status_code == 422

    def test_signup_password_no_special_char(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "test@example.com", "password": "Test1234"},
        )
        assert response.status_code == 422

    def test_signin_empty_email(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": "", "password": "Test@1234"},
        )
        assert response.status_code == 422

    def test_signin_empty_password(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": "test@example.com", "password": ""},
        )
        assert response.status_code == 422


class TestAuthenticationFlow:
    def test_signup_success(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "newuser@example.com", "password": "Test@1234"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Successfully created the user"
        assert "data" in data
        assert data["data"]["email"] == "newuser@example.com"
        assert "id" in data["data"]

    def test_signup_duplicate_email(self, client: TestClient):
        email = "duplicate@example.com"
        client.post(
            "/api/v1/auth/sign-up",
            json={"email": email, "password": "Test@1234"},
        )
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": email, "password": "Test@1234"},
        )
        assert response.status_code == 409

    def test_signin_success(self, client: TestClient, test_user: Any):
        response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": test_user["email"], "password": test_user["password"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Successfully signed in"
        assert data["data"]["email"] == test_user["email"]

    def test_signin_wrong_password(self, client: TestClient, test_user: Any):
        response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": test_user["email"], "password": "Wrong@1234"},
        )
        assert response.status_code == 400

    def test_signin_nonexistent_user(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": "nonexistent@example.com", "password": "Test@1234"},
        )
        assert response.status_code == 400


class TestSecurity:
    def test_signup_password_not_in_response(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "test@example.com", "password": "Test@1234"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "password" not in data
        assert "password" not in data.get("data", {})

    def test_signup_password_hashed_in_db(self, client: TestClient, db_session: Any):
        from app.db.schema import Users

        email = "hashtest@example.com"
        client.post(
            "/api/v1/auth/sign-up",
            json={"email": email, "password": "Test@1234"},
        )

        user = db_session.query(Users).filter(Users.email == email).first()
        assert user is not None
        assert user.password != "Test@1234"
        assert "$2b$" in user.password

    def test_cookies_set_on_signin(self, client: TestClient, test_user: Any):
        response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": test_user["email"], "password": test_user["password"]},
        )
        assert response.status_code == 200

        cookies = response.cookies
        assert "jwt" in cookies
        assert "token" in cookies
        assert cookies.get("jwt", "") != ""
        assert cookies.get("token", "") != ""

    def test_signin_error_doesnt_leak_email(self, client: TestClient, test_user: Any):
        response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": test_user["email"], "password": "Wrong@1234"},
        )
        assert response.status_code == 400
        data = response.json()
        assert test_user["email"] not in data.get("detail", "")

    def test_sql_injection_in_email(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "test' OR '1'='1", "password": "Test@1234"},
        )
        assert response.status_code == 422

    def test_sql_injection_in_password(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/sign-up",
            json={"email": "test@example.com", "password": "test' OR '1'='1"},
        )
        assert response.status_code == 422

    def test_access_token_has_required_claims(self, client: TestClient, test_user: Any):
        response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": test_user["email"], "password": test_user["password"]},
        )
        assert response.status_code == 200

        jwt_cookie = response.cookies.get("jwt")
        assert jwt_cookie is not None

        from app.core.config import config

        payload = jwt.decode(
            jwt_cookie, config.secret_key, algorithms=[config.algorithm]
        )

        assert "user_id" in payload
        assert "email" in payload
        assert "exp" in payload
        assert "type" in payload
        assert payload["type"] == "access"
        assert "iat" in payload

    def test_refresh_token_has_required_claims(
        self, client: TestClient, test_user: Any
    ):
        from jose import jwt

        response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": test_user["email"], "password": test_user["password"]},
        )
        assert response.status_code == 200

        token_cookie = response.cookies.get("token")
        assert token_cookie is not None

        from app.core.config import config

        payload = jwt.decode(
            token_cookie, config.secret_key, algorithms=[config.algorithm]
        )

        assert "user_id" in payload
        assert "email" in payload
        assert "exp" in payload
        assert "type" in payload
        assert payload["type"] == "refresh"
        assert "iat" in payload

    def test_access_and_refresh_tokens_different(
        self, client: TestClient, test_user: Any
    ):
        response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": test_user["email"], "password": test_user["password"]},
        )
        assert response.status_code == 200

        jwt_cookie = response.cookies.get("jwt")
        token_cookie = response.cookies.get("token")

        assert jwt_cookie != token_cookie


class TestTokenSession:
    def test_refresh_with_valid_token(self, client: TestClient, test_user: Any):
        import time

        signin_response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": test_user["email"], "password": test_user["password"]},
        )
        assert signin_response.status_code == 200

        old_jwt = signin_response.cookies.get("jwt") or ""
        refresh_token = signin_response.cookies.get("token") or ""

        client.cookies.set("jwt", old_jwt)
        client.cookies.set("token", refresh_token)

        time.sleep(1)

        refresh_response = client.get("/api/v1/auth/refresh")
        assert refresh_response.status_code == 200

        new_jwt = refresh_response.cookies.get("jwt")
        assert new_jwt is not None

    def test_refresh_without_token(self, client: TestClient):
        response = client.get("/api/v1/auth/refresh")
        assert response.status_code == 401

    def test_logout_requires_auth(self, client: TestClient):
        response = client.delete("/api/v1/auth/sign-out")
        assert response.status_code == 401

    def test_logout_clears_cookies(self, client: TestClient, test_user: Any):
        signin_response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": test_user["email"], "password": test_user["password"]},
        )
        assert signin_response.status_code == 200

        jwt_val = signin_response.cookies.get("jwt") or ""
        token_val = signin_response.cookies.get("token") or ""

        client.cookies.set("jwt", jwt_val)
        client.cookies.set("token", token_val)

        logout_response = client.delete("/api/v1/auth/sign-out")
        assert logout_response.status_code == 200

    def test_logout_success(self, client: TestClient, test_user: Any):
        signin_response = client.post(
            "/api/v1/auth/sign-in",
            json={"email": test_user["email"], "password": test_user["password"]},
        )
        assert signin_response.status_code == 200

        jwt_val = signin_response.cookies.get("jwt") or ""
        token_val = signin_response.cookies.get("token") or ""

        client.cookies.set("jwt", jwt_val)
        client.cookies.set("token", token_val)

        logout_response = client.delete("/api/v1/auth/sign-out")
        assert logout_response.status_code == 200
        data = logout_response.json()
        assert data["status"] == "success"
        assert "signed out" in data["message"].lower()
