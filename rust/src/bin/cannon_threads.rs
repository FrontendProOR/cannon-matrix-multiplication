use rust::*;
use std::env;
use std::sync::{Arc, Barrier};
use std::thread;


fn view<'a>(m: &'a [f64], n: usize, i: usize, j: usize, b: usize) -> Vec<f64> {
    let mut v = vec![0.0; b*b];
    for r in 0..b { let src = (i*b + r)*n + j*b; v[r*b..(r+1)*b].copy_from_slice(&m[src..src+b]); }
    v
}


fn add_mm(c: &mut [f64], a: &[f64], b: &[f64], bsz: usize) {
    for i in 0..bsz { for k in 0..bsz { let aik = a[i*bsz+k]; for j in 0..bsz { c[i*bsz+j]+=aik*b[k*bsz+j]; }}}
}


fn main() {
    let n: usize = env::args().nth(1).expect("n").parse().unwrap();
    let q: usize = env::args().nth(2).expect("q").parse().unwrap();
    let trace: Option<String> = env::args().nth(3);
    assert!(n % q == 0);
    let bsz = n / q;
    let a = Arc::new(gen_matrix(n, 0));
    let b = Arc::new(gen_matrix(n, 1));


    let barrier = Arc::new(Barrier::new(q*q));


    let t = std::time::Instant::now();
    let mut handles = vec![];
    for idx in 0..q*q { let a = a.clone(); let b = b.clone(); let barrier = barrier.clone();
        let trace = trace.clone();
        handles.push(thread::spawn(move || {
            let i = idx / q; let j = idx % q;
            let mut a_j = (j + i) % q; // initial skew A left by i
            let mut b_i = (i + j) % q; // initial skew B up by j
            let mut c_loc = vec![0.0_f64; bsz*bsz];
            for r in 0..q {
                let a_loc = view(&a, n, i, a_j, bsz);
                let b_loc = view(&b, n, b_i, j, bsz);
                add_mm(&mut c_loc, &a_loc, &b_loc, bsz);
                barrier.wait();
                if i==0 && j==0 { if let Some(tp) = &trace { let frob = frob_norm(&c_loc); std::fs::OpenOptions::new().create(true).append(true).open(tp).and_then(|mut f| { use std::io::Write; if r==0 { writeln!(f, "phase,frob_C_loc").ok(); } writeln!(f, "{},{}", r, frob) }).ok(); } }
                a_j = (a_j + q - 1) % q; // left
                b_i = (b_i + q - 1) % q; // up
                barrier.wait();
            }
            (i, j, c_loc)
        }));
    }
    let mut c = vec![0.0_f64; n*n];
    for h in handles { let (i, j, blk) = h.join().unwrap();
        for r in 0..bsz { let dst = (i*bsz + r)*n + j*bsz; c[dst..dst+bsz].copy_from_slice(&blk[r*bsz..(r+1)*bsz]); }
    }
    println!("time_sec={:.6}", t.elapsed().as_secs_f64());
}