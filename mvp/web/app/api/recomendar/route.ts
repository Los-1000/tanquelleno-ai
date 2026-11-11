import { NextResponse } from "next/server";
import { recomendar } from "@/lib/recomendar";
import { buscarDepartamento, type NivelTanque } from "@/lib/modelo";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const NIVELES: NivelTanque[] = ["bajo", "medio", "lleno"];

export async function POST(req: Request) {
  let cuerpo: unknown;
  try {
    cuerpo = await req.json();
  } catch {
    return NextResponse.json({ error: "El cuerpo debe ser JSON." }, { status: 400 });
  }
  const { departamento, nivel_tanque } = (cuerpo ?? {}) as Record<string, unknown>;

  if (typeof departamento !== "string" || !buscarDepartamento(departamento)) {
    return NextResponse.json(
      { error: "Elige un departamento de la lista." },
      { status: 400 },
    );
  }
  if (typeof nivel_tanque !== "string" || !NIVELES.includes(nivel_tanque as NivelTanque)) {
    return NextResponse.json(
      { error: "Indica si tu tanque está bajo, medio o lleno." },
      { status: 400 },
    );
  }

  try {
    const r = await recomendar(departamento, nivel_tanque as NivelTanque);
    // Solo se registran datos técnicos no personales (Ley N.° 29733).
    console.log(JSON.stringify({
      evento: "recomendacion",
      departamento: r.payload.departamento,
      tendencia: r.payload.tendencia_predicha,
      fuente_texto: r.fuente_texto,
      cumple_contrato: r.auditoria.cumple_contrato,
      latencia_ms: r.latencia_ms,
    }));
    return NextResponse.json(r);
  } catch (e) {
    console.error(e);
    return NextResponse.json(
      { error: "No pudimos calcular la recomendación. Intenta de nuevo en un momento." },
      { status: 500 },
    );
  }
}
