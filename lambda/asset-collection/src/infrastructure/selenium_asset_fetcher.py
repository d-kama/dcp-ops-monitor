from dataclasses import asdict
from datetime import datetime
from tempfile import mkdtemp
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.common.by import By

from src.application import IAssetFetcher
from src.config import AssetFetchConfig, get_logger
from src.domain import AssetValuation, CumulativeContributions, FinancialAsset, FinancialAssetHistory, GainsOrLosses
from src.infrastructure.yen_parser import parse_yen_amount

logger = get_logger()


class SeleniumAssetFetcher(IAssetFetcher):
    """Selenium WebDriver を使った資産情報取得実装

    エラーハンドリング（アーティファクト保存・ログ出力）は Application 層の責務。
    本クラスは Selenium 操作のみを担い、失敗時は生の例外を raise する。
    """

    def __init__(
        self,
        config: AssetFetchConfig,
        chrome_binary_location: str = "/opt/chrome/chrome",
        chrome_driver_path: str = "/opt/chromedriver",
    ) -> None:
        self.chrome_binary_location = chrome_binary_location
        self.chrome_driver_path = chrome_driver_path
        self.user_agent = config.user_agent
        self.driver = self._get_driver()
        self.config = config

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

    def open_start_page(self, url: str) -> None:
        self.driver.get(url)

    def login(self, config: AssetFetchConfig) -> None:
        input_user_id = self.driver.find_element(By.NAME, "userId")
        input_password = self.driver.find_element(By.NAME, "password")
        input_birthdate = self.driver.find_element(By.NAME, "birthDate")
        input_user_id.send_keys(config.login_user_id.get_secret_value())
        input_password.send_keys(config.login_password.get_secret_value())
        input_birthdate.send_keys(config.login_birthdate.get_secret_value())

        btn_login = self.driver.find_element(By.ID, "btnLogin")
        btn_login.submit()

        # ログアウトボタンがなければログイン失敗とする
        self.driver.find_element(By.LINK_TEXT, "ログアウト")

        # TODO: プラン移行完了後に削除する
        self._select_transferring_out_plan()

    def _select_transferring_out_plan(self) -> None:
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table.inputTable tbody tr")
        for row in rows:
            status_cells = row.find_elements(By.CSS_SELECTOR, "td[data-lang='jp']")
            for cell in status_cells:
                if "転出処理中" in cell.text:
                    row.find_element(By.CSS_SELECTOR, "input[type='radio']").click()
                    self.driver.find_element(By.ID, "btnSubmit").click()
                    return
        raise ValueError("転出処理中のプランが見つかりませんでした。")

    def navigate_to_asset_page(self) -> None:
        link_asset_valuation = self.driver.find_element(By.ID, "mainMenu01")
        link_asset_valuation.click()

        # 資産評価額照会ページの読み込み完了を確認
        self.driver.find_element(By.CLASS_NAME, "total")

    def extract(self) -> FinancialAssetHistory:
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
                extra=asdict(asset),
            )

        logger.info(
            "商品別の資産評価額の抽出完了",
            extra={
                "product_count": len(daily_assets.assets),
                "product_names": [a.product_name for a in daily_assets.assets],
            },
        )
        return daily_assets

    def logout(self) -> None:
        try:
            link_logout = self.driver.find_element(By.LINK_TEXT, "ログアウト")
            link_logout.click()
        except Exception:
            # ログアウト失敗はベストエフォート: 例外を raise しない
            logger.warning("ログアウト処理中に問題が発生しました。")

    def close(self) -> None:
        self.driver.quit()

    def capture_screenshot(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        path = f"/tmp/screenshot_{timestamp}.png"
        self.driver.save_screenshot(path)
        return path

    def get_page_source(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        path = f"/tmp/page_source_{timestamp}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        return path
