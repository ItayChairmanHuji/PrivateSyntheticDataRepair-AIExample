
import pandas as pd
import numpy as np
import time
import duckdb
import itertools

def benchmark_fd():
    print("\n--- Pattern: Functional Dependency (A -> B) ---")
    n = 1000000
    group_size = 100
    num_groups = n // group_size
    data = pd.DataFrame({
        'A': np.repeat(np.arange(num_groups), group_size),
        'B': np.random.randint(0, 2, size=n)
    })
    
    # DuckDB
    start = time.time()
    con = duckdb.connect(database=':memory:')
    con.register('df', data)
    con.execute("CREATE TABLE dt AS SELECT *, row_number() OVER () - 1 as __idx FROM df")
    res_ddb = con.execute("""
        SELECT t1.__idx as idx1, t2.__idx as idx2
        FROM dt t1 JOIN dt t2 ON t1.A = t2.A
        WHERE t1.__idx < t2.__idx AND t1.B != t2.B
    """).df()
    t_ddb = time.time() - start
    print(f"DuckDB: {t_ddb:.4f}s, Violations: {len(res_ddb)}")
    
    # Pandas (Optimized with GroupBy)
    start = time.time()
    res_pd = []
    for name, group in data.groupby('A'):
        if group['B'].nunique() > 1:
            indices = group.index.values
            vals = group['B'].values
            # Cross product within group where values differ
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    if vals[i] != vals[j]:
                        res_pd.append((indices[i], indices[j]))
    df_pd = pd.DataFrame(res_pd, columns=['idx1', 'idx2'])
    t_pd = time.time() - start
    print(f"Pandas (Loop): {t_pd:.4f}s, Violations: {len(df_pd)}")

    # Pandas (Vectorized Group Join)
    start = time.time()
    # This is basically what DuckDB does but in Pandas
    merged = data.reset_index().merge(data.reset_index(), on='A')
    filtered = merged[(merged['index_x'] < merged['index_y']) & (merged['B_x'] != merged['B_y'])]
    res_pd_vec = filtered[['index_x', 'index_y']]
    t_pd_vec = time.time() - start
    print(f"Pandas (Merge): {t_pd_vec:.4f}s, Violations: {len(res_pd_vec)}")

def benchmark_cross_filter():
    print("\n--- Pattern: Cross-Filter Order (Compas) ---")
    # not(t1.S='Low' & t2.S='High' & t1.V > t2.V)
    n = 100000
    data = pd.DataFrame({
        'S': np.random.choice(['Low', 'High', 'Other'], size=n),
        'V': np.random.randint(0, 100, size=n)
    })
    
    # DuckDB
    start = time.time()
    con = duckdb.connect(database=':memory:')
    con.register('df', data)
    con.execute("CREATE TABLE dt AS SELECT *, row_number() OVER () - 1 as __idx FROM df")
    res_ddb = con.execute("""
        SELECT t1.__idx as idx1, t2.__idx as idx2
        FROM dt t1 JOIN dt t2 ON 1=1
        WHERE t1.S = 'Low' AND t2.S = 'High' AND t1.V > t2.V
    """).df()
    t_ddb = time.time() - start
    print(f"DuckDB: {t_ddb:.4f}s, Violations: {len(res_ddb)}")
    
    # NumPy Broadcasting
    start = time.time()
    idx1 = data[data['S'] == 'Low'].index.values
    idx2 = data[data['S'] == 'High'].index.values
    v1 = data.loc[idx1, 'V'].values
    v2 = data.loc[idx2, 'V'].values
    mask = v1[:, None] > v2
    rel_i, rel_j = np.where(mask)
    res_np = pd.DataFrame({'idx1': idx1[rel_i], 'idx2': idx2[rel_j]})
    t_np = time.time() - start
    print(f"NumPy Broadcast: {t_np:.4f}s, Violations: {len(res_np)}")

if __name__ == "__main__":
    benchmark_fd()
    benchmark_cross_filter()
