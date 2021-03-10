import pandas as pd
import sys
import numpy as np
import time
from bluepyparallel import evaluate
from bluepyparallel import init_parallel_factory


def func(row):
    """Trivial computation"""

    time.sleep(1)

    return {"out": row["data"] + 10}


if __name__ == "__main__":
    parallel_lib = sys.argv[1]
    import bglibpy

    parallel_factory = init_parallel_factory(parallel_lib)
    print("using ", parallel_lib)
    df = pd.DataFrame()
    df["data"] = np.arange(1e6)
    print(df)
    df = evaluate(df, func, new_columns=[["out", 0]], parallel_factory=parallel_factory)
    parallel_factory.shutdown()
