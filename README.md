# cannon-matrix-multiplication
## Tema
Implementacija Kanonovog algoritma za množenje matrica u Python-u i Rust-u sa ciljem analize performansi i skalabilnosti.

## Za ocenu: 10

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