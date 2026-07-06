// translate-background.mjs
// Background function: tradueix articles ja extrets al català jurídic tècnic
// Llegeix _art_{docKey}, tradueix via Gemini, desa a _art_ca_{docKey}

import { getStore } from "@netlify/blobs";

const GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent";

export default async (req) => {
  let docKey;
  try { const body = await req.json(); docKey = body.docKey; } catch { return; }
  if (!docKey) return;

  const store = getStore("normativa-docs");
  const apiKey = Netlify.env.get("GEMINI_API_KEY");
  const origKey  = `_art_${docKey}`;
  const catKey   = `_art_ca_${docKey}`;
  const statusKey = `_art_ca_status_${docKey}`;

  try { await store.set(statusKey, JSON.stringify({ status: "processing", started: Date.now() })); } catch {}

  try {
    const origRaw = await store.get(origKey, { type: "text" });
    if (!origRaw) throw new Error("Articles originals no trobats a Blobs");

    const origArticles = JSON.parse(origRaw);
    if (!origArticles.length) throw new Error("Cap article original per traduir");

    // Divideix en lots: articles curts → lots de 20; articles llargs → lots de 5
    const avgTextLen = origArticles.reduce((s, a) => s + (a.text?.length || 0), 0) / origArticles.length;
    const BATCH = avgTextLen > 5000 ? 5 : avgTextLen > 2000 ? 10 : 20;
    const allTranslated = [];

    for (let i = 0; i < origArticles.length; i += BATCH) {
      const batch = origArticles.slice(i, i + BATCH);

      const translatePrompt = `Tradueix aquest array JSON d'articles normatius al català jurídic i tècnic formal correcte.
Retorna ÚNICAMENT el mateix array JSON amb els mateixos camps ("num", "title", "text"), però amb "title" i "text" traduïts al català.
Criteris de traducció:
- Usa terminologia jurídica catalana estàndard (ex: "han de" per "deben", "d'acord amb" per "conforme a", "estableix" per "establece", "espais públics urbanitzats" per "espacios públicos urbanizados", "ordenança" per "ordenanza", "municipi" per "municipio")
- Conserva la numeració interna, les referències a altres articles i les remissions normatives
- Mantén els acrònims tècnics establerts (BOE, CTE, DB, etc.) i els topònims oficials
- Si un terme especialitzat no té equivalent precís en català, inclou el terme original entre parèntesis
- Utilitza el to formal i la precisió tècnica propis dels textos legals catalans
- El camp "num" NO s'ha de traduir (conserva el valor original exacte)
- CONSERVA EL FORMAT DEL CAMP "text": mantén exactament els mateixos salts de línia (\\n), llistes (a), b), 1., 2., •, –), numeració de subapartats i sagnies que té el text original

Articles a traduir:
${JSON.stringify(batch)}

Retorna ÚNICAMENT l'array JSON, sense cap text addicional ni markdown.`;

      const resp = await fetch(GEMINI_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-goog-api-key": apiKey },
        body: JSON.stringify({
          contents: [{ role: "user", parts: [{ text: translatePrompt }] }],
          generationConfig: { temperature: 0.1, maxOutputTokens: 65536, topP: 0.9 }
        })
      });

      if (!resp.ok) {
        const errText = await resp.text();
        throw new Error(`Gemini ${resp.status}: ${errText.substring(0, 200)}`);
      }

      const data = await resp.json();
      const rawText = data.candidates?.[0]?.content?.parts?.[0]?.text ?? "[]";
      let batchTranslated = [];
      try {
        const match = rawText.match(/\[[\s\S]*\]/);
        if (match) {
          batchTranslated = JSON.parse(match[0]);
        } else {
          const startIdx = rawText.indexOf('[');
          if (startIdx !== -1) {
            let partial = rawText.substring(startIdx);
            const lastComplete = partial.lastIndexOf('},');
            if (lastComplete > 0) {
              partial = partial.substring(0, lastComplete + 1) + ']';
              batchTranslated = JSON.parse(partial);
            }
          }
        }
      } catch { batchTranslated = batch; } // fallback: retorna originals si falla el parse

      allTranslated.push(...batchTranslated);
    }

    await store.set(catKey, JSON.stringify(allTranslated));
    try { await store.delete(statusKey); } catch {}
    console.log(`[translate-background] OK: ${docKey} → ${allTranslated.length} articles CA`);
  } catch (e) {
    console.error(`[translate-background] ERROR: ${docKey}:`, e.message);
    try { await store.set(statusKey, JSON.stringify({ status: "error", message: e.message })); } catch {}
  }
};
