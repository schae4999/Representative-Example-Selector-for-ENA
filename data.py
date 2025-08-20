from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
df = pd.read_csv(app_dir / "ref_pipe_paired_code_occurrences.csv")
