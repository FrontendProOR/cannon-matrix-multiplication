use rust::*;
use std::env;


fn main() {
let n: usize = env::args().nth(1).expect("n").parse().unwrap();
let bs: usize = env::args().nth(2).unwrap_or("128".into()).parse().unwrap();
let trace: Option<String> = env::args().nth(3);
let a = gen_matrix(n, 0);
let b = gen_matrix(n, 1);
let t = now_sec(|| { let _c = block_mult(&a, &b, n, bs, trace.as_deref()); });
println!("time_sec={:.6}", t);
}