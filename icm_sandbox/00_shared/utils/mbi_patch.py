
import numpy as np
import pandas as pd
from mbi import Dataset
import mbi.graphical_model

def patched_synthetic_data(self, rows=None, method='round'):
    """ 
    Patched version of mbi.graphical_model.GraphicalModel.synthetic_data 
    to ensure deterministic column ordering for reproducibility.
    """
    total = int(self.total) if rows is None else rows
    cols = self.domain.attrs
    data = np.zeros((total, len(cols)), dtype=int)
    df = pd.DataFrame(data, columns=cols)
    cliques = [set(cl) for cl in self.cliques]

    def synthetic_col(counts, total):
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

    order = self.elimination_order[::-1]
    col = order[0]
    marg = self.project([col]).datavector(flatten=False)
    df.loc[:, col] = synthetic_col(marg, total)
    used = {col}

    for col in order[1:]:
        relevant = [cl for cl in cliques if col in cl]
        relevant = used.intersection(set.union(*relevant))
        # PATCH: Ensure deterministic ordering of parents by following generation order
        proj = tuple(x for x in order if x in relevant)
        used.add(col)
        marg = self.project(proj + (col,)).datavector(flatten=False)

        def foo(group):
            idx = group.name
            vals = synthetic_col(marg[idx], group.shape[0])
            group[col] = vals
            return group

        if len(proj) >= 1:
            df = df.groupby(list(proj), group_keys=False).apply(foo)
        else:
            df[col] = synthetic_col(marg, df.shape[0])

    return Dataset(df, self.domain)

def apply_patch():
    """ Apply the patch to mbi.graphical_model.GraphicalModel """
    print("Applying reproducibility patch to mbi.graphical_model.GraphicalModel...")
    mbi.graphical_model.GraphicalModel.synthetic_data = patched_synthetic_data
