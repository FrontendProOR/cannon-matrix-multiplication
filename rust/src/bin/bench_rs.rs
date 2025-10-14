use std::env;
use std::fs::{create_dir_all, File};
use std::io::Write;
use std::process::Command;
use std::time::Instant;

fn time_once<F: FnOnce()>(f: F) -> f64 {
    let t0 = Instant::now();
    f();
    t0.elapsed().as_secs_f64()
}

fn mean_stdev(vals: &[f64]) -> (f64, f64) {
    let n = vals.len() as f64;
    let m = vals.iter().sum::<f64>() / n;
    let v = vals.iter().map(|x| (x - m) * (x - m)).sum::<f64>() / n;
    (m, v.sqrt())
}

fn count_outliers_3sigma(vals: &[f64], mean: f64, stdev: f64) -> usize {
    if stdev == 0.0 { return 0; }
    let low = mean - 3.0 * stdev;
    let high = mean + 3.0 * stdev;
    vals.iter().filter(|&&x| x < low || x > high).count()
}

fn main() {
    // usage:
    // bench_rs <strong_rs|weak_rs> <q_list> <n> <bs> <reps> <out_csv>
    let mode = env::args().nth(1).expect("mode strong_rs|weak_rs");
    let q_list: Vec<usize> = env::args().nth(2).unwrap_or("1,2,4".into())
        .split(',').map(|s| s.parse().unwrap()).collect();
    let n_input: usize = env::args().nth(3).unwrap_or("1024".into()).parse().unwrap();
    let bs: usize = env::args().nth(4).unwrap_or("128".into()).parse().unwrap();
    let reps: usize = env::args().nth(5).unwrap_or("30".into()).parse().unwrap();
    let out = env::args().nth(6).unwrap_or("../data/logs/bench_rs.csv".into());

    create_dir_all("../data/logs").ok();
    let mut f = File::create(out).unwrap();
    // Dodali smo stdev + min/max + broj outliera 3σ
    writeln!(
        f,
        "mode,N,q,p,seq_mean,seq_stdev,seq_min,seq_max,seq_outliers3s,par_mean,par_stdev,par_min,par_max,par_outliers3s,speedup"
    ).unwrap();

    let base_b = bs * 2; // slabo skaliranje: N = base_b * q

    for &q in &q_list {
        let (n, p) = if mode == "strong_rs" { (n_input, q*q) } else { (base_b * q, q*q) };

        // sekvencijalno: reps puta
        let mut seq = Vec::with_capacity(reps);
        for _ in 0..reps {
            let t = time_once(|| {
                let status = Command::new("./target/release/cannon_seq")
                    .args([n.to_string(), bs.to_string()])
                    .status()
                    .expect("run cannon_seq");
                assert!(status.success());
            });
            seq.push(t);
        }
        let (seq_mean, seq_stdev) = mean_stdev(&seq);
        let (seq_min, seq_max) = (
            seq.iter().cloned().fold(f64::INFINITY, f64::min),
            seq.iter().cloned().fold(f64::NEG_INFINITY, f64::max),
        );
        let seq_out = count_outliers_3sigma(&seq, seq_mean, seq_stdev);

        // paralelno: reps puta
        let mut par = Vec::with_capacity(reps);
        for _ in 0..reps {
            let t = time_once(|| {
                let status = Command::new("./target/release/cannon_threads")
                    .args([n.to_string(), q.to_string()])
                    .status()
                    .expect("run cannon_threads");
                assert!(status.success());
            });
            par.push(t);
        }
        let (par_mean, par_stdev) = mean_stdev(&par);
        let (par_min, par_max) = (
            par.iter().cloned().fold(f64::INFINITY, f64::min),
            par.iter().cloned().fold(f64::NEG_INFINITY, f64::max),
        );
        let par_out = count_outliers_3sigma(&par, par_mean, par_stdev);

        let speedup = if par_mean > 0.0 { seq_mean / par_mean } else { 0.0 };

        writeln!(
            f,
            "{},{},{},{},{:.6},{:.6},{:.6},{:.6},{},{:.6},{:.6},{:.6},{:.6},{:.6},{:.6}",
            mode, n, q, p,
            seq_mean, seq_stdev, seq_min, seq_max, seq_out,
            par_mean, par_stdev, par_min, par_max, par_out,
            speedup
        ).unwrap();
    }
}
