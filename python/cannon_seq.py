import numpy as np
import time
from utils_io import gen_matrix, frob_norm, append_csv

# Blokovsko množenje: referentna sekvencijalna implementacija.
# Raspoređuje memorijski pristup u blokove dimenzije bs radi boljeg cache ponašanja.
# Opcionalno zapisuje trag: svaka ~10. iteracija upisuje Frobeniusovu normu C u CSV.
def block_mult_trace(A, B, bs, trace_path=None):
    n = A.shape[0]
    C = np.zeros_like(A)
    step = 0
    if trace_path:
        from utils_io import write_csv
        write_csv(trace_path, "step,frob_C", [])
    # Indeksi i,k,j su namerno ovog redosleda radi boljeg lokaliteta podataka.
    for i in range(0, n, bs):
        for k in range(0, n, bs):
            # Svaki (i,k) blok A se koristi za sve j blokove B -> minimizuje se reread A-bloka.
            for j in range(0, n, bs):
                # Množenje dva bs x bs bloka i akumulacija u odgovarajući blok C.
                C[i:i+bs, j:j+bs] += A[i:i+bs, k:k+bs] @ B[k:k+bs, j:j+bs]
                step += 1
                if trace_path and step % 10 == 0:
                    append_csv(trace_path, [(step, frob_norm(C))])
    # Završno merenje stanja.
    if trace_path:
        append_csv(trace_path, [(step, frob_norm(C))])
    return C

# Ulaz: n — dimenzija, bs — blok veličina, seed — determinističan ulaz,
# trace_path — putanja CSV fajla traga (ili None).
# Izlaz: (C, vreme_izvrsavanja)
def run(n: int, bs: int, seed: int = 0, trace_path: str | None = None):
    A = gen_matrix(n, seed)
    B = gen_matrix(n, seed+1)
    t0 = time.perf_counter()
    C = block_mult_trace(A, B, bs, trace_path)
    t1 = time.perf_counter()
    return C, (t1 - t0)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--bs', type=int, default=128)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--trace', type=str, default=None)
    args = ap.parse_args()
    C, dt = run(args.n, args.bs, args.seed, args.trace)
    print(f"time_sec={dt:.6f}")