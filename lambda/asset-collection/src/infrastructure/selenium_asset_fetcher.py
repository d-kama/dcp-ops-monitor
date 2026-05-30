from datetime import datetime
from tempfile import mkdtemp
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.common.by import By
from shared.domain.financial_asset import (
    AssetValuation,
    CumulativeContributions,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
)

from src.application import AssetFetchFailed, IAssetFetcher
from src.application.error_artifact_repository import IErrorArtifactRepository
from src.config import AssetFetchConfig
from src.config.settings import get_logger
from src.infrastructure.yen_parser import parse_yen_amount

logger = get_logger()


class SeleniumAssetFetchFailed(AssetFetchFailed):
    pass


class SeleniumAssetFetcher(IAssetFetcher):
    """Selenium WebDriverを提供するクラス"""

    def __init__(
        self,
        config: AssetFetchConfig,
        error_repo: IErrorArtifactRepository,
        chrome_binary_location: str = "/opt/chrome/chrome",
        chrome_driver_path: str = "/opt/chromedriver",
    ) -> None:
        self.chrome_binary_location = chrome_binary_location
        self.chrome_driver_path = chrome_driver_path
        self.user_agent = config.user_agent
        self.driver = self._get_driver()
        self.user_id = config.login_user_id
        self.password = config.login_password
        self.birthdate = config.login_birthdate
        self.start_url = config.start_url
        self._error_repo = error_repo

    def _get_driver(self) -> webdriver.Chrome:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--window-size=1280x1696")
        chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
        chrome_options.add_argument(f"--data-path={mkdtemp()}")
        chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--v=99")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument(f"--user-agent={self.user_agent}")

        # ref: https://github.com/umihico/docker-selenium-lambda/blob/main/main.py
        chrome_options.binary_location = self.chrome_binary_location
        service = webdriver.ChromeService(self.chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # スクレイピング全体通して暗黙的に待機する時間を10秒に設定
        driver.implicitly_wait(10)

        return driver

    def fetch_asset_valuation(self) -> FinancialAssetHistory:
        """資産評価情報を取得する

        Returns:
            FinancialAssetHistory: 商品別の資産評価情報
        """
        logger.info("資産評価情報の取得開始")
        self.driver.get(self.start_url)

        self._login()
        self._navigate_to_asset_page()
        daily_assets = self._extract_asset_valuation()
        self._logout()
        self.driver.quit()
        logger.info("資産評価情報の取得完了")
        return daily_assets

    def _login(self) -> None:
        try:
            logger.info("ログイン処理開始")
            input_user_id = self.driver.find_element(By.NAME, "userId")
            input_password = self.driver.find_element(By.NAME, "password")
            input_birthdate = self.driver.find_element(By.NAME, "birthDate")
            input_user_id.send_keys(self.user_id.get_secret_value())
            input_password.send_keys(self.password.get_secret_value())
            input_birthdate.send_keys(self.birthdate.get_secret_value())

            btn_login = self.driver.find_element(By.ID, "btnLogin")
            btn_login.submit()

            # ログアウトボタンがなければログイン失敗とする
            self.driver.find_element(By.LINK_TEXT, "ログアウト")
            logger.info("ログイン処理完了")

        except Exception as e:
            screenshot_path = "/tmp/error_login.png"
            self.driver.save_screenshot(screenshot_path)
            self.driver.quit()
            error_extra = {}
            try:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                key = f"errors/{timestamp}.png"
                self._error_repo.store(key=key, file_path=screenshot_path)
                error_extra = {"error_screenshot_key": key}
            except Exception as artifact_error:
                logger.warning("エラーアーティファクトの保存に失敗しました。", extra={"error": str(artifact_error)})
            logger.error("ログイン処理に失敗しました。", extra=error_extra)
            raise SeleniumAssetFetchFailed("ログイン処理に失敗しました") from e

    def _navigate_to_asset_page(self) -> None:
        """資産評価額照会ページへ遷移する"""
        try:
            logger.info("資産評価額照会ページへの遷移開始")
            link_asset_valuation = self.driver.find_element(By.ID, "mainMenu01")
            link_asset_valuation.click()

            # 資産評価額照会ページの読み込み完了を確認
            self.driver.find_element(By.CLASS_NAME, "total")
            logger.info("資産評価額照会ページへの遷移完了")
        except Exception as e:
            screenshot_path = "/tmp/error_asset_valuation.png"
            self.driver.save_screenshot(screenshot_path)
            self._logout()
            self.driver.quit()
            error_extra = {}
            try:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                key = f"errors/{timestamp}.png"
                self._error_repo.store(key=key, file_path=screenshot_path)
                error_extra = {"error_screenshot_key": key}
            except Exception as artifact_error:
                logger.warning("エラーアーティファクトの保存に失敗しました。", extra={"error": str(artifact_error)})
            logger.error("資産評価額照会ページの取得に失敗しました。", extra=error_extra)
            raise SeleniumAssetFetchFailed("資産評価額照会ページの取得に失敗しました") from e

    def _extract_asset_valuation(self) -> FinancialAssetHistory:
        """資産評価額照会ページから商品別の資産情報を抽出する

        Returns:
            FinancialAssetHistory: 商品別の資産評価情報
        """
        try:
            logger.info("資産情報の抽出開始")
            daily_assets = self._extract_product_assets()
            logger.info("資産情報の抽出完了")
            return daily_assets
        except Exception as e:
            html_path = "/tmp/error_extraction.html"
            error_extra = {}
            try:
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                key = f"errors/{timestamp}.html"
                self._error_repo.store(key=key, file_path=html_path)
                error_extra = {"error_html_key": key}
            except Exception as artifact_error:
                logger.warning("エラーアーティファクトの保存に失敗しました。", extra={"error": str(artifact_error)})
            self._logout()
            self.driver.quit()
            logger.error("資産情報の抽出に失敗しました。", extra=error_extra)
            raise SeleniumAssetFetchFailed("資産情報の抽出に失敗しました") from e

    def _extract_product_assets(self) -> FinancialAssetHistory:
        """商品別資産を抽出する

        Returns:
            FinancialAssetHistory: 商品別資産情報
        """
        logger.info("商品別の資産評価額の抽出開始")

        today = datetime.now(ZoneInfo("Asia/Tokyo")).date()
        product_info = self.driver.find_element(By.ID, "prodInfo")
        products = product_info.find_elements(By.CSS_SELECTOR, ".infoDetailUnit_02.pc_mb30")

        daily_assets = FinancialAssetHistory(assets=[])
        for product in products:
            table_body = product.find_element(By.TAG_NAME, "tbody")
            table_rows = table_body.find_elements(By.TAG_NAME, "tr")

            product_name = product.find_element(By.CLASS_NAME, "infoHdWrap00").text.strip()
            asset = FinancialAsset(
                product_name=product_name,
                base_date=today,
                cumulative_contributions=CumulativeContributions(
                    value=parse_yen_amount(table_rows[2].find_elements(By.TAG_NAME, "td")[-1].text)
                ),
                gains_or_losses=GainsOrLosses(
                    value=parse_yen_amount(table_rows[5].find_elements(By.TAG_NAME, "td")[-1].text)
                ),
                asset_valuation=AssetValuation(
                    value=parse_yen_amount(table_rows[2].find_elements(By.TAG_NAME, "td")[2].text)
                ),
            )
            daily_assets = daily_assets.add(asset)
            logger.debug(
                f"商品別資産評価額情報: {product_name}.",
                extra=asset.model_dump(),
            )

        logger.info(
            "商品別の資産評価額の抽出完了",
            extra={
                "product_count": len(daily_assets.assets),
                "product_names": [a.product_name for a in daily_assets.assets],
            },
        )
        return daily_assets

    def _logout(self) -> None:
        try:
            logger.info("ログアウト処理開始")
            link_logout = self.driver.find_element(By.LINK_TEXT, "ログアウト")
            link_logout.click()
            logger.info("ログアウト処理完了")
        except Exception:
            # ログアウト失敗はログのみ出力して無視
            logger.warning("ログアウト処理中に問題が発生しました。")
