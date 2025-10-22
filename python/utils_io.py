import numpy as np
from pathlib import Path

# Deterministička generacija kvadratne matrice N x N sa vrednostima u [0,1).
# seed → omogućava reprodukciju eksperimenata.
def gen_matrix(n: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.random((n, n), dtype=np.float64)

# Kreiranje CSV fajla sa zadatim hederom i redovima.
# Ako parent direktorijum ne postoji → pravi se.
def write_csv(path: str, header: str, rows: list[tuple]):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='') as f:
        f.write(header + "\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")

# Dodavanje redova na kraj postojećeg CSV-a. Kreira parent direktorijum po potrebi.
def append_csv(path: str, rows: list[tuple]):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a', newline='') as f:
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")

# Maksimalna apsolutna greška i indikator prolaza verifikacije u odnosu na toleranciju.
def check_close(C: np.ndarray, Ref: np.ndarray, tol=1e-9):
    err = np.max(np.abs(C-Ref))
    return err, err < tol

# Frobeniusova norma matrice, kao skalarni rezime stanja.
def frob_norm(x: np.ndarray) -> float:
    return float(np.linalg.norm(x))