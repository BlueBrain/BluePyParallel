"""Example of large computation using BluePyParallel."""

# Copyright 2021-2024 Blue Brain Project / EPFL

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
