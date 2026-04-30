import pandas as pd
from snsynth import Synthesizer as SNSynthesizer

from src.datasets.dataset import Dataset
from src.loggers.logger import Logger
from src.synthesizers.synthesizer import Synthesizer


class SmartNoiseSynthesizer(Synthesizer):
    def __init__(self, model_name, output_size: int, privacy_budget: float, logger: Logger, config: dict = {}):
        super().__init__(logger)
        self.model_name = model_name
        self.output_size = output_size
        self.privacy_budget = privacy_budget
        self.config = config

    def _get_synthetic_data(self, private_data: Dataset) -> pd.DataFrame:
        self.logger.log("synthesizer_privacy_budget", self.privacy_budget)
        synth = SNSynthesizer.create(self.model_name, epsilon=self.privacy_budget, **self.config)
        self.timer(lambda: synth.fit(private_data.data, categorical_columns=private_data.columns))
        return synth.sample(self.output_size)