from src.application import ICollectDailyAssetUseCase


class Main:
    def __init__(self, usecase: ICollectDailyAssetUseCase):
        self.usecase = usecase

    def run(self):
        result = self.usecase.execute()
        return result
