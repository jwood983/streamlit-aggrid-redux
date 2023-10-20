import numpy as np
import pandas as pd
import pyarrow as pa

from typing import Union

DataElement = Union[np.ndarray, pd.DataFrame, pa.Table, dict, str]
