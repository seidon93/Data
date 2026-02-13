"""
Financial Controlling Dataset Generator
========================================
Generates a comprehensive, realistic financial dataset for controlling purposes.
Covers: transactions, cost centers, projects, profit centers, regions, branches,
employees (HR), products, customers, suppliers, sales, purchases, production,
cash flow, budgets, and payroll.

Output: CSV files in ./financial_dataset/
"""

import os
import random
import datetime
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker('cs_CZ')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'financial_dataset')
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATE_START = datetime.date(2023, 1, 1)
DATE_END = datetime.date(2025, 12, 31)
TOTAL_DAYS = (DATE_END - DATE_START).days + 1

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_dates(n, start=DATE_START, end=DATE_END):
    days = np.random.randint(0, (end - start).days + 1, size=n)
    return [start + datetime.timedelta(int(d)) for d in days]

def seasonal_dates(n, start=DATE_START, end=DATE_END):
    """Generate dates with seasonal bias (more in Q4, less in Q1)."""
    total = (end - start).days + 1
    weights = []
    for d in range(total):
        dt = start + datetime.timedelta(d)
        month = dt.month
        if month in (10, 11, 12):
            w = 1.6
        elif month in (7, 8, 9):
            w = 1.1
        elif month in (4, 5, 6):
            w = 1.0
        else:
            w = 0.7
        weights.append(w)
    weights = np.array(weights)
    weights /= weights.sum()
    days = np.random.choice(total, size=n, p=weights)
    return [start + datetime.timedelta(int(d)) for d in days]

def save(df, name):
    path = os.path.join(OUTPUT_DIR, name)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    print(f"  ✓ {name}: {len(df):>10,} rows, {len(df.columns):>3} cols")
    return df

# ============================================================
# 1. DIMENSION TABLES
# ============================================================

def gen_regiony():
    data = [
        ('REG01', 'Praha', 'CZ'), ('REG02', 'Středočeský', 'CZ'),
        ('REG03', 'Jihomoravský', 'CZ'), ('REG04', 'Moravskoslezský', 'CZ'),
        ('REG05', 'Plzeňský', 'CZ'), ('REG06', 'Královéhradecký', 'CZ'),
        ('REG07', 'Olomoucký', 'CZ'), ('REG08', 'Liberecký', 'CZ'),
        ('REG09', 'Bratislava', 'SK'), ('REG10', 'Wien', 'AT'),
    ]
    return save(pd.DataFrame(data, columns=['region_id','region_nazev','zeme']), 'dim_regiony.csv')

def gen_pobocky(regiony):
    rows = []
    mesta = {
        'REG01': ['Praha 1','Praha 4','Praha 8'],
        'REG02': ['Kladno','Mladá Boleslav','Kolín'],
        'REG03': ['Brno-střed','Brno-sever','Znojmo'],
        'REG04': ['Ostrava','Frýdek-Místek','Opava'],
        'REG05': ['Plzeň','Klatovy','Rokycany'],
        'REG06': ['Hradec Králové','Trutnov','Náchod'],
        'REG07': ['Olomouc','Přerov','Šumperk'],
        'REG08': ['Liberec','Jablonec','Česká Lípa'],
        'REG09': ['Bratislava I','Bratislava III','Pezinok'],
        'REG10': ['Wien Zentrum','Wien Nord','Wien Süd'],
    }
    for i, (rid, cities) in enumerate(mesta.items()):
        for j, city in enumerate(cities):
            pid = f'POB{i*3+j+1:02d}'
            rows.append((pid, f'Pobočka {city}', fake.street_address(), city, rid,
                          random.choice(['aktivní','aktivní','aktivní','plánovaná'])))
    return save(pd.DataFrame(rows, columns=['pobocka_id','pobocka_nazev','adresa','mesto','region_id','stav']),
                'dim_pobocky.csv')

def gen_strediska(pobocky):
    typy = ['Výroba','Obchod','Administrativa','IT','Logistika','Finance','Marketing','HR','Kvalita','R&D']
    rows = []
    for i in range(50):
        sid = f'STR{i+1:03d}'
        typ = typy[i % len(typy)]
        parent = f'STR{random.randint(1, max(1, i)):03d}' if i > 0 else None
        pob = random.choice(pobocky['pobocka_id'].tolist())
        rows.append((sid, f'{typ} - oddělení {i+1}', typ, parent, pob,
                      random.choice(['aktivní','aktivní','neaktivní'])))
    return save(pd.DataFrame(rows, columns=['stredisko_id','stredisko_nazev','typ','nadrazene_stredisko','pobocka_id','stav']),
                'dim_strediska.csv')

def gen_profit_centra(regiony):
    rows = []
    nazvy = ['Retail CZ','Wholesale CZ','E-commerce','B2B International','Services CZ',
             'Retail SK','Manufacturing','Consulting','Logistics','Financial Services',
             'IT Solutions','Custom Products','Maintenance','After-sales','Export EU',
             'Government','Energy','Healthcare','Automotive','Ostatní']
    for i in range(20):
        rows.append((f'PC{i+1:02d}', nazvy[i], random.choice(regiony['region_id'].tolist()),
                      fake.name(), random.choice(['aktivní','aktivní','neaktivní']),
                      round(random.uniform(500000, 50000000), 2)))
    return save(pd.DataFrame(rows, columns=['profit_centrum_id','nazev','region_id','manazer','stav','rocni_cil']),
                'dim_profit_centra.csv')

def gen_projekty():
    stavy = ['Plánovaný','Aktivní','Aktivní','Aktivní','Pozastavený','Dokončený','Zrušený']
    rows = []
    for i in range(100):
        start = DATE_START + datetime.timedelta(random.randint(0, 800))
        end = start + datetime.timedelta(random.randint(30, 730))
        rows.append((f'PROJ{i+1:03d}', fake.catch_phrase()[:50], random.choice(stavy),
                      round(random.uniform(50000, 5000000), 2), start, end,
                      random.choice(['Interní','Zákaznický','R&D','Investiční','Údržba'])))
    return save(pd.DataFrame(rows, columns=['projekt_id','projekt_nazev','stav','rozpocet','datum_zahajeni','datum_ukonceni','typ']),
                'dim_projekty.csv')

def gen_ucty():
    """Generates a chart of accounts (účtový rozvrh) – Czech accounting standard."""
    groups = [
        # (range_start, count, prefix, name_template, typ, skupina)
        (11, 5, '0', 'DNM - {}', 'Aktiva', 'Dlouhodobý nehmotný majetek'),
        (21, 8, '0', 'DHM - {}', 'Aktiva', 'Dlouhodobý hmotný majetek'),
        (31, 5, '0', 'DFM - {}', 'Aktiva', 'Dlouhodobý finanční majetek'),
        (41, 3, '0', 'Oprávky DNM - {}', 'Aktiva', 'Oprávky k DNM'),
        (51, 5, '0', 'Oprávky DHM - {}', 'Aktiva', 'Oprávky k DHM'),
        (111, 5, '1', 'Materiál - {}', 'Aktiva', 'Zásoby materiálu'),
        (121, 5, '1', 'Nedokončená výroba - {}', 'Aktiva', 'Zásoby NV'),
        (131, 5, '1', 'Výrobky - {}', 'Aktiva', 'Zásoby výrobků'),
        (211, 3, '2', 'Pokladna {}', 'Aktiva', 'Finanční účty'),
        (221, 5, '2', 'Bankovní účet {}', 'Aktiva', 'Finanční účty'),
        (231, 2, '2', 'Krátkodobý úvěr {}', 'Pasiva', 'Finanční účty'),
        (311, 5, '3', 'Pohledávky {}', 'Aktiva', 'Pohledávky'),
        (321, 5, '3', 'Závazky {}', 'Pasiva', 'Závazky'),
        (331, 3, '3', 'Zaměstnanci {}', 'Pasiva', 'Zúčtování se zaměstnanci'),
        (341, 3, '3', 'Daňové záv./pohl. {}', 'Pasiva', 'Daně'),
        (343, 2, '3', 'DPH {}', 'Pasiva', 'Daně'),
        (361, 3, '3', 'Jiné závazky {}', 'Pasiva', 'Ostatní závazky'),
        (381, 5, '3', 'Časové rozlišení {}', 'Aktiva', 'Přechodné účty'),
        (411, 3, '4', 'Základní kapitál {}', 'Pasiva', 'Vlastní kapitál'),
        (421, 3, '4', 'Rezervní fond {}', 'Pasiva', 'Fondy'),
        (431, 2, '4', 'HV {}', 'Pasiva', 'Výsledek hospodaření'),
        (451, 3, '4', 'Rezervy {}', 'Pasiva', 'Rezervy'),
        (461, 3, '4', 'Dlouhodobé závazky {}', 'Pasiva', 'Dlouhodobé závazky'),
        (501, 8, '5', 'Spotřeba {}', 'Náklady', 'Spotřebované nákupy'),
        (511, 5, '5', 'Služby {}', 'Náklady', 'Služby'),
        (521, 5, '5', 'Osobní náklady {}', 'Náklady', 'Osobní náklady'),
        (531, 3, '5', 'Daně a poplatky {}', 'Náklady', 'Daně a poplatky'),
        (541, 5, '5', 'Ostatní provozní N {}', 'Náklady', 'Ostatní provozní náklady'),
        (551, 5, '5', 'Odpisy {}', 'Náklady', 'Odpisy'),
        (561, 5, '5', 'Finanční náklady {}', 'Náklady', 'Finanční náklady'),
        (591, 3, '5', 'Daň z příjmů {}', 'Náklady', 'Daně z příjmů'),
        (601, 5, '6', 'Tržby za výrobky {}', 'Výnosy', 'Tržby za vlastní výrobky'),
        (602, 5, '6', 'Tržby za služby {}', 'Výnosy', 'Tržby za služby'),
        (604, 5, '6', 'Tržby za zboží {}', 'Výnosy', 'Tržby za zboží'),
        (641, 5, '6', 'Ostatní provozní V {}', 'Výnosy', 'Ostatní provozní výnosy'),
        (661, 5, '6', 'Finanční výnosy {}', 'Výnosy', 'Finanční výnosy'),
    ]
    rows = []
    for start_num, count, trida, tmpl, typ, skupina in groups:
        for j in range(count):
            num = start_num + j
            rows.append((str(num).zfill(3), tmpl.format(j+1), typ, skupina, trida,
                          random.choice(['aktivní','aktivní','neaktivní'])))
    return save(pd.DataFrame(rows, columns=['ucet_cislo','ucet_nazev','typ','skupina','trida','stav']),
                'dim_ucty.csv')

def gen_zamestnanci(strediska):
    pozice = ['Analytik','Účetní','Manažer','Technik','Operátor','Obchodník','Programátor',
              'Ředitel','Asistent','Koordinátor','Správce','Specialista','Konzultant','Inženýr','Dispečer']
    rows = []
    for i in range(500):
        nastup = DATE_START + datetime.timedelta(random.randint(-1500, 800))
        rows.append((f'EMP{i+1:04d}', fake.first_name(), fake.last_name(),
                      random.choice(strediska['stredisko_id'].tolist()),
                      random.choice(pozice),
                      round(random.uniform(28000, 120000), 0),
                      nastup.isoformat(),
                      random.choice(['Aktivní']*9 + ['Neaktivní']),
                      random.choice(['Plný úvazek']*8 + ['Částečný úvazek','DPP']),
                      fake.email()))
    return save(pd.DataFrame(rows, columns=['zamestnanec_id','jmeno','prijmeni','stredisko_id',
                'pozice','hruba_mzda','datum_nastupu','stav','typ_uvazku','email']),
                'dim_zamestnanci.csv')

def gen_produkty():
    kategorie = ['Elektronika','Strojírenství','Software','Služby','Chemie',
                  'Potraviny','Textil','Stavebnictví','Automotive','Energie']
    rows = []
    for i in range(300):
        cena = round(random.uniform(50, 50000), 2)
        marze = random.uniform(0.1, 0.6)
        rows.append((f'PRD{i+1:04d}', fake.catch_phrase()[:40],
                      random.choice(kategorie), cena,
                      round(cena * (1 - marze), 2),
                      random.choice(['ks','kg','l','m','hod','bal']),
                      random.choice(['Aktivní']*8 + ['Ukončený','Plánovaný'])))
    return save(pd.DataFrame(rows, columns=['produkt_id','produkt_nazev','kategorie',
                'prodejni_cena','nakladova_cena','jednotka','stav']),
                'dim_produkty.csv')

def gen_zakaznici(regiony):
    segmenty = ['Enterprise','SMB','Retail','Government','Non-profit']
    rows = []
    for i in range(200):
        rows.append((f'CUS{i+1:04d}', fake.company()[:50],
                      random.choice(segmenty),
                      random.choice(regiony['region_id'].tolist()),
                      fake.street_address(), fake.city(),
                      random.choice(['Aktivní']*8 + ['Neaktivní','Prospect']),
                      round(random.uniform(10000, 5000000), 2),
                      random.choice(['NET30','NET60','NET90','COD'])))
    return save(pd.DataFrame(rows, columns=['zakaznik_id','zakaznik_nazev','segment','region_id',
                'adresa','mesto','stav','kreditni_limit','platebni_podminky']),
                'dim_zakaznici.csv')

def gen_dodavatele():
    kategorie = ['Materiál','Služby','IT','Logistika','Energie','Suroviny','Údržba','Marketing']
    rows = []
    for i in range(100):
        rows.append((f'SUP{i+1:03d}', fake.company()[:50],
                      random.choice(kategorie),
                      random.choice(['A','A','B','B','C']),
                      fake.street_address(), fake.city(),
                      random.choice(['CZ','CZ','CZ','SK','DE','AT']),
                      random.choice(['Aktivní']*8 + ['Neaktivní','Blokovaný']),
                      random.choice(['NET30','NET45','NET60','Předem'])))
    return save(pd.DataFrame(rows, columns=['dodavatel_id','dodavatel_nazev','kategorie',
                'hodnoceni','adresa','mesto','zeme','stav','platebni_podminky']),
                'dim_dodavatele.csv')

# ============================================================
# 2. FACT TABLES
# ============================================================

def gen_transakce(ucty, strediska, projekty, profit_centra, pobocky, n=500000):
    """Main accounting transactions."""
    print(f"\n  Generating {n:,} transactions...")
    typy_dokladu = ['FAP','FAP','FAV','FAV','FAV','PPD','VPD','BV','BV','INT','OPR','ZAL','DOB','STR']
    meny = ['CZK']*80 + ['EUR']*15 + ['USD']*5
    dph_sazby = [0.21, 0.21, 0.21, 0.15, 0.15, 0.10, 0.0]
    kurzy = {'CZK': 1.0, 'EUR': 24.5, 'USD': 22.8}

    ucet_list = ucty['ucet_cislo'].tolist()
    str_list = strediska['stredisko_id'].tolist()
    proj_list = projekty['projekt_id'].tolist()
    pc_list = profit_centra['profit_centrum_id'].tolist()
    pob_list = pobocky['pobocka_id'].tolist()

    chunk_size = 50000
    chunks = []
    tx_id = 1

    for chunk_start in range(0, n, chunk_size):
        cn = min(chunk_size, n - chunk_start)
        dates = seasonal_dates(cn)
        castky_base = np.abs(np.random.lognormal(mean=8, sigma=2, size=cn)).round(2)
        castky_base = np.clip(castky_base, 10, 50000000)

        rows = []
        for i in range(cn):
            mena = random.choice(meny)
            dph_sazba = random.choice(dph_sazby)
            castka = float(castky_base[i])
            dph = round(castka * dph_sazba, 2)
            typ_dokladu = random.choice(typy_dokladu)
            ucet_md = random.choice(ucet_list)
            ucet_dal = random.choice(ucet_list)
            while ucet_dal == ucet_md:
                ucet_dal = random.choice(ucet_list)

            rows.append((
                f'TX{tx_id:07d}', dates[i].isoformat(), typ_dokladu,
                castka, mena, kurzy[mena], round(castka * kurzy[mena], 2),
                dph_sazba, dph,
                ucet_md, ucet_dal,
                random.choice(str_list), random.choice(proj_list),
                random.choice(pc_list), random.choice(pob_list),
                fake.sentence(nb_words=4)[:60] if random.random() < 0.3 else '',
                random.choice(['Zaúčtováno','Zaúčtováno','Zaúčtováno','Koncept','Storno']),
                f'USR{random.randint(1,50):03d}',
            ))
            tx_id += 1

        chunks.append(pd.DataFrame(rows, columns=[
            'transakce_id','datum','typ_dokladu','castka','mena','kurz','castka_czk',
            'dph_sazba','dph_castka','ucet_md','ucet_dal','stredisko_id','projekt_id',
            'profit_centrum_id','pobocka_id','popis','stav','uzivatel']))

        print(f"    chunk {chunk_start+cn:>10,}/{n:,}")

    df = pd.concat(chunks, ignore_index=True)
    return save(df, 'fact_transakce.csv')

def gen_mzdy(zamestnanci):
    """Payroll data – monthly for each active employee."""
    rows = []
    emps = zamestnanci[zamestnanci['stav'] == 'Aktivní']
    for _, emp in emps.iterrows():
        hruba = float(emp['hruba_mzda'])
        for year in range(2023, 2026):
            for month in range(1, 13):
                soc_zam = round(hruba * 0.065, 2)  # employee social
                zdr_zam = round(hruba * 0.045, 2)  # employee health
                soc_firm = round(hruba * 0.248, 2)  # employer social
                zdr_firm = round(hruba * 0.09, 2)   # employer health
                dan = round(max(0, (hruba - soc_zam - zdr_zam) * 0.15), 2)
                cista = round(hruba - soc_zam - zdr_zam - dan, 2)
                odmena = round(random.uniform(0, hruba * 0.15), 2) if random.random() < 0.2 else 0
                rows.append((
                    emp['zamestnanec_id'], emp['stredisko_id'], f'{year}-{month:02d}',
                    hruba, odmena, hruba + odmena,
                    soc_zam, zdr_zam, soc_firm, zdr_firm, dan,
                    cista + odmena * 0.7,
                    round(hruba + odmena + soc_firm + zdr_firm, 2)
                ))
    return save(pd.DataFrame(rows, columns=[
        'zamestnanec_id','stredisko_id','obdobi','zakladni_mzda','odmeny','hruba_mzda_celkem',
        'soc_pojisteni_zam','zdr_pojisteni_zam','soc_pojisteni_firma','zdr_pojisteni_firma',
        'dan_z_prijmu','cista_mzda','celkove_naklady_firma']),
        'fact_mzdy.csv')

def gen_prodeje(zakaznici, produkty, pobocky, n=100000):
    """Sales / revenue data."""
    zak_list = zakaznici['zakaznik_id'].tolist()
    prod_df = produkty[['produkt_id','prodejni_cena','nakladova_cena']].values.tolist()
    pob_list = pobocky['pobocka_id'].tolist()
    kanaly = ['E-shop','Pobočka','Telefon','B2B portál','Obchodní zástupce']

    rows = []
    dates = seasonal_dates(n)
    for i in range(n):
        prod = random.choice(prod_df)
        mnozstvi = random.randint(1, 100)
        cena = float(prod[1])
        sleva_pct = random.choice([0,0,0,0,5,10,15,20]) / 100
        dph = random.choice([0.21, 0.15, 0.10])
        celkem_bez_dph = round(mnozstvi * cena * (1 - sleva_pct), 2)
        rows.append((
            f'FAV{i+1:07d}', dates[i].isoformat(),
            random.choice(zak_list), prod[0], mnozstvi, cena,
            sleva_pct, celkem_bez_dph,
            dph, round(celkem_bez_dph * dph, 2), round(celkem_bez_dph * (1 + dph), 2),
            round(mnozstvi * float(prod[2]), 2),
            random.choice(pob_list), random.choice(kanaly),
            random.choice(['Zaplaceno','Zaplaceno','Zaplaceno','Nezaplaceno','Částečně','Storno']),
            random.choice(['CZK']*85 + ['EUR']*15),
        ))
        if (i+1) % 25000 == 0:
            print(f"    sales {i+1:>10,}/{n:,}")

    return save(pd.DataFrame(rows, columns=[
        'faktura_id','datum','zakaznik_id','produkt_id','mnozstvi','jednotkova_cena',
        'sleva_pct','celkem_bez_dph','dph_sazba','dph_castka','celkem_s_dph',
        'nakladova_cena_celkem','pobocka_id','kanal','stav_platby','mena']),
        'fact_prodeje.csv')

def gen_nakupy(dodavatele, produkty, strediska, n=50000):
    """Purchase / procurement data."""
    dod_list = dodavatele['dodavatel_id'].tolist()
    str_list = strediska['stredisko_id'].tolist()
    typy_pol = ['Materiál','Služba','Energie','Náhradní díly','Kancelářské potřeby',
                'IT vybavení','Software licence','Doprava','Údržba','Suroviny']

    rows = []
    dates = random_dates(n)
    for i in range(n):
        mnozstvi = random.randint(1, 500)
        cena = round(random.uniform(20, 25000), 2)
        dph = random.choice([0.21, 0.15, 0.10, 0.0])
        celkem = round(mnozstvi * cena, 2)
        rows.append((
            f'OBJ{i+1:06d}', dates[i].isoformat(),
            random.choice(dod_list), random.choice(typy_pol),
            mnozstvi, cena, celkem, dph, round(celkem * dph, 2), round(celkem * (1 + dph), 2),
            random.choice(str_list),
            random.choice(['Schváleno','Schváleno','Přijato','Částečně přijato','Reklamace','Koncept']),
            random.choice(['CZK']*85 + ['EUR']*10 + ['USD']*5),
        ))
        if (i+1) % 10000 == 0:
            print(f"    purchases {i+1:>10,}/{n:,}")

    return save(pd.DataFrame(rows, columns=[
        'objednavka_id','datum','dodavatel_id','typ_polozky','mnozstvi','jednotkova_cena',
        'celkem_bez_dph','dph_sazba','dph_castka','celkem_s_dph','stredisko_id','stav','mena']),
        'fact_nakupy.csv')

def gen_vyrobni_zakazky(produkty, strediska, n=20000):
    """Production / manufacturing orders."""
    vyr_produkty = produkty[produkty['kategorie'].isin(
        ['Elektronika','Strojírenství','Chemie','Automotive','Textil','Stavebnictví'])
    ]['produkt_id'].tolist()
    if not vyr_produkty:
        vyr_produkty = produkty['produkt_id'].tolist()[:50]
    str_vyr = strediska[strediska['typ'] == 'Výroba']['stredisko_id'].tolist()
    if not str_vyr:
        str_vyr = strediska['stredisko_id'].tolist()[:10]
    stavy = ['Plánováno','V výrobě','V výrobě','Dokončeno','Dokončeno','Dokončeno','Pozastaveno','Zrušeno']

    rows = []
    for i in range(n):
        start = DATE_START + datetime.timedelta(random.randint(0, 900))
        dur = random.randint(1, 45)
        mnozstvi = random.randint(10, 5000)
        mat_cost = round(random.uniform(1000, 500000), 2)
        labor_cost = round(mat_cost * random.uniform(0.2, 0.8), 2)
        overhead = round((mat_cost + labor_cost) * random.uniform(0.05, 0.25), 2)
        rows.append((
            f'VZ{i+1:06d}', random.choice(vyr_produkty), mnozstvi,
            start.isoformat(), (start + datetime.timedelta(dur)).isoformat(),
            random.choice(str_vyr), mat_cost, labor_cost, overhead,
            round(mat_cost + labor_cost + overhead, 2),
            random.choice(stavy), round(random.uniform(0.85, 1.05), 3),
            random.randint(0, int(mnozstvi * 0.05)),
        ))

    return save(pd.DataFrame(rows, columns=[
        'zakazka_id','produkt_id','planovane_mnozstvi','datum_zahajeni','datum_ukonceni',
        'stredisko_id','naklady_material','naklady_prace','naklady_rezie',
        'celkove_naklady','stav','vyuziti_kapacity','zmetky']),
        'fact_vyrobni_zakazky.csv')

def gen_cashflow(pobocky, ucty, n=80000):
    """Cash flow data."""
    typy = ['Příjem z prodeje','Příjem z prodeje','Příjem z prodeje',
            'Platba dodavateli','Platba dodavateli','Mzdy','Daně','Splátka úvěru',
            'Úroky','Investice','Příjem úvěru','Dividendy','Ostatní příjem','Ostatní výdaj']
    pob_list = pobocky['pobocka_id'].tolist()
    ucet_list = ucty[ucty['skupina'] == 'Finanční účty']['ucet_cislo'].tolist()
    if not ucet_list:
        ucet_list = ucty['ucet_cislo'].tolist()[:10]

    rows = []
    dates = seasonal_dates(n)
    for i in range(n):
        typ = random.choice(typy)
        is_income = typ in ('Příjem z prodeje','Příjem úvěru','Ostatní příjem','Dividendy')
        castka = round(random.uniform(500, 2000000), 2)
        rows.append((
            f'CF{i+1:06d}', dates[i].isoformat(), typ,
            'Příjem' if is_income else 'Výdaj',
            castka if is_income else -castka,
            random.choice(ucet_list), random.choice(pob_list),
            random.choice(['CZK']*85 + ['EUR']*15),
            random.choice(['Realizováno','Realizováno','Realizováno','Plánováno']),
        ))

    return save(pd.DataFrame(rows, columns=[
        'cashflow_id','datum','typ_pohybu','smer','castka','ucet','pobocka_id','mena','stav']),
        'fact_cashflow.csv')

def gen_budget(strediska, ucty):
    """Budget vs actual per cost center, account, and month."""
    str_list = strediska['stredisko_id'].tolist()
    # Use subset of accounts for budgeting (costs & revenues)
    budget_ucty = ucty[ucty['typ'].isin(['Náklady','Výnosy'])]['ucet_cislo'].tolist()
    if len(budget_ucty) > 40:
        budget_ucty = random.sample(budget_ucty, 40)

    rows = []
    for strid in str_list:
        for ucet in random.sample(budget_ucty, min(8, len(budget_ucty))):
            for year in range(2023, 2026):
                for month in range(1, 13):
                    plan = round(random.uniform(5000, 500000), 2)
                    skutecnost = round(plan * random.uniform(0.7, 1.3), 2)
                    rows.append((
                        strid, ucet, f'{year}-{month:02d}',
                        plan, skutecnost, round(skutecnost - plan, 2),
                        round((skutecnost - plan) / plan * 100, 1),
                    ))

    return save(pd.DataFrame(rows, columns=[
        'stredisko_id','ucet_cislo','obdobi','plan','skutecnost','odchylka','odchylka_pct']),
        'fact_budget.csv')


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  FINANCIAL CONTROLLING DATASET GENERATOR")
    print("=" * 60)
    print(f"\n  Output: {OUTPUT_DIR}\n")

    print("\n── Dimension Tables ──")
    regiony = gen_regiony()
    pobocky = gen_pobocky(regiony)
    strediska = gen_strediska(pobocky)
    profit_centra = gen_profit_centra(regiony)
    projekty = gen_projekty()
    ucty = gen_ucty()
    zamestnanci = gen_zamestnanci(strediska)
    produkty = gen_produkty()
    zakaznici = gen_zakaznici(regiony)
    dodavatele = gen_dodavatele()

    print("\n── Fact Tables ──")
    gen_transakce(ucty, strediska, projekty, profit_centra, pobocky)
    gen_mzdy(zamestnanci)
    gen_prodeje(zakaznici, produkty, pobocky)
    gen_nakupy(dodavatele, produkty, strediska)
    gen_vyrobni_zakazky(produkty, strediska)
    gen_cashflow(pobocky, ucty)
    gen_budget(strediska, ucty)

    print("\n" + "=" * 60)
    print("  ALL DONE!")
    total_files = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')])
    total_size = sum(os.path.getsize(os.path.join(OUTPUT_DIR, f))
                     for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv'))
    print(f"  Files: {total_files}")
    print(f"  Total size: {total_size / 1024 / 1024:.1f} MB")
    print("=" * 60)


if __name__ == '__main__':
    main()
