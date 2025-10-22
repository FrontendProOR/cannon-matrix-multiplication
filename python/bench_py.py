import argparse, time
from utils_io import write_csv

# Višestruka merenja funkcije fn(), sa detekcijom i izbacivanjem outlier-a.
# Sortira vremena, računa IQR i zadržava vrednosti u [Q1-1.5*IQR, Q3+1.5*IQR].
# Vraća srednju vrednost, standardnu devijaciju i broj zadržanih uzoraka.
def timings(fn, reps=30):
    vals = []
    for _ in range(reps):
        t0 = time.perf_counter(); fn(); vals.append(time.perf_counter()-t0)
    vals.sort()
    q1 = vals[len(vals)//4]; q3 = vals[(3*len(vals))//4]
    iqr = q3 - q1
    low, high = q1 - 1.5*iqr, q3 + 1.5*iqr
    core = [v for v in vals if low <= v <= high]
    mean = sum(core)/len(core)
    stdev = (sum((x-mean)**2 for x in core)/len(core))**0.5
    return {'mean': mean,'stdev': stdev,'n': len(core),'dropped': len(vals)-len(core)}

if __name__ == "__main__":
    from cannon_seq import run as run_seq
    from cannon_mp import run as run_mp
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['strong_py','weak_py'], required=True)
    ap.add_argument('--n', type=int, default=2048)
    ap.add_argument('--bs', type=int, default=128)
    ap.add_argument('--q_list', type=str, default='1,2,4')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--reps', type=int, default=30)
    ap.add_argument('--out', type=str, default='../data/logs/bench_py.csv')
    args = ap.parse_args()

    rows = []
    if args.mode == 'strong_py':
        # Jako skaliranje: n je fiksno; menjamo q → p=q*q.
        for q in [int(x) for x in args.q_list.split(',')]:
            seq = timings(lambda: run_seq(args.n, args.bs, args.seed)[1], args.reps)
            par = timings(lambda: run_mp(args.n, q, args.seed)[1], args.reps)
            S = (seq['mean']/par['mean']) if par['mean']>0 else 0
            rows.append(("strong", args.n, q, q*q, seq['mean'], seq['stdev'], par['mean'], par['stdev'], S, par['n']))
    else:
        # Slabo skaliranje: dimenzija raste ~ proporcionalno q tako da je posao po jezgri konstantan.
        base_b = args.bs*2 # bazični korak dimenzije; efektivno n = base_b * q
        for q in [int(x) for x in args.q_list.split(',')]:
            n = base_b * q
            seq = timings(lambda: run_seq(n, args.bs, args.seed)[1], args.reps)
            par = timings(lambda: run_mp(n, q, args.seed)[1], args.reps)
            S = (seq['mean']/par['mean']) if par['mean']>0 else 0
            rows.append(("weak", n, q, q*q, seq['mean'], seq['stdev'], par['mean'], par['stdev'], S, par['n']))

    #CSV izlaz uključuje prosek, stdev, broj uzoraka posle outlier filtera i speedup.
    header = "mode,N,q,p,seq_mean,seq_stdev,par_mean,par_stdev,speedup,used_samples"
    write_csv(args.out, header, rows)
    print(f"wrote {args.out}")