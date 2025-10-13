import numpy as np
from pathlib import Path

def gen_matrix(n: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.random((n, n), dtype=np.float64)

def write_csv(path: str, header: str, rows: list[tuple]):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='') as f:
        f.write(header + "\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")

def append_csv(path: str, rows: list[tuple]):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a', newline='') as f:
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")

def check_close(C: np.ndarray, Ref: np.ndarray, tol=1e-9):
    err = np.max(np.abs(C-Ref))
    return err, err < tol

def frob_norm(x: np.ndarray) -> float:
    return float(np.linalg.norm(x))