// whatsapp.mjs — Trasto Petit WhatsApp Bot
// Twilio webhook → Claude API → TwiML response
// Desplegat a: https://taulerarqui.netlify.app/.netlify/functions/whatsapp

const SYSTEM_PROMPT = `Ets el Trasto Petit, l'assistent personal del Jordi Ninot de Sabadell.
Ajudes amb qualsevol tasca: cerques, fitxers, dades, CSVs, codi, redaccions, preguntes diverses.

NORMES:
- Contesta SEMPRE en català (o en l'idioma en que t'escriguin).
- Via WhatsApp sigues concís: màxim 3 paràgrafs o 1500 caràcters.
- Si cal accés directe als fitxers del Mac (operacions de disc, GitHub, Netlify), avisa que s'ha de fer des del Cowork de l'ordinador.
- Usa format de text plà sense markdown (WhatsApp no renderitza **negreta** amb asteriscs).
`;

function escapeXml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function twimlResponse(message) {
  // WhatsApp via Twilio: límit pràctic ~1500 chars
  const text = message.length > 1490
    ? message.substring(0, 1487) + '...'
    : message;

  const twiml = `<?xml version="1.0" encoding="UTF-8"?><Response><Message>${escapeXml(text)}</Message></Response>`;
  return new Response(twiml, {
    status: 200,
    headers: { 'Content-Type': 'text/xml; charset=utf-8' }
  });
}

async function callClaude(userMessage) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return 'Error: ANTHROPIC_API_KEY no configurada. Afegeix-la a Netlify → Site configuration → Environment variables i redesplega.';
  }

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 1024,
      system: SYSTEM_PROMPT,
      messages: [{ role: 'user', content: userMessage }]
    })
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Claude API ${res.status}: ${err.substring(0, 200)}`);
  }

  const data = await res.json();
  return data.content[0].text;
}

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
  }

  try {
    // Twilio envia application/x-www-form-urlencoded
    const bodyText = await req.text();
    const params = new URLSearchParams(bodyText);
    const from = params.get('From') || 'unknown';
    const body = params.get('Body') || '';

    console.log(`[trasto-wa] From: ${from} | "${body.substring(0, 80)}"`);

    if (!body.trim()) {
      return twimlResponse('Hola! Sóc el Trasto Petit. Escriu-me el que necessites i t\'ajudaré!');
    }

    const reply = await callClaude(body);
    return twimlResponse(reply);

  } catch (err) {
    console.error('[trasto-wa] Error:', err.message);
    return twimlResponse(`Error intern: ${err.message.substring(0, 100)}. Prova-ho de nou.`);
  }
}

export const config = { path: '/api/whatsapp' };
