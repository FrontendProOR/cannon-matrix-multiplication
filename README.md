# cannon-matrix-multiplication
## Tema
Implementacija Kanonovog algoritma za množenje matrica u Python-u i Rust-u sa ciljem analize performansi i skalabilnosti.

## Za ocenu: 9

## Problem
Dat je problem množenja matrica C = A x B dimenzije N x N. Klasična sekvencijalna složenost je O(N^3). 
### Cilj je:

1. implementirati sekvencijalno rešenje kao baznu referencu

2. implementirati paralelno rešenje koje deli posao preko više jezgara / procesa / niti

3. izmeriti i objasniti skaliranje (jako i slabo)

4. uporediti teorijske maksimume ( Amdal / Gustafson ) sa praktičnim rezultatima

5. opciono vizualizovati rezultate u Rust okruženju

## Metode koje ce biti koriscene:

- Sekvencijalno množenje: blokovski algoritam radi boljeg iskorišćenja memorijske hijerarhije. Jezik: Python i Rust.

- Cannons algoritam: 2D particionisanje N x N matrica na q x q mrežu blokova veličine ( N / q ) x ( N / q ). Početno poravnanje: (i) levlje kružno pomeranje blokova A po redovima za i, (ii) desno kružno pomeranje blokova B po kolonama za j. Zatim sledi q faza: lokalni C += A * B, pa kružna rotacija A ulevo i B nagore unutar mreže. Time se komunikacija/račun raspoređuju uravnoteženo.

- Paralelizacija u Python-u: multiprocessing sa deljenjem blokova kroz shared_memory ili mmap, plus barijere i cevi/queue za sinhronizaciju.

- Paralelizacija u Rust-u: niti ( std::thread ) uz kanale ( std::sync::mpsc ) ili Arc<Mutex<>> za koordinaciju i deljenje blokova.

- Merenje performansi: višestruka ponavljanja, računanje srednje vrednosti, standardne devijacije i outlier analiza. Logovanje u CSV.

###  Skaliranje:

- Jako skaliranje: fiksna veličina problema, menjamo broj jezgara p, posmatramo ubrzanje S(p) = T₁ / Tp.

- Slabo skaliranje: veličina problema proporcionalna p tako da je posao po jegru približno konstantan; merenje S(weak)(p) = T₁ / Tp u skladu sa Gustafsonovim zakonom.

### Teorija:

- Amdalov zakon: S(p) ≤ 1 / ( s + ( 1 − s ) / p ), gde je s sekvencijalna frakcija.

- Gustafsonov zakon: S(p) ≤ p − s * ( p − 1 ).

### Vizualizacija: crtanje grafika u Rust-u uz plotters.

# Beleske za Odbranu:
# Za ocenu (6):
## 0. Priprema okruzenja:
### U root od projekta 
- `cd python`
- `python -m venv .venv` kreiramo virtuelno okruzenje u folderu .venv
- Za Windows PowerShell:
- `. .venv/Scripts/Activate.ps1` aktivira virtuelno okruzenje
- Za Linux/macOS:
- `source .venv/bin/activate` aktivira virtuelno okruzenje
- `pip install -r requirements.txt` skidanje zavisnosti numpy,...

## 1. Smoke Test Sekvencijalne verzije(za 6):
- Terminal komanda: `python cannon_seq.py --n 256 --bs 64`
- Ocekivani rezultat: time_sec=...
- Moj rezultat: time_sec=0.001516
- Uglavnom oko ~0.0015 gore dole +-0.0001s

## 2. Smoke test paralelne verzije + verifikacija
- Terminal komanda: `python cannon_mp.py --n 256 --q 2 --verify`
- Ocekivani rezultat: 
time_sec=...
verify_err=...
ok=True
- Moj rezultat:
time_sec=0.474708
verify_err=0.000e+00,
ok=True
- Uglavnom je time_sec=~0.46 (+-0.01s)

## 3. Brz Strong scaling sanity-check
Terminal komanda: `python bench_py.py --mode strong_py --n 512 --bs 64 --q_list 1,2,4 --reps 5 --out ../data/logs/strong_py_quick.csv`
- Rezultat u fajlu:` data/logs/strong_py_quick.csv `
- heder sadrži:
- mode,N,q,p,seq_mean,seq_stdev,par_mean,par_stdev,speedup,used_samples
- speedup raste otprilike sa p=1,4,16

## 4. Brz Weak scaling sanity-check
Terminal komanda: `python bench_py.py --mode weak_py --bs 64 --q_list 1,2,4 --reps 5 --out ../data/logs/weak_py_quick.csv`
- Rezultat u fajlu: `data/logs/weak_py_quick.csv`

## 5. Generisanje traga promena stanja
- `python cannon_seq.py --n 256 --bs 64 --trace ../data/logs/trace_seq_py.csv`
- time_sec=0.018640
- `python cannon_mp.py  --n 256 --q 2 --trace ../data/logs/trace_mp_py.csv`
- time_sec=0.475360
### CSV fajlovi:
- trace_seq_py.csv: step,frob_C

- trace_mp_py.csv: phase,worker_idx,frob_C_loc

# Za ocenu (7):
## 1) Build okruženja

- Kompajliranje u release modu

- Terminal Komanda:
`
cargo clean
`
,
`
cargo build --release
`

- Očekivani izlaz:
Finished 'release' profile ... itd.

## 2) Sekvencijalno množenje vreme izvršavanja

1. Pokretanje sekvencijalne verzije

- Terminal Komanda:
`
./target/release/cannon_seq 1024 128
`

(format i parametri: `cannon_seq N BS`)

- Očekivani izlaz:
`
time_sec=0.XXXXX
`
- Moj rezultat: time_sec=0.286605
***
2. Sekvencijalno sa trace (fajl promena stanja)

- Terminal Komanda:
`
./target/release/cannon_seq 512 128 ../data/logs/trace_seq_rs.csv
`

- Očekivani izlaz:
`
time_sec=0.XXXXX
`
- Moj rezultat: time_sec=0.037944

- i kreiran fajl `../data/logs/trace_seq_rs.csv` sa zaglavljem:
`
step,frob_C
`

i više redova sa numeričkim vrednostima.

- Moj rezultat je u fajlu sa putanjom: `../data/logs/trace_seq_rs.csv `

## 3) Paralelno množenje ( threads) vreme izvršavanja

### 1. Pokretanje paralelne verzije za više q (Ryzen 7 5800U → koristi q=1,2,4)

- Terminal Komanda (q=1):
`
./target/release/cannon_threads 1024 1
`

(format: `cannon_threads N Q`, broj niti je p = Q*Q)

- Očekivani izlaz:

time_sec=0.XXXXX


- Moj rezultat: time_sec=0.259688
***
- Terminal Komanda (q=2):
`
./target/release/cannon_threads 1024 2
`

- Očekivani izlaz: time_sec=0.XXXXX


- Moj rezultat: time_sec=0.082388 prvi put ovo je outlier
ovo je kasnije pet puta 
time_sec=0.155444
***
- Terminal Komanda (q=4):
`
./target/release/cannon_threads 1024 4
`

- Očekivani izlaz: time_sec=0.XXXXX


- Moj rezultat: time_sec=0.126123

### 2. Paralelno sa trace (fajl promena stanja po fazama)

- Terminal Komanda:
`
./target/release/cannon_threads 512 2 ../data/logs/trace_mp_rs.csv
`

- Očekivani izlaz: time_sec=0.XXXXX
- Moj rezultat: time_sec=0.014810

i kreiran fajl `../data/logs/trace_mp_rs.csv` sa zaglavljem:
`
phase,frob_C_loc
`

i više redova sa numeričkim vrednostima.

Moj rezultat je u fajlu sa putanjom: `../data/logs/trace_mp_rs.csv`

## 4) Brzi uporedni benchmark CSV

### Jako skaliranje Rust (q=1,2,4)

- Terminal Komanda(deo sa 1,2,4 je koliko je q tj. jezgra ili koliko fizickih core-ova, N broj redova i kolona):
`
./target/release/bench_rs strong_rs 1,2,4 1024 128 ../data/logs/strong_rs_quick.csv
`

(format: `bench_rs strong_rs Q_LIST N BS OUT_CSV`)

### Očekivani izlaz:

Kreira CSV `../data/logs/strong_rs_quick.csv` sa zaglavljem:
`
mode,N,q,p,seq_mean,par_mean,speedup
`

i redovima sa numerikom.

- Moj rezultat je u fajlu sa putanjom:` ../data/logs/strong_rs_quick.csv`
- q=1 -> `time_sec=0.235677`
- q=2 -> `time_sec=0.074133`
- q=4 -> `time_sec=0.105194`

### Slabo skaliranje Rust (q=1,2,4)

- Terminal Komanda ( 3 parametar q se pise jedna cifra 1,2,3 koliko jezgara):
`
./target/release/bench_rs weak_rs 1,2,4 1024 128 ../data/logs/weak_rs_quick.csv
`

### Očekivani izlaz:

Kreira CSV `../data/logs/weak_rs_quick.csv` sa 
zaglavljem:

`
mode,N,q,p,seq_mean,par_mean,speedup
`

- Moj rezultat je u fajlu sa putanjom:` ../data/logs/weak_rs_quick.csv`
- q=1 -> `time_sec=0.004950`
- q=2 -> `time_sec=0.012934`
- q=4 -> `time_sec=0.123387`

# Za ocenu (9)
### Terminal komande za testiranje:
`
cargo build --release
`
***
- Komanda za strong:
`
./target/release/bench_rs strong_rs 1,2,4 1024 128 30 ../data/logs/strong_rs.csv
`
- Rezultati u `../data/logs/strong_rs.csv`
- U terminalu:
`time_sec=0.589572`   
`time_sec=0.584396`   
`time_sec=0.656565`   
`time_sec=0.594633`   
`time_sec=0.550159`   
od nekih pola je trostruko smanjeno vreme ovako 30 puta
***
- Komanda za weak:
`
./target/release/bench_rs weak_rs   1,2,4 1024 128 30 ../data/logs/weak_rs.csv
`
- Rezultati u ../data/logs/weak_rs.csv 
- U terminalu:
`time_sec=0.067304`
`time_sec=0.068339`
`time_sec=0.066087`
`time_sec=0.064980`
`time_sec=0.068660`
ovako 30 puta od pola je duplo krace vreme