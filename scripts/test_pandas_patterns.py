
import pandas as pd
import numpy as np
import time
import duckdb

def benchmark_patterns():
    n = 1000000
    limit = 100000
    
    print(f"=== Pattern 1: Conditional Constant-Value FD (C-FD-C) ===")
    data_p1 = pd.DataFrame({
        'AGEP': np.random.choice([0, 1], size=n, p=[0.1, 0.9]),
        'SCHL': np.random.randint(0, 10, size=n)
    })
    
    start = time.time()
    df_agep0 = data_p1[data_p1['AGEP'] == 0]
    idx_schl0 = df_agep0[df_agep0['SCHL'] == 0].index
    idx_schl_not0 = df_agep0[df_agep0['SCHL'] != 0].index
    
    res = []
    count = 0
    if not idx_schl0.empty and not idx_schl_not0.empty:
        for i1 in idx_schl0:
            for i2 in idx_schl_not0:
                res.append((i1, i2))
                count += 1
                if count >= limit: break
            if count >= limit: break
    t_p1 = time.time() - start
    print(f"Pandas P1 time: {t_p1:.4f}s, Found: {len(res)}")

    print(f"\n=== Pattern 2: Standard FD (Single Key) ===")
    data_p2 = pd.DataFrame({
        'CIT': np.random.randint(0, 50, size=n),
        'NATIVITY': np.random.randint(0, 2, size=n)
    })
    
    start = time.time()
    # Faster way in pandas: use groupby and only look at groups with >1 unique NATIVITY
    groups = data_p2.groupby('CIT')
    res2 = []
    count2 = 0
    for name, group in groups:
        if count2 >= limit: break
        val_counts = group['NATIVITY'].value_counts()
        if len(val_counts) > 1:
            # Different values exist
            vals = val_counts.index.tolist()
            # Pairs between different values
            for i in range(len(vals)):
                for j in range(i+1, len(vals)):
                    idx1 = group[group['NATIVITY'] == vals[i]].index
                    idx2 = group[group['NATIVITY'] == vals[j]].index
                    for v1 in idx1:
                        for v2 in idx2:
                            res2.append((v1, v2))
                            count2 += 1
                            if count2 >= limit: break
                        if count2 >= limit: break
                    if count2 >= limit: break
                if count2 >= limit: break
    t_p2 = time.time() - start
    print(f"Pandas P2 time: {t_p2:.4f}s, Found: {len(res2)}")

    print(f"\n=== Pattern 3: Standard FD (DuckDB Optimized) ===")
    con = duckdb.connect(database=':memory:')
    con.register('data_raw', data_p2)
    start = time.time()
    # Identifying groups with violations is extremely fast in DuckDB
    query_groups = "SELECT CIT FROM data_raw GROUP BY CIT HAVING COUNT(DISTINCT NATIVITY) > 1"
    violating_cits = con.execute(query_groups).df()['CIT'].tolist()
    
    # Then we can either join in DuckDB or process in Pandas
    # For many violations, DuckDB join is usually faster
    if violating_cits:
        query_violations = f"""
            SELECT t1.rowid as idx1, t2.rowid as idx2
            FROM data_raw t1
            JOIN data_raw t2 ON t1.CIT = t2.CIT
            WHERE t1.CIT IN ({','.join(map(str, violating_cits))})
              AND t1.rowid < t2.rowid
              AND t1.NATIVITY != t2.NATIVITY
            LIMIT {limit}
        """
        # Note: rowid in DuckDB starts from 0 if registered from pandas? Actually safer to add explicit index
        con.execute("CREATE TABLE dt AS SELECT *, row_number() OVER () - 1 as __idx FROM data_raw")
        query_violations = f"""
            SELECT t1.__idx as idx1, t2.__idx as idx2
            FROM dt t1
            JOIN dt t2 ON t1.CIT = t2.CIT
            WHERE t1.__idx < t2.__idx
              AND t1.NATIVITY != t2.NATIVITY
            LIMIT {limit}
        """
        res3 = con.execute(query_violations).df()
    t_p3 = time.time() - start
    print(f"DuckDB P3 time: {t_p3:.4f}s, Found: {len(res3)}")

if __name__ == "__main__":
    benchmark_patterns()
