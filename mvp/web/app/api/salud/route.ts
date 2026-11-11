import { NextResponse } from "next/server";
import { MODELO, DEPARTAMENTOS } from "@/lib/modelo";

export const dynamic = "force-dynamic";

/** Chequeo de disponibilidad para la evidencia del KR3. */
export function GET() {
  return NextResponse.json({
    estado: "ok",
    modelo_version: MODELO.version,
    departamentos: DEPARTAMENTOS.length,
    llm_configurado: Boolean(process.env.GEMINI_API_KEY),
  });
}
