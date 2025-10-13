import numpy as np
import time
import multiprocessing as mp
from multiprocessing import shared_memory
from utils_io import gen_matrix, append_csv, frob_norm

# Pretpostavka: N deljivo sa q. Procesorska mreža q×q. p=q*q procesa.
# Svaki proces drži lokalne blokove Aij, Bij, Cij dimenzije b×b, b=N//q.

def worker(idx, q, n, shm_names, rounds, barrier, trace_pipe):
    b = n // q
    i, j = divmod(idx, q)

    shmA = shared_memory.SharedMemory(name=shm_names['A'])
    shmB = shared_memory.SharedMemory(name=shm_names['B'])
    shmC = shared_memory.SharedMemory(name=shm_names['C'])
    C = np.ndarray((n, n), dtype=np.float64, buffer=shmC.buf)
    A = np.ndarray((n, n), dtype=np.float64, buffer=shmA.buf)
    B = np.ndarray((n, n), dtype=np.float64, buffer=shmB.buf)

    def view(mat, ii, jj):
        return mat[ii*b:(ii+1)*b, jj*b:(jj+1)*b]

    a_i, a_j = i, (j + i) % q
    b_i, b_j = (i + j) % q, j

    A_loc = view(A, a_i, a_j).copy()
    B_loc = view(B, b_i, b_j).copy()
    C_loc = np.zeros((b, b), dtype=np.float64)

    for r in range(rounds):
        C_loc += A_loc @ B_loc
        barrier.wait() # sinhronizacija pre rotacije
        # if i==0 and j==0 and trace_pipe is not None:
        if trace_pipe is not None:
            trace_pipe.send((r, float(np.linalg.norm(C_loc))))
        next_a_j = (a_j - 1) % q
        next_b_i = (b_i - 1) % q
        A_loc = view(A, a_i, next_a_j).copy()
        B_loc = view(B, next_b_i, b_j).copy()
        a_j = next_a_j
        b_i = next_b_i
        barrier.wait()

    view(C, i, j)[:] = C_loc

    shmA.close(); shmB.close(); shmC.close()

def run(n: int, q: int, seed: int = 0, trace_path: str | None = None):
    assert n % q == 0
    p = q*q
    A = gen_matrix(n, seed)
    B = gen_matrix(n, seed+1)
    C = np.zeros((n, n), dtype=np.float64)

    shmA = shared_memory.SharedMemory(create=True, size=A.nbytes)
    shmB = shared_memory.SharedMemory(create=True, size=B.nbytes)
    shmC = shared_memory.SharedMemory(create=True, size=C.nbytes)
    A_sh = np.ndarray(A.shape, dtype=A.dtype, buffer=shmA.buf); A_sh[:] = A
    B_sh = np.ndarray(B.shape, dtype=B.dtype, buffer=shmB.buf); B_sh[:] = B
    C_sh = np.ndarray(C.shape, dtype=C.dtype, buffer=shmC.buf); C_sh[:] = 0

    names = {'A': shmA.name, 'B': shmB.name, 'C': shmC.name}
    rounds = q

    barrier = mp.Barrier(p)

    parent_conns = []
    child_conns = []
    if trace_path:
        for _ in range(p):
            pc, cc = mp.Pipe(duplex=False)
            parent_conns.append(pc); child_conns.append(cc)
        from utils_io import write_csv
        write_csv(trace_path, "phase,worker_idx,frob_C_loc", [])

    t0 = time.perf_counter()
    procs = []
    for idx in range(p):
        tr = child_conns[idx] if trace_path else None
        proc = mp.Process(target=worker, args=(idx, q, n, names, rounds, barrier, tr))
        proc.start(); procs.append(proc)
    if trace_path:
        for r in range(rounds):
            for idx in range(p):
                ph, val = parent_conns[idx].recv()
                append_csv(trace_path, [(ph, idx, val)])
    for proc in procs: proc.join()
    t1 = time.perf_counter()

    C = np.ndarray(C.shape, dtype=C.dtype, buffer=shmC.buf).copy()

    shmA.close(); shmA.unlink()
    shmB.close(); shmB.unlink()
    shmC.close(); shmC.unlink()

    return C, (t1 - t0)

if __name__ == "__main__":
    import argparse
    from utils_io import check_close
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--q', type=int, required=True)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--trace', type=str, default=None)
    args = ap.parse_args()
    C, dt = run(args.n, args.q, args.seed, args.trace)
    print(f"time_sec={dt:.6f}")
    if args.verify:
        from cannon_seq import run as run_seq
        Ref, _ = run_seq(args.n, bs=max(32, args.n//args.q), seed=args.seed)
        err, ok = check_close(C, Ref)
        print(f"verify_err={err:.3e}, ok={ok}")