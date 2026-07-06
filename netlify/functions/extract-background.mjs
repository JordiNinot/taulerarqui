// extract-background.mjs
// Background function: extreu articles d'un PDF via Gemini (fins 15 min, retorna 202 immediatament)
// El resultat s'emmagatzema a Netlify Blobs; el browser fa polling via /api/gemini?extractStatus

import { getStore } from "@netlify/blobs";

const GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent";

export default async (req) => {
  let docKey;
  try {
    const body = await req.json();
    docKey = body.docKey;
  } catch { return; }

  if (!docKey) return;

  const store = getStore("normativa-docs");
  const apiKey = Netlify.env.get("GEMINI_API_KEY");
  const cacheKey = `_art_${docKey}`;
  const statusKey = `_art_status_${docKey}`;

  // Marca com a processant
  try { await store.set(statusKey, JSON.stringify({ status: "processing", started: Date.now() })); } catch { }

  try {
    const buffer = await store.get(docKey, { type: "arrayBuffer" });
    if (!buffer) throw new Error("Document no trobat");
    if (buffer.byteLength > 10 * 1024 * 1024) throw new Error("Document massa gran");

    const pdfData = Buffer.from(buffer).toString("base64");
    const extractPrompt = `Extreu TOTS els articles o seccions d'aquest document PDF com a array JSON.
Format exacte per cada element: {"num":"identificador original","title":"Títol exacte","text":"text complet"}

Regles OBLIGATÒRIES per al camp "text":
- Copia el text de forma LITERAL i COMPLETA, sense resumir ni ometre res
- Conserva exactament els salts de paràgraf originals com \\n entre paràgrafs
- Conserva les llistes i enumeracions amb els marcadors originals: a), b), c), 1., 2., 3., •, –, etc.
- Conserva la numeració de subapartats (1.1, 1.2, art. 5.1, etc.) exactament com apareix
- Conserva les tabulacions i sagnies com espais
- Conserva les taules en format text pla mantenint l'alineació amb espais
- NO fussionis paràgrafs separats; mantén cada paràgraf en la seva línia
- NO eliminis ni abreugis cap contingut

Si no hi ha articles numerats, usa el títol de secció com a identificador "num".
Retorna ÚNICAMENT l'array JSON, sense cap text addicional ni markdown.`;

    const extractResp = await fetch(GEMINI_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-goog-api-key": apiKey },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [
          { text: extractPrompt },
          { inline_data: { mime_type: "application/pdf", data: pdfData } }
        ]}],
        generationConfig: { temperature: 0.1, maxOutputTokens: 65536, topP: 0.9 }
      })
    });

    if (!extractResp.ok) {
      const errText = await extractResp.text();
      throw new Error(`Gemini ${extractResp.status}: ${errText.substring(0, 200)}`);
    }

    const extractData = await extractResp.json();
    const rawText = extractData.candidates?.[0]?.content?.parts?.[0]?.text ?? "[]";
    const finishReason = extractData.candidates?.[0]?.finishReason ?? "unknown";
    let articles = [];
    try {
      const match = rawText.match(/\[[\s\S]*\]/);
      if (match) {
        articles = JSON.parse(match[0]);
      } else {
        // Fallback: JSON truncat (max tokens assolit) — recupera objectes complets
        const startIdx = rawText.indexOf('[');
        if (startIdx !== -1) {
          let partial = rawText.substring(startIdx);
          // Troba l'últim objecte complet (acaba amb },)
          const lastComplete = partial.lastIndexOf('},');
          if (lastComplete > 0) {
            partial = partial.substring(0, lastComplete + 1) + ']';
            articles = JSON.parse(partial);
          }
        }
      }
    } catch { articles = []; }

    // Debug: desa el rawText (primers 3000 chars) i finishReason per diagnòstic
    try { await store.set(`_art_debug_${docKey}`, JSON.stringify({ finishReason, rawLen: rawText.length, preview: rawText.substring(0, 2000), tail: rawText.substring(Math.max(0, rawText.length - 500)) })); } catch { }

    await store.set(cacheKey, JSON.stringify(articles));
    try { await store.delete(statusKey); } catch { }

    console.log(`[extract-background] OK: ${docKey} → ${articles.length} articles (rawLen=${rawText.length})`);
  } catch (e) {
    console.error(`[extract-background] ERROR: ${docKey}:`, e.message);
    try { await store.set(statusKey, JSON.stringify({ status: "error", message: e.message })); } catch { }
  }
};
