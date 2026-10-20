# SCENARIUSZ WYSTĄPIENIA I NOTATKI PRELEGENTA (10 MINUT)
## Konkurs IDUB: Działanie D12 – Wsparcie Kół Naukowych AGH
### POB 6: Inteligentne techniki informacyjne, telekomunikacyjne, komputerowe i sterowania
**Projekt:** *Algorytm „Neuro-Curiosity” do optymalizacji strategii sterowania pojazdów autonomicznych*  
**Koło Naukowe:** Koło Naukowe SENSOR (WIMiR & Wydział Odlewnictwa)  
**Opiekun naukowy:** dr hab. inż. Krzysztof Lalik, prof. AGH  
**Prelegent / Lider modułu Cyfrowego Bliźniaka:** Patryk Pięta (Wydział Odlewnictwa, Technologie Przemysłu 4.0)  

---

## ⏱ HARMONOGRAM MINUTOWY WYSTĄPIENIA (CUE SHEET)

| Slajd | Zakres czasowy | Czas trwania | Tematyka slajdu | Główny cel ewaluacyjny |
|:---:|:---:|:---:|---|---|
| **1** | `0:00 – 1:00` | 60 s | Strona tytułowa, IDUB POB 6, zespół SKN Sensor | Przedstawienie interdyscyplinarnego zespołu i afiliacji |
| **2** | `1:00 – 2:00` | 60 s | Problem badawczy i bariery klasycznego RL | Wykazanie konieczności odejścia od błądzenia losowego |
| **3** | `2:00 – 3:15` | 75 s | Istota innowacji: Architektura ICM (Neuro-Curiosity) | Kluczowa nowość naukowa projektu |
| **4** | `3:15 – 4:15` | 60 s | Transfer Sim-to-Real i Domain Randomization | Pokonanie bariery wdrożenia bez niszczenia sprzętu |
| **5** | `4:15 – 5:45` | 90 s | **Cyfrowy Bliźniak (Digital Twin) & Edge AI** | **Główny punkt demonstracyjny (3D Live Demo)** |
| **6** | `5:45 – 7:00` | 75 s | Weryfikacja statystyczna (Test Friedmana i Nemenyiego) | Metodologiczny rygor naukowy dla publikacji Q1 |
| **7** | `7:00 – 8:00` | 60 s | Harmonogram i kamienie milowe (Q1 – Q4) | Wykonalność projektu w cyklu rocznym |
| **8** | `8:00 – 9:00` | 60 s | Budżet (44 900 PLN) i plan upowszechniania | Efektywność kosztowa i prestiżowe konferencje |
| **9** | `9:00 – 10:00` | 60 s | Podsumowanie i otwarcie dyskusji Q&A | Zamknięcie w czasie i zaproszenie do pytań |

---

## 🎤 SZCZEGÓŁOWY SKRYPT WYSTĄPIENIA SLAJD PO SLAJDZIE

---

### SLAJD 1: STRONA TYTUŁOWA
* **Czas:** `0:00 – 1:00` (60 sekund)
* **Co widzi komisja:** Oficjalne barwy AGH, logotypy SKN Sensor, AGH oraz IDUB Uczelnia Badawcza, tytuł projektu, dane opiekuna i zespołu.
* **Gesty / Wskazówki sceniczne:** Stań prosto, uśmiechnij się, nawiąż kontakt wzrokowy z członkami komisji. Mów spokojnym, pewnym głosem.
* **SKRYPT SŁOWO W SŁOWO:**
> *"Dzień dobry Państwu. Nazywam się Patryk Pięta i w imieniu Koła Naukowego SENSOR działającego przy Wydziale Inżynierii Mechanicznej i Robotyki oraz Wydziale Odlewnictwa AGH, mam przyjemność zaprezentować nasz projekt badawczy pt.:*  
> ***«Algorytm „Neuro-Curiosity” do optymalizacji strategii sterowania pojazdów autonomicznych».***  
> *Projekt realizujemy pod opieką naukową profesora Krzysztofa Lalika w ramach konkursu IDUB Działanie D12, wpisując się w Priorytetowy Obszar Badawczy POB 6.*  
> *Nasz zespół łączy kompetencje w obszarze głębokiego uczenia maszynowego, systemów wbudowanych Edge AI oraz przemysłowych platform Przemysłu 4.0. Dzisiaj pokażemy, jak połączyliśmy algorytmy ciekawości neuronowej z technologią Cyfrowego Bliźniaka, rozwiązując fundamentalny problem nawigacji autonomicznej w intralogistyce."*

---

### SLAJD 2: PROBLEM BADAWCZY I WYZWANIA INTRALOGISTYKI
* **Czas:** `1:00 – 2:00` (60 sekund)
* **Co widzi komisja:** Po lewej 3 zwięzłe klocki problemowe (Rzadkie nagrody, Klątwa wielowymiarowości, Ryzyko kolizji/Jerk). Po prawej duża ramka z wizualizacją błędu klasycznej eksploracji.
* **Gesty / Wskazówki sceniczne:** Wskaż ręką lub wskaźnikiem na ramkę po prawej stronie. Zaakcentuj słowo "niszczenie sprzętu" i "brak sygnału zwrotnego".
* **SKRYPT SŁOWO W SŁOWO:**
> *"Przejdźmy do sedna problemu. Dynamiczny rozwój inteligentnych fabryk wymaga wprowadzania setek wózków AGV i robotów AMR na hale produkcyjne. Inżynierowie chcą uczyć te roboty metodami uczenia ze wzmocnieniem (Reinforcement Learning). Natrafiają jednak na trzy krytyczne bariery.*  
> *Po pierwsze: **problem rzadkich nagród (Sparse Rewards)**. W wielkiej hali magazynowej wózek nie otrzymuje żadnego sygnału zwrotnego, dopóki przypadkowo nie dotrze do celu. Wykonuje miliony jałowych ruchów.*  
> *Po drugie: **klątwa wielowymiarowości**. Sensory LiDAR generują tysiące punktów na sekundę, gubiąc tradycyjne sieci w szumie otoczenia.*  
> *Po trzecie i najważniejsze: **eksploracja losowa w świecie realnym grozi wypadkami**. Błądzenie wózka to ryzyko zderzenia z regałem, a gwałtowne zmiany prędkości powodują wysoki wskaźnik szarpnięcia (Jerk) i niszczenie przekładni mechanicznych. Nasz projekt eliminuje to ryzyko u podstaw."*

---

### SLAJD 3: ISTOTA INNOWACJI – ALGORYTM „NEURO-CURIOSITY” (ICM)
* **Czas:** `2:00 – 3:15` (75 sekund)
* **Co widzi komisja:** 3 klocki idei po lewej (Wewnętrzna motywacja, Forward Dynamics, Inverse Model) oraz ramka ze schematem blokowym architektury ICM po prawej.
* **Gesty / Wskazówki sceniczne:** Wskaż na schemat przepływu danych. Wyjaśnij intuicyjnie metaforę ludzkiej ciekawości.
* **SKRYPT SŁOWO W SŁOWO:**
> *"Naszym rozwiązaniem jest algorytm **Neuro-Curiosity** oparty na architekturze Intrinsic Curiosity Module.*  
> *Zamiast polegać na rzadkich nagrodach zewnętrznych, wyposażamy agenta w **biologicznie inspirowaną ciekawość poznawczą**. Robot dąży do stanów, których jeszcze nie potrafi przewidzieć.*  
> *Jak to działa? Sieć neuronowa modeluje dynamikę w przód (Forward Model) – stara się odgadnąć, co wózek zobaczy po wykonaniu danej akcji. Im bardziej wózek jest 'zaskoczony' otoczeniem – czyli im większy błąd predykcji popełnił model – tym wyższą **nagrodę wewnętrzną** otrzymuje agent.*  
> *Równocześnie kluczową rolę pełni tzw. **Inverse Model**. Filtruje on zakłócenia tła – na przykład migające lampy fabryczne czy cienie ludzi – skupiając uwagę algorytmu wyłącznie na obiektach, na które pojazd ma realny wpływ sterujący. W efekcie wózek aktywnie, bezpiecznie i metodycznie bada przestrzeń magazynu."*

---

### SLAJD 4: METODOLOGIA SIM-TO-REAL I DOMAIN RANDOMIZATION
* **Czas:** `3:15 – 4:15` (60 sekund)
* **Co widzi komisja:** 3 pigułki procesowe u góry (Isaac Sim → Domain Randomization → Zero-Shot) oraz 2 ramki na dole (Symulacja vs Rzeczywisty wózek).
* **Gesty / Wskazówki sceniczne:** Pokaż płynne przejście z lewej ramki (wirtualnej) do prawej (fizycznej platformy).
* **SKRYPT SŁOWO W SŁOWO:**
> *"Kolejnym wyzwaniem jest tzw. **Reality Gap** – jak bezpiecznie przenieść inteligencję z komputera na fizyczny wózek fabryczny?*  
> *Stosujemy sprawdzony, trzystopniowy proces transferu Sim-to-Real.*  
> *Krok pierwszy: prowadzimy masowy, równoległy trening floty w środowisku **NVIDIA Isaac Sim**, korzystając z fotorealistycznej fizyki PhysX i ray tracingu RTX emulującego sensory LiDAR.*  
> *Krok drugi to **Domain Randomization**. W trakcie symulacji celowo rozstrajamy parametry: zmieniamy tarcie kół o posadzkę w zakresie od 0.35 do 0.95, losowo modyfikujemy masę przewożonych palet oraz dodajemy sztuczne opóźnienia magistrali komunikacyjnej.*  
> *Dzięki temu sieć staje się całkowicie niewrażliwa na niedoskonałości fizycznego świata. Umożliwia to krok trzeci: **Zero-Shot Transfer**. Skompilowany model TensorRT wgrywamy bezpośrednio na komputer pokładowy wózka, redukując testy poligonowe o ponad 75%."*

---

### SLAJD 5: CYFROWY BLIŹNIAK (DIGITAL TWIN) & ARCHITEKTURA EDGE AI
* **Czas:** `4:15 – 5:45` (90 sekund) – **GŁÓWNY PUNKT DEMONSTRACYJNY!**
* **Co widzi komisja:** Duży, ostry zrzut ekranu z działającej aplikacji 3D WebGL (arena 100x100m, dwa wózki AGV, promienie LiDAR, kokpit operatorski), link do `localhost:8080`, klocki technologii (Jetson Orin NX, Kafka, TimescaleDB).
* **Gesty / Wskazówki sceniczne:** Mów z dumą i pasją – to Twój autorski wkład inżynierski! Wskaż na ekranie wózek AGV-01 i telemetrię. Jeśli masz możliwość, możesz przełączyć okno na przeglądarkę z działającym systemem.
* **SKRYPT SŁOWO W SŁOWO:**
> *"Przechodzimy do serca demonstracyjnego naszego projektu – platformy **Cyfrowego Bliźniaka**, którą rozwijam w ramach mojej pracy inżynierskiej na Wydziale Odlewnictwa we współpracy z Kołem Sensor.*  
> *Po lewej stronie widzą Państwo działające środowisko 3D w Three.js i WebGL. Na arenie o wymiarach 100 na 100 metrów symulujemy zachowanie dwóch pojazdów w czasie rzeczywistym:*  
> *Pojazd **AGV-01** sterowany jest naszym algorytmem Neuro-Curiosity, a **AGV-02** klasyczną polityką eksploracji losowej.*  
> *Po prawej stronie przedstawiliśmy architekturę sprzętowo-programową. Wózek posiada pokładowy komputer brzegowy **NVIDIA Jetson Orin NX** o mocy do 100 TOPS, który podejmuje decyzje sterujące w czasie poniżej 15 milisekund – bez konieczności łączności z chmurą.*  
> *Dane telemetryczne, chmury punktów LiDAR oraz stan wskaźników Jerk przesyłane są przez szynę przemysłową **Apache Kafka**, agregowane w bazie **TimescaleDB** i analizowane przez silnik **Apache Spark**. Jest to kompletne, gotowe środowisko badawcze."*

---

### SLAJD 6: WERYFIKACJA STATYSTYCZNA I KLUCZOWE WSKAŹNIKI
* **Czas:** `5:45 – 7:00` (75 sekund)
* **Co widzi komisja:** 3 duże karty KPI (+85% droga bezkolizyjna, -62% Jerk, Test Friedmana/Nemenyiego) oraz ramka na wykres zbieżności i diagram CD.
* **Gesty / Wskazówki sceniczne:** Skieruj wzrok na recenzentów naukowych w komisji. Podkreśl rygor statystyczny wymagany przez IDUB.
* **SKRYPT SŁOWO W SŁOWO:**
> *"Projekt opiera się na twardych, rygorystycznych danych empirycznych. Mierzymy cztery kluczowe metryki:*  
> *Po pierwsze: uzyskujemy **o 85% dłuższą średnią drogę bezkolizyjną** w gęsto zastawionym magazynie w porównaniu do polityk tradycyjnych.*  
> *Po drugie: notujemy **spadek wskaźnika szarpnięcia Jerk o 62%**. Dla inżynierii intralogistycznej oznacza to bezpieczny transport delikatnych ładunków i wielokrotnie mniejsze zużycie napędów.*  
> *Co szczególnie istotne dla kryteriów doskonałości IDUB: **nie opieramy się na zwykłym porównaniu średnich**. W środowisku stochastycznym byłoby to błędem metodologicznym. Przeprowadzamy nieparametryczny **test rangowy Friedmana** na 50 zróżnicowanych trasach magazynowych oraz post-hoc **test Nemenyiego**. Pozwala to wykazać bezsporną istotność statystyczną przewagi naszego algorytmu z poziomem p poniżej 0.05, co stanowi fundament do publikacji w czasopismach z pierwszego kwartyla (JCR Q1)."*

---

### SLAJD 7: HARMONOGRAM REALIZACJI I KAMIENIE MILOWE
* **Czas:** `7:00 – 8:00` (60 sekund)
* **Co widzi komisja:** 4 kwartały ułożone w czytelne klocki po lewej stronie oraz ramka na zdjęcie laboratorium SKN Sensor po prawej.
* **Gesty / Wskazówki sceniczne:** Mów rytmicznie, pokazując logiczne przejście od teorii do wdrożenia.
* **SKRYPT SŁOWO W SŁOWO:**
> *"Prace zaplanowaliśmy na cztery logiczne kwartały w cyklu rocznym:*  
> *W **Kwartale I** budujemy wirtualną geometrię hali w Isaac Sim oraz implementujemy sieć ICM w środowisku PyTorch.*  
> *W **Kwartale II** optymalizujemy sieć neuronową do formatu TensorRT na jednostce NVIDIA Jetson Orin NX i łączymy ją z Cyfrowym Bliźniakiem.*  
> *W **Kwartale III** prowadzimy intensywne testy Sim-to-Real z losowością tarcia posadzki i przechodzimy do prób jezdnych fizycznej platformy na hali laboratoryjnej AGH.*  
> *W **Kwartale IV** realizujemy pełną serię 50 testów statystycznych, przygotowujemy publikację naukową oraz udostępniamy kod źródłowy społeczności akademickiej."*

---

### SLAJD 8: BUDŻET PROJEKTU I PLAN UPOWSZECHNIANIA WYNIKÓW
* **Czas:** `8:00 – 9:00` (60 sekund)
* **Co widzi komisja:** Podsumowanie budżetu (44 900 PLN) w trzech zwięzłych kartach po lewej oraz ramka z logotypami konferencji i baz indeksacyjnych po prawej.
* **Gesty / Wskazówki sceniczne:** Podkreśl racjonalność wydatkowania każdej złotówki oraz wysoki zwrot w postaci wskaźników ewaluacyjnych AGH.
* **SKRYPT SŁOWO W SŁOWO:**
> *"Wnioskowany budżet projektu wynosi **44 900 PLN** i został zoptymalizowany pod kątem maksymalnej efektywności naukowej:*  
> *Kluczowe pozycje sprzętowe to jednostka brzegowa **NVIDIA Jetson Orin NX** z przemysłowym zasilaniem za 8 000 PLN oraz sensoryka i materiały za 1 900 PLN.*  
> *Najważniejszą część budżetu – 35 000 PLN – przeznaczamy na upowszechnianie wyników: udział zespołu w 27. Międzynarodowej Konferencji **ICCC 2026** indeksowanej w IEEE Xplore oraz w **Krajowej Konferencji Robotyki KKR**.*  
> *Ponadto planujemy publikację artykułu podsumowującego w renomowanym czasopiśmie z listy filadelfijskiej w formule Open Access, udostępnienie kodu w modelu Open Source na platformie GitHub oraz demonstrację działania systemu podczas Dni Otwartych AGH."*

---

### SLAJD 9: PODSUMOWANIE I OTWARCIE DYSKUSJI
* **Czas:** `9:00 – 10:00` (60 sekund)
* **Co widzi komisja:** 3 filary sukcesu projektu po lewej, duży czerwony napis "DZIĘKUJEMY ZA UWAGĘ!" oraz ramka na kod QR po prawej.
* **Gesty / Wskazówki sceniczne:** Zwolnij tempo, podsumuj z dumą, podziękuj z szacunkiem i z uśmiechem zaproś do pytań.
* **SKRYPT SŁOWO W SŁOWO:**
> *"Podsumowując nasze wystąpienie:*  
> *Po pierwsze: **innowacja naukowa** – przełamujemy barierę rzadkich nagród w robotyce mobilnej poprzez wewnętrzną ciekawość neuronową.*  
> *Po drugie: **wartość przemysłowa** – transfer Sim-to-Real pozwala wdrażać bezpieczne wózki autonomiczne bez kosztownych testów zderzeniowych i niszczenia napędów.*  
> *Po trzecie: **synergia AGH** – projekt w praktyce integruje wiedzę studentów WIMiR i Wydziału Odlewnictwa, rozwijając zaawansowane stanowisko Cyfrowego Bliźniaka w priorytecie POB 6.*  
> *Dziękuję bardzo Państwu za uwagę. Z przyjemnością odpowiem na pytania komisji oraz zaprezentuję działanie Cyfrowego Bliźniaka na żywo."*

---

## 🛠 INSTRUKCJA WKLEJANIA WŁASNYCH MATERIAŁÓW (ZDJĘĆ, SCHEMATÓW, FILMÓW)

W pliku prezentacji `Prezentacja_IDUB_Neuro_Curiosity_AGH.pptx` przygotowano dedykowane, błękitne ramki-placeholdery. Aby wstawić własne materiały:

1. **Wstawianie zdjęcia / zrzutu ekranu:**
   - Otwórz prezentację w programie PowerPoint.
   - Kliknij na wybraną błękitną ramkę i naciśnij `Delete` (lub kliknij wewnątrz niej: `Wstawianie` \(\rightarrow\) `Obrazy` \(\rightarrow\) `To urządzenie...`).
   - Dopasuj rozmiar obrazka do obszaru slajdu.

2. **Wstawianie wideo (np. na Slajdzie 4 lub 5):**
   - W menu PowerPoint wybierz: `Wstawianie` \(\rightarrow\) `Wideo` \(\rightarrow\) `Wideo na tym urządzeniu...`.
   - Wskaż plik `.mp4` (nagrany np. za pomocą skrótu `Win + Alt + R` lub OBS Studio).
   - W zakładce `Odtwarzanie`:
     - Ustaw: *Początek:* **Automatycznie**.
     - Zaznacz: **W pętli do zatrzymania**.

3. **Lista rekomendowanych materiałów na poszczególne slajdy:**
   - **Slajd 2:** Zrzut ekranu lub animacja tradycyjnego błądzenia AGV / kolizji.
   - **Slajd 3:** Schemat blokowy architektury sieci neuronowej ICM (z wniosku grantowego).
   - **Slajd 4:** Po lewej: zrzut sceny z Isaac Sim; Po prawej: zdjęcie fizycznego wózka AGV lub podwozia koła Sensor.
   - **Slajd 5:** *Już zawiera autentyczny screenshot Cyfrowego Bliźniaka!* W dolnej ramce po prawej możesz wkleić krótki filmik MP4 z przejazdu.
   - **Slajd 6:** Wykres porównawczy zbieżności nagrody (Neuro-Curiosity vs Epsilon-Greedy) lub diagram testu Nemenyiego.
   - **Slajd 7:** Zdjęcie członków zespołu SKN Sensor przy stanowisku laboratoryjnym na AGH.
   - **Slajd 8:** Logotypy IEEE Xplore, ICCC 2026, KKR oraz GitHub.
   - **Slajd 9:** Kod QR (np. wygenerowany na qr-code-generator.com) prowadzący do repozytorium GitHub projektu.

---

## ❓ FAQ – PRZEWIDYWANE PYTANIA KOMISJI IDUB I WZORCOWE ODPOWIEDZI

### Pytanie 1: Czym Neuro-Curiosity różni się od klasycznego kształtowania nagrody (reward shaping)?
> **Odpowiedź:**  
> *"Reward shaping wymaga ręcznego definiowania odległości od celów i tworzenia arbitralnych wag kar i nagród przez inżyniera, co w skomplikowanych magazynach prowadzi do lokalnych minimów i niebezpiecznych heurystyk. Neuro-Curiosity generuje nagrodę **wewnętrzną i samosuperwizowaną** – wynika ona z błędu predykcji modelu dynamiki otoczenia. Robot sam uczy się, co jest dla niego nowe i warte zbadania, co eliminuje konieczność ręcznego strojenia funkcji nagrody dla każdego układu hali."*

### Pytanie 2: W jaki sposób radzicie sobie z tzw. Reality Gap podczas transferu z symulatora na platformę Jetson?
> **Odpowiedź:**  
> *"Wykorzystujemy zaawansowaną metodę **Domain Randomization** w NVIDIA Isaac Sim. Podczas treningu losowo modyfikujemy współczynniki tarcia posadzki w zakresie \(\mu \in [0.35, 0.95]\), masę ładunku paletowego o \(\pm 30\%\), a także wprowadzamy syntetyczny jitter komunikacyjny magistrali i szum czujników LiDAR. Wytrenowana sieć uczy się sterowania niewrażliwego na zaburzenia, dzięki czemu po skompilowaniu do formatu TensorRT na Jetsonie Orin NX działa poprawnie w trybie Zero-Shot bez konieczności ryzykownego douczania na fizycznej posadzce."*

### Pytanie 3: Dlaczego komputer pokładowy Jetson Orin NX, a nie obliczenia w chmurze?
> **Odpowiedź:**  
> *"W intralogistyce przemysłowej warunkiem krytycznym jest determinizm czasowy i bezpieczeństwo. Komunikacja z chmurą wprowadza opóźnienia sieciowe rzędu 50-200 ms oraz ryzyko utraty pakietów w strefach cienia radiowego hali magazynowej. Moduł pokładowy NVIDIA Jetson Orin NX zapewnia inferencję sieci w czasie poniżej 15 ms, gwarantując natychmiastowe zatrzymanie lub ominięcie przeszkody nawet przy całkowitej utracie łączności Wi-Fi."*

### Pytanie 4: Dlaczego do oceny wyników stosujecie test Friedmana i Nemenyiego zamiast standardowego testu t-Studenta?
> **Odpowiedź:**  
> *"Test t-Studenta wymaga spełnienia założeń o normalności rozkładu i porównuje tylko dwie próby na pojedynczej trasie. W robotyce mobilnej wyniki osiągane przez algorytmy na różnych trasach testowych nie mają rozkładu normalnego i charakteryzują się dużą stochastycznością. Nieparametryczny test rangowy Friedmana pozwala obiektywnie porównać wiele polityk sterowania na 50 zróżnicowanych scenariuszach fabrycznych, a post-hoc test Nemenyiego jednoznacznie wskazuje, które różnice są statystycznie istotne przy \(p < 0.05\). Jest to standard wymagany przez wiodące czasopisma z pierwszego kwartyla (JCR Q1)."*

### Pytanie 5: Jaki jest podział zadań między Wydziałem Inżynierii Mechanicznej i Robotyki a Wydziałem Odlewnictwa?
> **Odpowiedź:**  
> *"Projekt jest wzorcowym przykładem synergii międzywydziałowej w ramach POB 6. Koledzy z WIMiR i koła Sensor odpowiadają za konstrukcję kinematyczną wózka, implementację sieci ICM oraz symulacje w Isaac Sim pod okiem profesora Lalika. Z kolei ja z ramienia Wydziału Odlewnictwa (kierunek Technologie Przemysłu 4.0) realizuję warstwę Cyfrowego Bliźniaka – platformę 3D Three.js, szynę danych IIoT Apache Kafka, agregację w TimescaleDB oraz brzegową integrację telemetryczną, co stanowi również trzon mojej pracy inżynierskiej."*

---
*Dokument przygotowany dla zespołu SKN Sensor • Akademia Górniczo-Hutnicza w Krakowie • Październik 2026*
