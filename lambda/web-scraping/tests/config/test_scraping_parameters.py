from src.config import ScrapingParameters


class TestScrapingParameters:
    def test_create__valid_fields(self):
        """全フィールド指定でインスタンス化できる"""
        params = ScrapingParameters(
            login_user_id="user-id",
            login_password="password",
            login_birthdate="19800101",
            start_url="https://example.com/login",
            user_agent="Mozilla/5.0 test-agent",
        )

        assert params.login_user_id.get_secret_value() == "user-id"
        assert params.login_password.get_secret_value() == "password"
        assert params.login_birthdate.get_secret_value() == "19800101"
        assert params.start_url == "https://example.com/login"
        assert params.user_agent == "Mozilla/5.0 test-agent"

    def test_repr__masks_sensitive_fields(self):
        """repr() の出力に認証情報の平文が含まれない"""
        params = ScrapingParameters(
            login_user_id="secret-user-123",
            login_password="secret-pass-456",
            login_birthdate="19800101",
            start_url="https://example.com/login",
            user_agent="Mozilla/5.0 test-agent",
        )

        result = repr(params)

        assert "secret-user-123" not in result
        assert "secret-pass-456" not in result
        assert "19800101" not in result
