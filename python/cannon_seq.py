import numpy as np
import time
from utils_io import gen_matrix, frob_norm, append_csv

# blokovsko množenje kao dobra baza za poređenje
def block_mult_trace(A, B, bs, trace_path=None):
    n = A.shape[0]
    C = np.zeros_like(A)
    step = 0
    if trace_path:
        from utils_io import write_csv
        write_csv(trace_path, "step,frob_C", [])
    for i in range(0, n, bs):
        for k in range(0, n, bs):
            for j in range(0, n, bs):
                C[i:i+bs, j:j+bs] += A[i:i+bs, k:k+bs] @ B[k:k+bs, j:j+bs]
                step += 1
                if trace_path and step % 10 == 0:
                    append_csv(trace_path, [(step, frob_norm(C))])
    if trace_path:
        append_csv(trace_path, [(step, frob_norm(C))])
    return C

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