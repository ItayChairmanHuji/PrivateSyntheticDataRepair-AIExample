import numpy as np
import pandas as pd
from mbi import Dataset
import mbi.graphical_model

def _synthetic_col(counts, total, method='round'):
    if method == 'sample':
        probas = counts / counts.sum()
        return np.random.choice(counts.size, total, True, probas)
    
    counts *= total / counts.sum()
    frac, integ = np.modf(counts)
    integ = integ.astype(int)
    extra = total - integ.sum()
    if extra > 0:
        idx = np.random.choice(counts.size, extra, False, frac / frac.sum())
        integ[idx] += 1
    vals = np.repeat(np.arange(counts.size), integ)
    np.random.shuffle(vals)
    return vals

def _process_column(df, col, order, used, cliques, model, total, method):
    relevant = [cl for cl in cliques if col in cl]
    relevant = used.intersection(set.union(*relevant))
    proj = tuple(x for x in order if x in relevant)
    used.add(col)
    marg = model.project(proj + (col,)).datavector(flatten=False)

    if len(proj) >= 1:
        def foo(group):
            group[col] = _synthetic_col(marg[group.name], group.shape[0], method)
            return group
        return df.groupby(list(proj), group_keys=False).apply(foo)
    
    df[col] = _synthetic_col(marg, df.shape[0], method)
    return df

def patched_synthetic_data(self, rows=None, method='round'):
    total = int(self.total) if rows is None else rows
    df = pd.DataFrame(np.zeros((total, len(self.domain.attrs)), dtype=int), columns=self.domain.attrs)
    cliques = [set(cl) for cl in self.cliques]
    order = self.elimination_order[::-1]
    
    first_col = order[0]
    marg = self.project([first_col]).datavector(flatten=False)
    df.loc[:, first_col] = _synthetic_col(marg, total, method)
    used = {first_col}

    for col in order[1:]:
        df = _process_column(df, col, order, used, cliques, self, total, method)

    return Dataset(df, self.domain)

def apply_patch():
    print("Applying reproducibility patch to mbi.graphical_model.GraphicalModel...")
    mbi.graphical_model.GraphicalModel.synthetic_data = patched_synthetic_data
