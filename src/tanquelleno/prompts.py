"""
===============================================================================
PROYECTO: TanqueLleno AI — Fase M (Modelado)
ARCHIVO:  src/tanquelleno/prompts.py
DESCRIPCIÓN:
    System Prompt del componente generativo G1 y auditoría anti-alucinación.

    El System Prompt es la transcripción literal del congelado en la Fase O
    (plantilla 3). `auditar_alucinacion_numerica()` es el mecanismo que hace
    verificable el KR2: extrae toda cifra monetaria del texto generado y exige
    que cada una provenga del payload. Sin esa verificación, "0% de
    alucinaciones" sería una afirmación sin evidencia.
===============================================================================
"""

from __future__ import annotations

import re

from . import config

SYSTEM_PROMPT_G1 = """Eres TanqueLleno AI, un asistente experto y transparente diseñado para orientar a conductores particulares de Lima Metropolitana en la optimización del gasto en combustible.

Tu misión es transformar los resultados cuantitativos de nuestro modelo analítico en una recomendación clara, directa, empática y accionable en lenguaje natural.

REGLAS DE OBLIGATORIO CUMPLIMIENTO:

1. INFORMACIÓN SOBRE INTERACCIÓN CON IA:
   - Debes incluir siempre al inicio o cierre el aviso: "Este reporte es generado por el asistente de IA de TanqueLleno AI a partir de estimaciones probabilísticas".

2. PROHIBICIÓN TOTAL DE INVENTAR PRECIOS O DIRECCIONES:
   - Utiliza ÚNICAMENTE los números y la tendencia proporcionados en el contexto (payload).
   - Jamás inventes valores de combustible, marcas de grifos, distritos específicos ni garantices un precio futuro.

3. DECLARACIÓN OBLIGATORIA DE CONFIANZA:
   - Si el atributo 'confianza' es "BAJA" o la probabilidad está entre 0.40 y 0.55, debes advertir explícitamente al conductor: "El mercado se encuentra en una zona de alta incertidumbre estadística; no se descartan fluctuaciones imprevistas".

4. NATURALEZA ESTIMATIVA Y NO GARANTÍA:
   - Recuerda siempre al usuario que esta proyección es una estimación estadística y no una garantía financiera contractual. Factores geopolíticos o decretos de urgencia pueden alterar las tendencias.

5. ESTRUCTURA DE RESPUESTA:
   - [Diagnóstico de Tendencia]: Señala con claridad si la presión proyectada es al alza, a la baja o de estabilidad.
   - [Acción Recomendada]: Si la tendencia es ALZA y el conductor tiene tanque medio o bajo, recomiéndale tanquear antes del cierre de semana. Si es BAJA o ESTABLE, sugiere recargar solo lo necesario o esperar.
   - [Banda de Precio de Referencia]: Utiliza el P10 y P90 suministrados para enseñarle cuál es un precio competitivo en su departamento (ej. "Encuentra un grifo que expenda cerca de S/ {p10_mercado} y evita pagar más de S/ {p90_mercado}").

FORMATO Y TONO:
- Tono: Profesional, directo, cercano, libre de jerga técnica compleja.
- Extensión máxima: 3 párrafos concisos."""

AVISO_IA = (
    "Este reporte es generado por el asistente de IA de TanqueLleno AI a partir "
    "de estimaciones probabilísticas"
)
ADVERTENCIA_INCERTIDUMBRE = (
    "El mercado se encuentra en una zona de alta incertidumbre estadística; "
    "no se descartan fluctuaciones imprevistas"
)

# Captura importes como "S/ 14.30", "S/14.3" o "14.30 soles".
_PATRON_MONTO = re.compile(r"(?:S/\.?\s*|\bsoles?\s+)?(\d+[.,]\d{1,2})\b", re.IGNORECASE)


def construir_mensaje_usuario(payload: dict, nivel_tanque: str = "medio") -> str:
    """Serializa el payload en el mensaje de usuario que acompaña al System Prompt."""
    faltantes = [c for c in config.CAMPOS_PAYLOAD if c not in payload]
    if faltantes:
        raise ValueError(f"El payload no cumple el contrato; faltan campos: {faltantes}")

    lineas = [f"- {campo}: {payload[campo]}" for campo in config.CAMPOS_PAYLOAD]
    lineas.append(f"- nivel_tanque_usuario: {nivel_tanque}")
    return (
        "Contexto cuantitativo del modelo analítico (única fuente de cifras "
        "permitida):\n" + "\n".join(lineas)
    )


def valores_permitidos(payload: dict) -> set[str]:
    """Cifras que el generador puede mencionar sin incurrir en alucinación.

    Incluye cada valor del payload en sus formatos equivalentes de dos y una
    decimal, para no marcar como inventado un "S/ 14.3" que en realidad es el
    14.30 del payload.
    """
    permitidos: set[str] = set()
    for valor in payload.values():
        if not isinstance(valor, (int, float)) or isinstance(valor, bool):
            continue
        permitidos.add(f"{float(valor):.2f}")
        permitidos.add(f"{float(valor):.1f}")
        permitidos.add(str(valor))
    permitidos.add(f"{float(config.GALONES_POR_TANQUEADA):.2f}")
    permitidos.add(str(config.GALONES_POR_TANQUEADA))
    return permitidos


def requiere_advertencia(payload: dict) -> bool:
    """Indica si el System Prompt obliga a declarar incertidumbre."""
    prob = float(payload.get("probabilidad_alza", 0.0))
    return (
        str(payload.get("confianza", "")).upper() == "BAJA"
        or config.ZONA_INCERTIDUMBRE[0] <= prob <= config.ZONA_INCERTIDUMBRE[1]
    )


def auditar_alucinacion_numerica(texto: str, payload: dict) -> dict:
    """Verifica que toda cifra del texto generado provenga del payload.

    Este es el instrumento de medición del KR2. Además de las cifras, comprueba
    las dos frases que el System Prompt declara obligatorias.

    Returns:
        dict con `sin_alucinacion` (bool), la lista de `cifras_inventadas`,
        y las banderas de cumplimiento de avisos.
    """
    permitidos = valores_permitidos(payload)
    encontradas = [m.group(1).replace(",", ".") for m in _PATRON_MONTO.finditer(texto)]

    inventadas = [
        cifra for cifra in encontradas
        if f"{float(cifra):.2f}" not in permitidos and cifra not in permitidos
    ]

    necesita = requiere_advertencia(payload)
    incluye_aviso = AVISO_IA.lower() in texto.lower()
    incluye_advertencia = ADVERTENCIA_INCERTIDUMBRE.lower() in texto.lower()

    return {
        "sin_alucinacion": not inventadas,
        "cifras_detectadas": encontradas,
        "cifras_inventadas": sorted(set(inventadas)),
        "incluye_aviso_ia": incluye_aviso,
        "requiere_advertencia_incertidumbre": necesita,
        "incluye_advertencia_incertidumbre": incluye_advertencia,
        "cumple_contrato": (
            not inventadas
            and incluye_aviso
            and (not necesita or incluye_advertencia)
        ),
    }


def redactar_sin_llm(payload: dict, nivel_tanque: str = "medio") -> str:
    """Genera la recomendación con plantillas deterministas, sin llamar al LLM.

    Cumple dos funciones: es el modo de respaldo cuando la API del LLM no está
    disponible o excede los 3 segundos del KR3, y es el caso de prueba de
    referencia para `auditar_alucinacion_numerica()`, ya que por construcción
    solo puede emitir cifras del payload.
    """
    tendencia = str(payload["tendencia_predicha"]).upper()
    prob = float(payload["probabilidad_alza"])

    if tendencia == "SUBE":
        diagnostico = (
            f"La presión proyectada para {payload['periodo']} en {payload['departamento']} "
            f"es al alza, con una probabilidad estimada de {prob:.2f}."
        )
        accion = (
            "Con el tanque medio o bajo, conviene abastecer antes del cierre de semana "
            "en lugar de esperar al próximo ajuste."
            if nivel_tanque in ("medio", "bajo")
            else "Con el tanque lleno no necesitas actuar hoy; mantén la próxima carga a la vista."
        )
    elif tendencia == "BAJA":
        diagnostico = (
            f"La presión proyectada para {payload['periodo']} en {payload['departamento']} "
            f"es a la baja (probabilidad de alza: {prob:.2f})."
        )
        accion = "Carga solo lo necesario para moverte y espera al siguiente ajuste."
    else:
        diagnostico = (
            f"Para {payload['periodo']} en {payload['departamento']} se proyecta "
            f"estabilidad (probabilidad de alza: {prob:.2f})."
        )
        accion = "No hay urgencia por adelantar la carga; abastece según tu rutina habitual."

    banda = (
        f"Busca un grifo que expenda cerca de S/ {payload['p10_mercado']} y evita pagar "
        f"más de S/ {payload['p90_mercado']}; la mediana del mercado está en "
        f"S/ {payload['p50_mediana']}."
    )

    cierre = (
        "Esta proyección es una estimación estadística, no una garantía financiera: "
        "factores geopolíticos o decretos de urgencia pueden alterar la tendencia. "
        f"{AVISO_IA}."
    )

    partes = [f"{diagnostico} {accion}", banda]
    if requiere_advertencia(payload):
        partes.append(f"{ADVERTENCIA_INCERTIDUMBRE}.")
    partes.append(cierre)
    return "\n\n".join(partes)
