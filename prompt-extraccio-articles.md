# Prompt per a Gemini — Extracció d'articles de normativa

## Com usar-lo

1. Obre [gemini.google.com](https://gemini.google.com) o el model Gemini 2.5 Flash/Pro que tinguis disponible
2. Adjunta el PDF de la normativa (pots arrossegar-lo al xat)
3. Enganxa el prompt de sota i envia

---

## El prompt (copia i enganxa)

```
Analitza el document PDF adjunt i extreu TOTS els articles, seccions i apartats que contingui.

Retorna ÚNICAMENT un array JSON vàlid amb aquest format exacte, sense cap text addicional, sense markdown, sense ```json:

[
  {
    "num": "Art. 1",
    "title": "Objecte",
    "text": "Contingut complet de l'article tal com apareix al document, sense resumir ni ometre res."
  },
  {
    "num": "Art. 2",
    "title": "Àmbit d'aplicació",
    "text": "..."
  }
]

Regles:
- "num": número d'article o secció (exemples vàlids: "Art. 1", "Article 1", "Secció 2", "Disposició Addicional 1a", "Annex I", "Capítol III")
- "title": títol de l'article o secció, sense el número
- "text": TEXT COMPLET sense resumir. Inclou tots els punts, lletres i subapartats. Preserva salts de línia amb \n
- Inclou disposicions addicionals, transitòries, derogatòries i finals
- Inclou annexos com a elements separats
- NO incloguis la portada, índex ni preàmbul com a articles
- Si el document no té articles numerats, usa els títols de secció al camp "num"

Comença directament amb [ i acaba amb ]
```

---

## Què fer amb el resultat

Un cop Gemini retorni el JSON:

1. Selecciona tot el text retornat (Ctrl+A dins del xat) i copia'l
2. Guarda'l com a fitxer `.json` (per exemple: `TMA851.pdf.json`)
3. A l'aplicació, passa el ratolí per sobre del document al panell de l'esquerra
4. Apareixerà una icona de pujada (↑) — clica-la
5. Selecciona el fitxer `.json` que has guardat
6. Els articles es carregaran immediatament i es guardaran en caché

> El nom del fitxer JSON no importa — l'aplicació llegeix el contingut, no el nom.
