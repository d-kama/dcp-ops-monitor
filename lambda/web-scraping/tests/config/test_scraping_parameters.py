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

        assert params.login_user_id == "user-id"
        assert params.login_password == "password"
        assert params.login_birthdate == "19800101"
        assert params.start_url == "https://example.com/login"
        assert params.user_agent == "Mozilla/5.0 test-agent"
