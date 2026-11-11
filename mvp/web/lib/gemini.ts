/**
 * Cliente mínimo de la API de Google Gemini (REST, sin SDK).
 * La clave se lee de la variable de entorno GEMINI_API_KEY (secreto de Vercel);
 * nunca se envía al navegador.
 */
const ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models";

export interface OpcionesGemini {
  apiKey: string;
  modelo?: string;
  timeoutMs?: number;
}

export async function generarConGemini(
  systemPrompt: string,
  mensajeUsuario: string,
  { apiKey, modelo = "gemini-2.5-flash", timeoutMs = 6000 }: OpcionesGemini,
): Promise<string> {
  const controlador = new AbortController();
  const temporizador = setTimeout(() => controlador.abort(), timeoutMs);
  try {
    const resp = await fetch(`${ENDPOINT}/${encodeURIComponent(modelo)}:generateContent`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-goog-api-key": apiKey },
      signal: controlador.signal,
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: systemPrompt }] },
        contents: [{ role: "user", parts: [{ text: mensajeUsuario }] }],
        generationConfig: {
          temperature: 0.2,
          maxOutputTokens: 600,
          thinkingConfig: { thinkingBudget: 0 },
        },
      }),
    });
    if (!resp.ok) {
      throw new Error(`Gemini respondió ${resp.status}`);
    }
    const datos = (await resp.json()) as {
      candidates?: { content?: { parts?: { text?: string }[] } }[];
    };
    const texto = datos.candidates?.[0]?.content?.parts?.map((p) => p.text ?? "").join("").trim();
    if (!texto) throw new Error("Gemini devolvió una respuesta vacía");
    return texto;
  } finally {
    clearTimeout(temporizador);
  }
}
