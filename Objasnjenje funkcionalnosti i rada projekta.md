# Šta je Cannonov algoritam i čemu služi

Cannonov algoritam je paralelni algoritam za množenje kvadratnih matrica.
Koristi se da se posao ravnomerno raspodeli između više procesora ili niti, tako da svi rade istovremeno i maksimalno iskoriste računarske resurse.

Pojasnjenje:
* Matrice A i B dimenzija N x N se dele na blokove.
    Na primer ako imamo q x q procesora svaka nit ili proces dobija po jedan blok dimenzije (N/q) x (N/q)
* Pre nego sto pocne racunanje matrice se poravnaju ( skew ):
    * Svaka vrsta matrice A se pomera ulevo za i mesta ( gde je redni broj vrste).
    * Svaka kolona matrice B se pomera navise za j mesta ( gde je j redni broj kolone).
* Zatim se u q koraka izvrsava:
    1. Svaki proces racuna proizvod svoga bloka Aij x Bij i dodaje ga svom lokalnom Cij.
    2. Nakon racunanja blok A se rotira ulevo, a blok B navise.
    3. Sinhonrizacija svih procesa( barijera)
* Na kraju blokovi Cij cine globalnu matricu C.
Prednost ovoga: uravnotezuje racun i komunikaciju sto povecava efikasnost.

# Neki od problema koje ovaj projekat obradjuje: 
Jako i Slabo skaliranje

## Jako skaliranje meri koliko algoritam ubrzava kada povećamo broj procesora, a problem ostane isti.
Znači, matrice su uvek iste veličine, ali dodajemo više jezgara i gledamo koliko vreme opada.
Formula S(p) = T1/Tp
Gde bi T1 bilo vreme izvrsavanja na jednom procesoru
a Tp je vreme na p procesora.
Ako je S(p) = p, to znači da je skaliranje idealno (nema gubitaka).
Kod stvarnih sistema, skaliranje je manje zbog sinhronizacije i komunikacionih troškova

## Slabo skaliranje meri koliko algoritam zadržava performanse ako povećavamo i veličinu problema i broj procesora proporcionalno.
Znači, ako dupliramo broj procesora, dupliramo i veličinu matrice tako da svaki procesor ima isti deo posla.
Cilj: da vreme ostane približno isto iako broj procesora raste.
Koristi se za algoritme koji se izvode na velikim sistemima gde problem raste sa brojem resursa

# Sta nam govori Amdahlov zakon
Amdahlov zakon govori koliko maksimal 
no ubrzanje možemo očekivati ako samo deo programa možemo paralelizovati.
Formula je S(p) = 1/( s + (1-s)/p)
* s = deo programa koji mora ostati sekvencijalan npr. 10% => s = 0.1
* p = broj procesora
Čak i ako koristimo beskonačno mnogo procesora, ubrzanje ne može preći 1/s.
To znači da ograničenje dolazi od dela koda koji se ne može paralelizovati

# Gustafsonov zakon
Gustafsonov zakon se koristi u kontekstu slabog skaliranja.
On kaže da ako povećavamo veličinu problema zajedno sa brojem procesora, možemo postići skoro linearno ubrzanje.
Formula: 
S(p) = p-s(p-1)
* s je sekvencijalni deoe koda kao i kod amdahla 
Ako je s vrlo mali( npr. 1% ) tada sa 100 procesora dobijamo ubrzanje skoro 99x
Uglavnom ako problem raste paralelizacija ima smisla.

# Frobeniusova norma matrice meri ukupnu “veličinu” matrice gledano kroz sve njene elemente.
Definiše se kao kvadratni koren zbira kvadrata svih elemenata matrice.
Objasnjenje:
Recimo da je matrica kao tacka u n^2 dimenzionalnom prostoru gde je svaki element matrice jedna kordinata.
Frobeniusova norma je udaljenost te tačke od koordinatnog početka.
Zato se koristi kao skalarni rezime stanja matrice, veća norma znači da matrica ima veće vrednosti elemenata, manja norma da su elementi bliži nuli.
U mom projektu se Frobeniusova norma matrice C koristi se za praćenje napretka izračunavanja tokom množenja matrica.(merenje ukupne energije ili jacine matrice, stabilna i laka za izracunavanje je se samo sabiralo i korenovalo, pratimo konvergenciju i dinamiku izracunavanja izmedju sekvencijane i paralelne verzije algoritma)

# Podatci sistema na kom se testiralo
RAM 16 GB DDR4 3200 Mt/s
AMD Ryzen 7 5800U with Radeon Graphics Cores 8 Threads 16
( iz nekog razloga sam do sad mislio da ima samo 4 jer sam radio prvo na desktop verziji starog amd procesora ryzen 5 2400g koji ima 4 jezgra ali rezultai su uglavnom sa procesora od laptopa 1,2,4 a mogao sam i 2,4,8 al eto mrsko mi sve pokretati opet i generisati grafike)
Integrated Ryzen graphics  500MB
neki nepoznat stock SSD 512GB

# Slikovitmo objasnjenje rada Kanonovog algoritma mnozenja matrica 
Cannon algoritam ukratko kako funkcionise slikovito:
Ima koraka koliko je koren od recimo P tj. za matrice od koren od 9 ima 3 koraka
korak 0:
* Cirkularno smenjuje se pozicija koridnata ( brojeva ili blokova ili celija stagod Aij ) prema i-tom redu u matrici A blokovi za poziciju u levu stranu a pozicija se mnozi sa brojem u kom je redu.
* dok se kod matrice B pomeraju blokovi na gore za broj pozicija po tome u kom je indeksnom redu 
korak 1
* matrica Cij svaki proceesor Pij lokalno  azurira (dodaje) matricu Cij u paraleli i na taj nacin A10 i B02 postaju C12 koji je zapravo P12
korak 2 
nakon ovoga opet premestanje 
* pozicija matrice A(levo) i B (na gore) samo sto ovaj put je za sve po jedno mesto premestanje i za A i B znaci jednom u levo A i jednom na gore B
* nakon toga opet update C matricu paralelno od strane svako procesora
i nakon ovoga C ima svoj finalnu verziju
koju mozda zapisemo u neku finalnu promenjivu ili mozemo koristiti samo C ja sam C koristio samo tj. ABC i to je to radi razumevanja algoritma moze se koristiti ABC i finalna matrica P recimo
Video uglavnom ja sam samo naveo pomeranje a unutar samog ovoga se radi mnozenje svega unutar celija tj. blokova pojedinacno po koridnati.

* Uglavnom imam matrice sa nekim brojevima A i B onda se ispomeraju pozicije za A po broju redova u levo tj. i dok se za B pomere pozicije za broj kolona na gore, onda se to izmnozi i azurira u C i prelazi u naredno pomeranje za po jednu poziciju A i B po svom pravcu i onda opet mnozenje i azuriranje u C matricu i to je to.
C = C1 + C2
Nakon poravnanja prvog koraka svaki element kordinata se pomera samo za jednu poziciju mnoze se i sabiraju za kasnije c1,c2,c3,c4
https://www.youtube.com/watch?v=olIEHFK_RzM
https://www.youtube.com/watch?v=6r6uPImUUBQ
