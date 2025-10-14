use rust::*;
use std::env; use std::fs::{create_dir_all, File}; use std::io::Write;

fn main(){
    let mode = env::args().nth(1).expect("mode strong_rs|weak_rs");
    let q_list: Vec<usize> = env::args().nth(2).unwrap_or("1,2,4".into()).split(',').map(|s| s.parse().unwrap()).collect();
    let n: usize = env::args().nth(3).unwrap_or("1024".into()).parse().unwrap();
    let bs: usize = env::args().nth(4).unwrap_or("128".into()).parse().unwrap();
    let out = env::args().nth(5).unwrap_or("../data/logs/bench_rs.csv".into());

    create_dir_all("../data/logs").ok();
    let mut f = File::create(out).unwrap();
    writeln!(f, "mode,N,q,p,seq_mean,par_mean,speedup").unwrap();


    if mode=="strong_rs" {
        for &q in &q_list {
            let t_seq = now_sec(||{ let _= block_mult(&gen_matrix(n,0), &gen_matrix(n,1), n, bs, None); });
            let t_par = now_sec(||{ std::process::Command::new(std::env::current_exe().unwrap().with_file_name("cannon_threads")).args([n.to_string(), q.to_string()]).status().unwrap(); });
            let s = t_seq / t_par.max(1e-12);
            writeln!(f, "strong,{},{},{},{:.6},{:.6},{:.6}", n,q,q*q,t_seq,t_par,s).unwrap();
        }
    } else {
        let base_b = bs*2;
        for &q in &q_list {
            let nn = base_b*q;
            let t_seq = now_sec(||{ let _= block_mult(&gen_matrix(nn,0), &gen_matrix(nn,1), nn, bs, None); });
            let t_par = now_sec(||{ std::process::Command::new(std::env::current_exe().unwrap().with_file_name("cannon_threads")).args([nn.to_string(), q.to_string()]).status().unwrap(); });
            let s = t_seq / t_par.max(1e-12);
            writeln!(f, "weak,{},{},{},{:.6},{:.6},{:.6}", nn,q,q*q,t_seq,t_par,s).unwrap();
        }
    }
}