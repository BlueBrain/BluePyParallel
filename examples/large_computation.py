"""Example of large computation using BluePyParallel."""
import sys
import time

import numpy as np
import pandas as pd

from bluepyparallel import evaluate
from bluepyparallel import init_parallel_factory


def func(row):
    """Trivial computation."""
    time.sleep(1)

    if row["data"] in [1, 3]:
        raise ValueError(f"The value {row['data']} is forbidden")
    else:
        return {"out": row["data"] + 10}


if __name__ == "__main__":
    parallel_lib = sys.argv[1] or None
    batch_size = int(sys.argv[2]) if len(sys.argv) >= 3 else None
    chunk_size = int(sys.argv[3]) if len(sys.argv) >= 4 else None
    args = int(sys.argv[4]) if len(sys.argv) >= 5 else None

    parallel_factory = init_parallel_factory(parallel_lib, batch_size=batch_size)

    df = pd.DataFrame()
    df["data"] = np.arange(20)

    df = evaluate(
        df,
        func,
        new_columns=[["out", 0]],
        parallel_factory=parallel_factory,
    )
    parallel_factory.shutdown()
    print(df)
    print(df.loc[1, "exception"])
    print(df.loc[3, "exception"])
