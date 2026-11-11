import Asistente from "@/components/Asistente";
import { DEPARTAMENTOS, MODELO } from "@/lib/modelo";

export default function Inicio() {
  const departamentos = DEPARTAMENTOS.map((d) => d.departamento);
  const mesBase = DEPARTAMENTOS[0]?.mes_base ?? "";
  return (
    <main className="contenedor">
      <div className="aviso-ia" role="note">
        <span className="aviso-ia__icono" aria-hidden>
          ✦
        </span>
        <p>
          <strong>Estás usando un asistente de Inteligencia Artificial.</strong> Sus
          recomendaciones son estimaciones estadísticas, no garantías de precio.
        </p>
      </div>

      <header className="cabecera">
        <p className="marca">Lunetra IA</p>
        <h1>¿Lleno hoy o espero?</h1>
        <p className="bajada">
          Te decimos si conviene cargar gasolina hoy o esperar, y cuánto es un precio justo por
          galón en tu zona.
        </p>
      </header>

      <Asistente departamentos={departamentos} />

      <footer className="pie">
        <p>
          <strong>Tus datos:</strong> no pedimos nombre, correo, placa ni ubicación GPS. Solo
          usamos el departamento y el nivel de tanque que eliges, y no los guardamos asociados a
          ti (Ley N.° 29733 de Protección de Datos Personales).
        </p>
        <p>
          Modelo: regresión logística regularizada entrenada con precios oficiales de Osinergmin
          (último mes observado: {mesBase.slice(0, 7)}). En el test ciego 2026 detecta el{" "}
          {Math.round(MODELO.metricas_test.recall_sube_umbral * 100)}% de las subidas y supera
          al baseline de persistencia (Macro-F1 {MODELO.metricas_test.macro_f1_umbral.toFixed(2)}{" "}
          vs {MODELO.metricas_test.baseline_persistencia_macro_f1.toFixed(2)}).
        </p>
        <p>Proyecto académico AD5018 · UTEC · Equipo Los-1000</p>
      </footer>
    </main>
  );
}
