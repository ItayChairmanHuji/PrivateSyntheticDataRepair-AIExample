
import pandas as pd
import numpy as np
import time
from src.loading.file_loader import FileLoader
from src.loading.components.data_loader import DataLoader
from src.loading.components.dcs_loader import DCsLoader
from src.loading.components.metadata_loader import MetadataLoader
from src.loading.components.data_encoder import DataEncoder
from src.loading.components.dcs_encoder import DCsEncoder
from src.synthesizing.co_noise import CoNoise

def get_loader(name):
    return FileLoader(
        name=name,
        base_path="data",
        data_loader=DataLoader(),
        dcs_loader=DCsLoader(),
        metadata_loader=MetadataLoader(),
        data_encoder=DataEncoder(),
        dcs_encoder=DCsEncoder()
    )

def test_user_suggestion():
    print("Loading Census...")
    loader = get_loader("census")
    dataset = loader.load()
    
    print(f"Loaded {len(dataset.data)} rows. Adding noise...")
    synthesizer = CoNoise(num_of_iterations=100, seed=42)
    noisy_dataset = synthesizer.synthesize(dataset)
    df = noisy_dataset.data
    
    # User Suggestion for FD: not(t1.CIT=t2.CIT & t1.NATIVITY!=t2.NATIVITY)
    print("Finding violations with user's suggested logic...")
    start = time.time()
    
    # 1. Identify where A (CIT) points to more than one unique B (NATIVITY)
    mask = df.groupby('CIT')['NATIVITY'].transform('nunique') > 1
    
    # 2. Filter the dataframe to see the violations
    violations_df = df[mask].sort_values('CIT')
    
    t_user = time.time() - start
    print(f"User Logic Time: {t_user:.4f}s")
    print(f"Number of problematic rows: {len(violations_df)}")
    
    # Now, to actually get the idx1, idx2 pairs (required by the system):
    print("Generating idx1, idx2 pairs from problematic rows...")
    start_pairs = time.time()
    
    res = []
    # Group by CIT and find pairs with different NATIVITY
    for name, group in violations_df.groupby('CIT'):
        # For each group, we can have multiple values of NATIVITY
        # Every row with NATIVITY=v1 conflicts with every row with NATIVITY=v2
        indices_by_val = group.groupby('NATIVITY').groups
        vals = list(indices_by_val.keys())
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                # Cross product of indices
                idx_i = indices_by_val[vals[i]]
                idx_j = indices_by_val[vals[j]]
                # Use itertools.product or similar
                import itertools
                for pair in itertools.product(idx_i, idx_j):
                    res.append(pair)
                    
    df_pairs = pd.DataFrame(res, columns=['idx1', 'idx2'])
    t_pairs = time.time() - start_pairs
    print(f"Pair Generation Time: {t_pairs:.4f}s, Total Pairs: {len(df_pairs)}")

if __name__ == "__main__":
    test_user_suggestion()
