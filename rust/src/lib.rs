use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use std::time::Instant;


pub fn gen_matrix(n: usize, seed: u64) -> Vec<f64> {
    let mut rng = StdRng::seed_from_u64(seed);
    let mut a = vec![0.0_f64; n*n];
    for x in &mut a { *x = rng.random::<f64>(); }
    a
}


pub fn block_mult(a: &[f64], b: &[f64], n: usize, bs: usize, trace: Option<&str>) -> Vec<f64> {
    let mut c = vec![0.0; n*n];
    let mut step: usize = 0;
    if let Some(tp) = trace { std::fs::write(tp, "step,frob_C").ok(); }
    for ii in (0..n).step_by(bs) { for kk in (0..n).step_by(bs) { for jj in (0..n).step_by(bs) {
        for i in ii..(ii+bs) { for k in kk..(kk+bs) { let aik = a[i*n + k];
            for j in jj..(jj+bs) { c[i*n + j] += aik * b[k*n + j]; }}}
        step += 1;
        if step % 10 == 0 { if let Some(tp) = trace { let frob = frob_norm(&c); std::fs::OpenOptions::new().append(true).open(tp).and_then(|mut f| { use std::io::Write; writeln!(f, "{},{}", step, frob) }).ok(); } }
}}}
    if let Some(tp) = trace { let frob = frob_norm(&c); std::fs::OpenOptions::new().append(true).open(tp).and_then(|mut f| { use std::io::Write; writeln!(f, "{},{}", step, frob) }).ok(); }
    c
}


pub fn frob_norm(x: &[f64]) -> f64 { x.iter().map(|v| v*v).sum::<f64>().sqrt() }


pub fn now_sec(f: impl FnOnce() ) -> f64 {
    let t0 = Instant::now(); f(); t0.elapsed().as_secs_f64()
}


pub fn max_abs_diff(a: &[f64], b: &[f64]) -> f64 { a.iter().zip(b).map(|(x,y)| (x-y).abs()).fold(0.0, f64::max) }