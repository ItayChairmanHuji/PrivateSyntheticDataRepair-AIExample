
import pandas as pd
from src.loading.file_loader import FileLoader
from src.loading.components.data_loader import DataLoader
from src.loading.components.dcs_loader import DCsLoader
from src.loading.components.metadata_loader import MetadataLoader
from src.loading.components.data_encoder import DataEncoder
from src.loading.components.dcs_encoder import DCsEncoder
from src.loading.violation_finder import ViolationFinder

def inspect():
    loader = FileLoader(
        name="compas", 
        base_path="data",
        data_loader=DataLoader(),
        dcs_loader=DCsLoader(),
        metadata_loader=MetadataLoader(),
        data_encoder=DataEncoder(),
        dcs_encoder=DCsEncoder()
    )
    dataset = loader.load()
    df = dataset.data
    
    print("\n--- Encoded Denial Constraints ---")
    finder = ViolationFinder()
    for dc in dataset.dcs.constraints:
        print(dc.to_string())
        eq, ineq, u1, u2 = finder._categorize_predicates(dc)
        print(f"  EQ Keys: {eq}")
        print(f"  Ineq Preds: {[p.to_string() for p in ineq]}")
        print(f"  U1: {[p.to_string() for p in u1]}")
        print(f"  U2: {[p.to_string() for p in u2]}")
        
    violations = dataset.get_violations()
    
    print(f"Found {len(violations)} violations.")
    if len(violations) > 0:
        sample = violations.head(10)
        # Get mapping to decode values
        mappings = dataset.mappings
        
        for _, row in sample.iterrows():
            i1, i2 = int(row['idx1']), int(row['idx2'])
            t1, t2 = df.iloc[i1], df.iloc[i2]
            
            print(f"\nViolation Pair: ({i1}, {i2})")
            # Decode for readability if possible
            st1 = mappings['ScoreText'].inverse_transform([int(t1['ScoreText'])])[0]
            st2 = mappings['ScoreText'].inverse_transform([int(t2['ScoreText'])])[0]
            
            print(f"t1: ScoreText={st1} ({t1['ScoreText']}), DecileScore={t1['DecileScore']}")
            print(f"t2: ScoreText={st2} ({t2['ScoreText']}), DecileScore={t2['DecileScore']}")
            
            # Check the OC: not(t1.ScoreText='Low' & t2.ScoreText='High' & t1.DecileScore > t2.DecileScore)
            # wait, the logic I used in inspect assumes the first DC. 
            # Let's check which DC produced these.
            
    # Also check the raw values in data.csv for a few specific indices
    raw_data = pd.read_csv("data/compas/data.csv")
    print("\n--- Raw Data Check ---")
    # Let's look for any 'Low' score with Decile > any 'High' score
    lows = raw_data[raw_data['ScoreText'] == 'Low']
    highs = raw_data[raw_data['ScoreText'] == 'High']
    print(f"Lows: {len(lows)}, Highs: {len(highs)}")
    print("Max Decile in Low:", lows['DecileScore'].max())
    print("Min Decile in High:", highs['DecileScore'].min())

if __name__ == "__main__":
    inspect()
