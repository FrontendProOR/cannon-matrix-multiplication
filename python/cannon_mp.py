import numpy as np
import time
import multiprocessing as mp
from multiprocessing import shared_memory
from utils_io import gen_matrix, append_csv, frob_norm

# Pretpostavke: n je deljivo sa q. Mreža procesa je q×q, ukupan broj procesa p=q*q.
# Svaki proces računa svoj lokalni blok C_{ij} dimenzije b×b gde je b=n//q.


# Radnik procesa: dohvaća deljene matrice iz shared_memory, formira početno poravnanje
# (Cannon: A levo ciklično po redovima, B gore ciklično po kolonama), u svakoj rundi
# radi lokalno blok-množenje i zatim izvrši rotaciju pokazivača na sledeće blokove.
# barrier sinhronizuje sve procese pre i posle rotacije.
# trace_pipe opcionalno šalje par (faza, ||C_loc||_F) roditeljskom procesu radi traga.
def worker(idx, q, n, shm_names, rounds, barrier, trace_pipe):
    b = n // q
    i, j = divmod(idx, q) # 2D koordinata procesa u q×q mreži

    # Mapiranje deljenog segmenta memorije u NumPy nizove.
    shmA = shared_memory.SharedMemory(name=shm_names['A'])
    shmB = shared_memory.SharedMemory(name=shm_names['B'])
    shmC = shared_memory.SharedMemory(name=shm_names['C'])
    C = np.ndarray((n, n), dtype=np.float64, buffer=shmC.buf)
    A = np.ndarray((n, n), dtype=np.float64, buffer=shmA.buf)
    B = np.ndarray((n, n), dtype=np.float64, buffer=shmB.buf)

    # Pomoćna: izdvajanje bs×bs bloka po indeksima (ii, jj) u q×q mreži blokova.
    def view(mat, ii, jj):
        return mat[ii*b:(ii+1)*b, jj*b:(jj+1)*b]

    # Početno poravnanje (Cannon):
    # A: svaka vrsta i se ciklično pomeri ulevo za i → (i, j) uzima A(i, j+i mod q)
    # B: svaka kolona j se ciklično pomeri naviše za j → (i, j) uzima B(i+j mod q, j)
    a_i, a_j = i, (j + i) % q
    b_i, b_j = (i + j) % q, j

    # Lokalne kopije inicijalnih blokova A i B; C_loc akumulira rezultat.
    A_loc = view(A, a_i, a_j).copy()
    B_loc = view(B, b_i, b_j).copy()
    C_loc = np.zeros((b, b), dtype=np.float64)

    for r in range(rounds):
        # Lokalno blok množenje i akumulacija.
        C_loc += A_loc @ B_loc
        barrier.wait() # sinhronizacija pre rotacije # svi završe računanje pre rotacije

        # if i==0 and j==0 and trace_pipe is not None:
        if trace_pipe is not None:
            # Slanje Frobenius norme lokalnog rezultata za trenutnu fazu r
            trace_pipe.send((r, float(np.linalg.norm(C_loc))))
        # Rotacije pokazivača na sledeće A i B blokove u Cannon ciklusu
        next_a_j = (a_j - 1) % q # A se kreće ulevo unutar vrste
        next_b_i = (b_i - 1) % q # B se kreće naviše unutar kolone
        A_loc = view(A, a_i, next_a_j).copy()
        B_loc = view(B, next_b_i, b_j).copy()
        a_j = next_a_j
        b_i = next_b_i
        barrier.wait() # svi završe izbor sledećih blokova

    # Upis lokalnog rezultata u globalnu C matricu na poziciju (i,j)
    view(C, i, j)[:] = C_loc

    # Zatvaranje referenci na deljene segmente u radniku.
    shmA.close(); shmB.close(); shmC.close()

# Orkestracija: priprema podataka, deljene memorije, procesa i kolekcija traga.
# Vraća: (C, ukupno_vreme).

def run(n: int, q: int, seed: int = 0, trace_path: str | None = None):
    assert n % q == 0
    p = q*q
    # Determinističke ulazne matrice.
    A = gen_matrix(n, seed)
    B = gen_matrix(n, seed+1)
    C = np.zeros((n, n), dtype=np.float64)

    # Alokacija deljene memorije za A, B, C i inicijalno popunjavanje.
    shmA = shared_memory.SharedMemory(create=True, size=A.nbytes)
    shmB = shared_memory.SharedMemory(create=True, size=B.nbytes)
    shmC = shared_memory.SharedMemory(create=True, size=C.nbytes)
    A_sh = np.ndarray(A.shape, dtype=A.dtype, buffer=shmA.buf); A_sh[:] = A
    B_sh = np.ndarray(B.shape, dtype=B.dtype, buffer=shmB.buf); B_sh[:] = B
    C_sh = np.ndarray(C.shape, dtype=C.dtype, buffer=shmC.buf); C_sh[:] = 0

    names = {'A': shmA.name, 'B': shmB.name, 'C': shmC.name}
    rounds = q # Broj Cannon rundi = q

    barrier = mp.Barrier(p) # globalna barijera za sve procese

    parent_conns = []
    child_conns = []
    if trace_path:
        # Jednosmerni Pipe ka roditelju za svaki proces.
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
    # Kolekcija traga u roditelju: čitanje runde po proces.
    if trace_path:
        for r in range(rounds):
            for idx in range(p):
                ph, val = parent_conns[idx].recv()
                append_csv(trace_path, [(ph, idx, val)])
    for proc in procs: proc.join()
    t1 = time.perf_counter()

    # Kopija C iz deljene memorije pre dealokacije.
    C = np.ndarray(C.shape, dtype=C.dtype, buffer=shmC.buf).copy()

    # Čišćenje deljenih segmenata.
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
        # Verifikacija prema sekvencijalnom blokovskom rešenju;
        # bs ~ n/q kao razumna vrednost bloka.
        from cannon_seq import run as run_seq
        Ref, _ = run_seq(args.n, bs=max(32, args.n//args.q), seed=args.seed)
        err, ok = check_close(C, Ref)
        print(f"verify_err={err:.3e}, ok={ok}")