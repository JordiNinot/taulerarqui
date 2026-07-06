# DOCUMENTACIÓ DE BASE - TAXES D'OCUPACIÓ DE LA VIA PÚBLICA

Aquest document conté el nomenclàtor oficial de carrers amb la seva categoria fiscal corresponent i la normativa reguladora de les tarifes per a l'ocupació temporal de l'espai públic en aquest municipi.

---

## 1. NOMENCLÀTOR DE CARRERS I CATEGORIES FISCALS

La categoria d'un carrer determina el coeficient corrector aplicat a la taxa de via pública. Les dades provenen de l'**Annex de carrers** de l'**Ordenança Fiscal 2.2 (IAE) de l'Ajuntament de Sabadell**, que estableix 6 categories fiscals oficials (Article 10è). L'Ordenança Fiscal 4.5, que regula les taxes d'ocupació de la via pública, reutilitza aquest mateix annex per a la classificació dels carrers (Article 7è.13).

| Categoria Fiscal Oficial | Coeficient IAE Real | Coeficient Normalitzat (usat a la calculadora) |
| :---: | :---: | :---: |
| 1A | 3.800 | 1.50 |
| 1B | 3.700 | 1.45 |
| 2 | 3.405 | 1.28 |
| 3 | 3.164 | 1.15 |
| 4 | 2.915 | 1.02 |
| 5 | 2.519 | 0.80 |

*El coeficient normalitzat s'obté per interpolació lineal del coeficient IAE real dins el rang 0.80–1.50, i s'utilitza directament en les fórmules dels conceptes A (Tanca), B (Grua) i C (Rasa) de la secció 2. El concepte D (Terrasses) n'és l'excepció: utilitza tarifes oficials per m² ja diferenciades per categoria (veure secció 2, Concepte D), de manera que aquest coeficient no s'hi aplica per evitar duplicar l'ajust categòric.*

### Mostra de carrers (llistat complet a `app.js` → `baseCarrers`, 1.157 entrades)

| Nom del Carrer | Categoria Fiscal | Coeficient Normalitzat |
| :--- | :---: | :---: |
| Plaça de Catalunya | 1A | 1.50 |
| Avinguda de Francesc Macià | 1A | 1.50 |
| Rambla | 1B | 1.45 |
| Carrer de Sant Cugat | 1B | 1.45 |
| Carrer de Sant Josep | 1B | 1.45 |
| Carrer de Sant Pere | 1B | 1.45 |
| Carrer de Cervantes | 2 | 1.28 |
| Carrer del Marquès de Comillas | 2 | 1.28 |
| Carretera de Caldes | 3 | 1.15 |
| Plaça de la Creu de Barberà | 3 | 1.15 |
| Carrer del Marquès Ciutadilla | 4 | 1.02 |
| Carrer de Ruiz Villalba | 4 | 1.02 |
| Carrer del Pintor Pradilla | 5 | 0.80 |

*Nota: Qualsevol carrer no inclòs expressament a l'annex oficial s'assimila per defecte a la **Categoria 5 (Coeficient 0.80)**, seguint la regla legal de l'Article 10è.3 de l'Ordenança 2.2 ("els carrers no inclosos en la relació seran considerats... de l'última categoria").*

*Limitació coneguda: l'extracció del PDF font no va permetre capturar el 100% de l'alfabet (cobreix aproximadament de la A a la S); els carrers no capturats (aprox. un 15%, majoritàriament T–Z) cauen també al valor per defecte de Categoria 5 fins que es completi l'annex.*

### Categoria variable segons número de portal

A l'annex oficial, **46 dels 1.157 carrers** tenen una categoria fiscal que **canvia segons el número de policia** (per exemple, un costat del carrer en una categoria i l'altre en una categoria diferent, o trams "del 1 al 100" / "del 101 al final" amb categories diferents). Per a aquests carrers, la calculadora demana opcionalment el **número de portal** i resol la categoria exacta segons els trams definits a l'annex (camp `trams` a `baseCarrers`, a `app.js`), tenint en compte la paritat (parell/imparell) i el rang numèric de cada tram.

* Si no s'indica número de portal, o el carrer no té trams definits, s'utilitza la **categoria predominant (moda)** del carrer com a aproximació.
* Si s'indica un número però aquest no encaixa exactament en cap tram registrat (un buit puntual a les dades font, detectat en 2 dels 46 carrers), la calculadora recorre també a la categoria predominant com a aproximació conservadora, en lloc de bloquejar el càlcul.
* Exemple: a l'Avinguda d'Arraona, els números 1–23 i 2–22 són categoria 3, mentre que del 24/25 en endavant passen a categoria 2.

Aquesta lògica es manté com una resolució *més precisa* del mateix sistema de categories de la secció anterior; no modifica les tarifes ni fórmules de la secció 2.

### Validació del número de portal

El camp de número de portal només accepta un **enter positiu** (sense decimals, signes ni lletres); qualsevol altre valor es marca com a invàlid amb un missatge a sota del camp i **bloqueja el botó "Calcular Taxa Estimada"** fins que es corregeixi o es deixi en blanc.

No es bloqueja, en canvi, cap número que simplement no encaixi amb cap tram registrat (vegeu el punt anterior): l'annex de trams defineix límits de categoria fiscal, no un cens real d'adreces, i els seus trams són gairebé sempre **oberts per dalt** (p. ex. "del 24 en endavant"). A més, 3 dels 46 carrers amb trams (Plaça de Ramon Llull, Carrer d'Antoni Forrellad, Carrer de Prat de la Riba) tenen un buit real de dades en un dels dos costats (parell/imparell) que **no** vol dir que aquells portals no existeixin —simplement que l'annex no els classifica explícitament, i la calculadora hi aplica la categoria predominant com a aproximació. Per aquest motiu, validar "número inexistent" més enllà del format bàsic requeriria un cens postal real (p. ex. el dataset de l'Ajuntament a `opendata.sabadell.cat`, no incorporat encara a la calculadora) i queda fora de l'abast d'aquesta validació.

---

## 2. ORDENANÇA FISCAL: TARIFES D'OCUPACIÓ TEMPORAL

El càlcul estimat de les taxes d'ocupació de l'espai públic municipal s'obté mitjançant les següents tarifes bases i coeficients.

### Concepte A: Tanca, Bastida o Tancament d'Obra
* **Descripció**: Ocupació de vorera o calçada mitjançant elements protectors, bastides de façana o pilars de sustentació d'obra.
* **Tarifa Base**: 1,20 € per m² i dia.
* **Fórmula**:
  $$\text{Taxa} = \text{Superfície (m²)} \times \text{Durada (Dies)} \times 1.20 \times \text{Coeficient Categoria}$$

### Concepte B: Grua Mòbil o Reserva d'Espai
* **Descripció**: Ocupació de la calçada per a operacions de càrrega/descàrrega, estacionament de grues de gran tonatge o reserves per a mudances.
* **Tarifa Base**: 3,50 € per metre lineal i dia.
* **Fórmula**:
  $$\text{Taxa} = \text{Metres Lineals (ml)} \times \text{Durada (Dies)} \times 3.50 \times \text{Coeficient Categoria}$$

### Concepte C: Cales, Rases i Calicantes (Obres en Paviment)
* **Descripció**: Perforació del paviment o vorera per a connexions de serveis (aigua, gas, llum, telecomunicacions).
* **Tarifa Base**: 15,00 € per m² afectat.
* **Drets d'Obra Fixos**: 60,00 € fixos per sol·licitud de cala.
* **Fórmula**:
  $$\text{Taxa} = 60.00 + (\text{Superfície Afectada (m²)} \times 15.00 \times \text{Coeficient Categoria})$$

### Concepte D: Terrasses i Vetlladors (per m²)
* **Descripció**: Ocupació de l'espai de via pública (vorera o calçada) per a l'activitat de restauració (taules, cadires i altres elements de vetllador).
* **Font**: tarifes reals i oficials de l'**Annex de tarifes, Secció 2a** de l'**Ordenança Fiscal 4.5 (2026)**. A diferència dels conceptes A, B i C, aquestes tarifes ja estan diferenciades per categoria de carrer (no s'hi aplica el coeficient normalitzat de la secció 1, per evitar duplicar l'ajust categòric).
* **Modalitats d'autorització** (segons l'Article 7è.6): una terrassa es pot autoritzar per temporada anual, temporada d'estiu, temporada d'hivern, només caps de setmana d'estiu, només caps de setmana d'hivern, o de forma eventual (puntual, facturada per dies). Un "cap de setmana" comprèn de divendres a diumenge inclosos.
* **Línies d'autorització independents**: com que diferents parts d'una mateixa terrassa poden tenir superfícies i règims diferents (p. ex. una part autoritzada tot l'any i una extensió que només s'autoritza a l'estiu), la calculadora permet afegir diverses línies, cadascuna amb la seva pròpia modalitat i m² (i dies, si la modalitat és "eventual"). El total és la suma de totes les línies. No hi ha restricció d'exclusivitat entre modalitats —incloent "Temporada anual"—, ja que cada línia pot representar una superfície diferent de la mateixa terrassa.

**Tarifes oficials per m² (€), 2026:**

| Categoria | Anual | Estiu | Hivern | Caps de setmana estiu | Caps de setmana hivern | Eventual (dia) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1A | 105,01 | 67,55 | 55,02 | 34,51 | 26,52 | 0,54 |
| 1B | 95,77 | 61,56 | 50,30 | 31,54 | 26,52 | 0,48 |
| 2 | 74,15 | 47,63 | 39,46 | 24,52 | 26,52 | 0,37 |
| 3 | 55,58 | 35,72 | 30,15 | 18,34 | 26,52 | 0,31 |
| 4 | 55,58 | 35,72 | 30,15 | 18,34 | 26,52 | 0,31 |
| 5 | 55,58 | 35,72 | 30,15 | 18,34 | 26,52 | 0,31 |

*Nota: les categories 3, 4 i 5 comparteixen exactament les mateixes tarifes de terrassa. La modalitat "Caps de setmana d'hivern" és un import pla (26,52 €) idèntic per a totes les categories, segons consta literalment a l'annex oficial.*

* **Fórmula per línia (modalitats per temporada: anual / estiu / hivern / caps de setmana estiu / caps de setmana hivern)** — import únic per a tot el període, no es multiplica per dies ni mesos:
  $$\text{Taxa}_{\text{línia}} = \text{Superfície línia (m²)} \times \text{Tarifa}[\text{Categoria}][\text{Modalitat}]$$

* **Fórmula per línia (modalitat eventual)** — facturació per dia:
  $$\text{Taxa}_{\text{línia}} = \text{Superfície línia (m²)} \times \text{Dies} \times \text{Tarifa}[\text{Categoria}][\text{eventual}]$$

* **Selecció de dies eventuals per calendari**: per a la modalitat "Eventual", el nombre de "Dies" no s'introdueix manualment: es deriva del **recompte de dates concretes** que el tècnic marca en un calendari interactiu (un per línia). El calendari permet navegar entre mesos i anys, i assenyala visualment els **festius oficials** vigents a Sabadell, a tres nivells jurisdiccionals:
  * **Estatal** (Espanya) — vora vermella inferior a la cel·la del dia.
  * **Autonòmic** (Catalunya) — vora taronja.
  * **Local** (Sabadell) — vora verda.

  Els dies seleccionats es marquen en blau. Aquestes dades es guarden a `FESTIUS` (a `app.js`) per als anys 2026 i 2027 i **s'han de revisar i actualitzar cada any**, ja que els festius (especialment els autonòmics i locals) varien: el calendari laboral de Catalunya es publica anualment per ordre del Departament d'Empresa i Treball, i els dos festius locals els aprova cada any el Ple de l'Ajuntament de Sabadell (abans del 2 d'octubre de l'any anterior). Si una línia eventual fa referència a un any sense dades de festius carregades, el calendari es mostra igualment (sense marcar cap dia com a festiu) i el càlcul continua funcionant amb normalitat a partir del recompte de dies marcats.

  **Festius carregats per al 2026** (Sabadell): 1 de gener (Cap d'Any, estatal), 6 de gener (Reis, autonòmic), 3 d'abril (Divendres Sant, autonòmic), 6 d'abril (Dilluns de Pasqua, autonòmic), 1 de maig (Treball, estatal), **11 de maig (Aplec de la Salut, local)**, 24 de juny (Sant Joan, autonòmic), 15 d'agost (Assumpció, estatal), **7 de setembre (Festa Major de Sabadell, local)**, 11 de setembre (Diada Nacional, autonòmic), 12 d'octubre (Hispanitat, estatal), 1 de novembre (Tots Sants, estatal), 6 de desembre (Constitució, estatal), 8 de desembre (Immaculada, estatal), 25 de desembre (Nadal, estatal), 26 de desembre (Sant Esteve, autonòmic).

* **Total del concepte**: suma de la taxa de totes les línies afegides.
  $$\text{Taxa} = \sum_{\text{línies}} \text{Taxa}_{\text{línia}}$$

* **Exemple (línia única)**: una terrassa de 20 m² a la Rambla (Categoria 1B) amb autorització de temporada d'estiu: $20 \times 61.56 = 1.231,20$ €. La mateixa terrassa en règim eventual durant 5 dies: $20 \times 5 \times 0.48 = 48,00$ €.

* **Exemple (línies combinades)**: una terrassa a la Rambla (Categoria 1B) amb 20 m² autoritzats tot l'any (anual), 12 m² addicionals només a l'estiu, i 23 m² més només els caps de setmana d'hivern: $(20 \times 95{,}77) + (12 \times 61{,}56) + (23 \times 26{,}52) = 1.915{,}40 + 738{,}72 + 609{,}96 = 3.264{,}08$ €.
