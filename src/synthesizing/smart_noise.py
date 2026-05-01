import pandas as pd
from snsynth import Synthesizer as SnSynthesizer
from src.entities.dataset import Dataset
from src.synthesizing.synthesizer import Synthesizer

class SmartNoiseSynthesizer(Synthesizer):
    """
    Integration with the SmartNoise (snsynth) library for Differential Privacy (DP) synthetic data generation.
    
    This synthesizer supports multiple DP algorithms provided by the SmartNoise ecosystem, 
    including MST, AIM, and PATECTGAN. It automatically handles basic data type inference 
    and ensures the output matches the project's Dataset structures.
    
    Attributes:
        engine (str): The name of the synthesis algorithm (e.g., "mst", "aim", "patectgan").
        epsilon (float): The privacy budget.
        kwargs (dict): Additional parameters passed directly to the underlying SmartNoise algorithm.
    """
    def __init__(self, engine: str, epsilon: float = 1.0, **kwargs):
        """
        Initializes the synthesizer with a specific engine and privacy parameters.
        
        Args:
            engine (str): Algorithm name.
            epsilon (float): Privacy budget (default: 1.0).
            **kwargs: Extra arguments. Supports a nested 'kwargs' dictionary for compatibility.
        """
        self.engine = engine
        self.epsilon = epsilon
        # Support both flattened kwargs and a nested 'kwargs' dictionary
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], dict):
            extra_args = kwargs.pop('kwargs')
            kwargs.update(extra_args)
        self.kwargs = kwargs

    def synthesize(self, dataset: Dataset) -> Dataset:
        """
        Generates a synthetic version of the provided dataset.
        
        Args:
            dataset (Dataset): The source dataset to synthesize.
            
        Returns:
            Dataset: A new dataset object containing the synthetic data.
        """
        synth = SnSynthesizer.create(self.engine, epsilon=self.epsilon, **self.kwargs)
        synth.fit(dataset.data)
        synthetic_df = synth.sample(len(dataset.data))
        
        # Ensure it's a DataFrame (some engines might return numpy)
        if not isinstance(synthetic_df, pd.DataFrame):
            synthetic_df = pd.DataFrame(synthetic_df, columns=dataset.data.columns)

        return Dataset(
            name=f"{dataset.name}_{self.engine}",
            data=synthetic_df,
            dcs=dataset.dcs,
            target=dataset.target
        )
