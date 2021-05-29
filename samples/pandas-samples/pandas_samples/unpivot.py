import pandas._testing as tm
import pandas as pd
import numpy as np


def unpivot(frame):
    """
    Example:
    >>> df
             date variable     value
    0  2000-01-03        A  0.895557
    1  2000-01-04        A  0.779718
    2  2000-01-05        A  0.738892
    3  2000-01-03        B -1.513487
    4  2000-01-04        B -0.543134
    5  2000-01-05        B  0.902733
    6  2000-01-03        C -0.053496
    7  2000-01-04        C  0.298079
    8  2000-01-05        C -1.962022
    9  2000-01-03        D -0.174269
    10 2000-01-04        D -0.047428
    11 2000-01-05        D -1.871996
    >>> tm.makeTimeDataFrame(3)
                       A         B         C         D
    2000-01-03 -0.911447  0.274853 -0.740769  2.330942
    2000-01-04 -0.208471 -1.024612  0.512266 -0.708707
    2000-01-05 -1.368389 -3.464163 -1.940530 -1.149835
    """
    N, K = frame.shape
    data = {
        "value": frame.to_numpy().ravel("F"),
        "variable": np.asarray(frame.columns).repeat(N),
        "date": np.tile(np.asarray(frame.index), K),
    }
    return pd.DataFrame(data, columns=["date", "variable", "value"])

df = tm.makeTimeDataFrame(3)

print("Just a random frame: {}".format(df))

df_pivoted = unpivot(df)

print("After performing unpivot: {}".format(df_pivoted))

