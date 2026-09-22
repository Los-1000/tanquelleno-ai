# Guion de Sustentación — Deck de Presentación Lunetra IA (PC1)

**Proyecto:** Lunetra IA — Asistente Inteligente de Combustibles  
**Curso:** AD5018 — Inteligencia Artificial para Negocios (UTEC, Framework PROMPT v2.0)  
**Evaluación:** Práctica Calificada 1 (PC1) · Fases P, R y O  
**Equipo:** Stefano Canales · Carlos Flores · Carlos Alcazar · Miguel Ángel Mori  
**Repositorio GitHub:** [github.com/Los-1000/tanquelleno-ai](https://github.com/Los-1000/tanquelleno-ai)  
**Fecha de Sustentación:** 19 de septiembre de 2026  
**Duración Estimada:** 10 minutos (13 diapositivas optimizadas)  

---

### Diapositiva 01 / 13: Portada
- **Título en Lámina:** Lunetra IA
- **Subtítulo:** Asistente Inteligente para la Optimización del Gasto en Combustibles
- **Datos en Lámina:** Stefano Canales · Carlos Flores · Carlos Alcazar · Miguel Ángel Mori | Inteligencia Artificial para Negocios · 19 de septiembre de 2026 | UTEC 2026.
- **Mensaje Central del Ponente:**  
  "Buenos días profesor y miembros del jurado. Hoy presentamos **Lunetra IA**, un asistente de inteligencia artificial concebido para resolver la asimetría y opacidad en el mercado de combustibles de Lima Metropolitana, permitiendo a los conductores responder a una sola pregunta con precisión y ahorro real."

---

### Diapositiva 02 / 13: El Problema
- **Título en Lámina:** EL PROBLEMA
- **Encabezado:** Todos los que manejan en Lima se hacen la misma pregunta, y nadie tiene la respuesta: **"¿Lleno hoy o espero?"**
- **Puntos Clave (Hoy Pasa Esto):**
  1. **Se carga por costumbre:** En el grifo de siempre y el día que uno se acuerda, sin comparar nada.
  2. **El precio sube sin aviso:** Uno se entera recién cuando ya está frente al surtidor pagando el incremento.
  3. **Nadie compara precios:** Los datos existen y son públicos, pero están confinados en tablas densas que nadie lee antes de salir.
- **Mensaje Central del Ponente:**  
  "El problema de los conductores no es la falta de una aplicación tecnológica, sino la incertidumbre económica. Cada semana, miles de personas toman decisiones a ciegas basadas en inercia, pagando de más sin saberlo."

---

### Diapositiva 03 / 13: Para Quién lo Hacemos
- **Título en Lámina:** PARA QUIÉN LO HACEMOS
- **Encabezado:** Una persona, no "el mercado"
- **Subtexto:** "Si el usuario es 'todos', el producto no sirve para nadie. El nuestro es así de concreto:"
- **Perfil de Persona:**
  - **Lima:** Vive y maneja dentro de la ciudad.
  - **Todos los días:** Usa su auto para trabajar, no de paseo (25 a 40 km diarios).
  - **8 galones:** Es lo que carga en una semana normal de Gasolina Regular (G90) o Premium.
  - **Su bolsillo:** Nadie le reembolsa la gasolina; asume el 100% del gasto de su presupuesto personal.
- **Mensaje Central del Ponente:**  
  "Delimitamos estrictamente a nuestro usuario. No hablamos genéricamente de 'los peruanos' ni de flotas subsidiadas. Diseñamos para el trabajador limeño que usa su vehículo particular a diario y siente directamente el impacto en su bolsillo."

---

### Diapositiva 04 / 13: Lo que Encontramos en los Datos — 1 de 2
- **Título en Lámina:** LO QUE ENCONTRAMOS EN LOS DATOS — 1 DE 2
- **Encabezado:** El mismo día, el mismo combustible, dos precios muy distintos
- **Evidencia Cuantitativa Oficial (Corte 28-feb-2026, 8,825 grifos a nivel nacional):**
  - **El grifo más barato (P10):** **S/ 13.39** por galón de gasolina regular.
  - **La diferencia:** **S/ 2.12 por galón**, el mismo día y a la misma hora.
  - **El grifo más caro (P90):** **S/ 15.70** por galón de gasolina regular.
  - *Conclusión:* "No es la inflación ni el dólar: es simplemente en qué grifo cargas."
- **Mensaje Central del Ponente:**  
  "Al analizar los datos oficiales de Osinergmin comprobamos un hecho contundente: la dispersión transversal entre grifos en un mismo día alcanza S/ 2.12 por galón. La mayor oportunidad de ahorro no está en predecir variaciones de centavos, sino en evitar la cola cara del mercado."

---

### Diapositiva 05 / 13: Cuánto Cuesta No Saberlo
- **Título en Lámina:** CUÁNTO CUESTA NO SABERLO
- **Encabezado:** Cargar siempre en el grifo caro cuesta **S/ 814 al año**
- **Impacto Económico Calculado:**
  - **Por cada tanqueada:** **S/ 17 de más**, en una carga típica de 8 galones ($8 \times \text{S/ } 2.12 = \text{S/ } 16.96$).
  - **Al mes:** **S/ 68** cargando una vez por semana.
  - **Al año:** **S/ 814**, equivalente a casi un sueldo mínimo, solo por desconocer la distribución de precios.
- **Mensaje Central del Ponente:**  
  "Aquí radica la justificación económica de nuestro proyecto: la asimetría informativa le drena S/ 68 mensuales a un conductor limeño. Reducir esa brecha genera un impacto directo e inmediato en su economía familiar."

---

### Diapositiva 06 / 13: Lo que Encontramos en los Datos — 2 de 2
- **Título en Lámina:** LO QUE ENCONTRAMOS EN LOS DATOS — 2 DE 2
- **Encabezado:** Los precios se mueven lento. Por eso se pueden anticipar.
- **Evidencia Cuantitativa:**
  - **96 de cada 100 grifos** cobran hoy exactamente lo mismo que cobraron ayer (Hallazgo H1: 96.02% de inercia).
  - En un día cualquiera, solo **4 grifos cambian** de precio.
  - **Por qué es buena noticia:** Si los precios fueran caóticos, no habría nada que anticipar. Como se mueven de manera gradual e inercial, sí es viable avisar con tiempo al usuario.
  - **Lo que esto significa:** El grifo barato de hoy también será barato mañana. Conocer la tendencia y la banda justa te sirve para toda la semana.
- **Mensaje Central del Ponente:**  
  "La alta inercia diaria confirma que no debemos construir alertas de alta frecuencia que saturen al usuario, sino un modelo robusto que anticipe los momentos de ajuste mayorista."

---

### Diapositiva 07 / 13: De Dónde Salen Nuestros Datos
- **Título en Lámina:** DE DÓNDE SALEN NUESTROS DATOS
- **Encabezado:** Todo viene de datos públicos que cualquiera puede verificar
- **Fuente Oficial:** **Osinergmin**, división de supervisión regional (sistemas SCOP-DOCS y PRICE). Sin datos comprados, sin encuestas informales y sin cifras inventadas.
- **Cifras de Respaldo:**
  - **Cuántos grifos:** **8,825** estaciones de servicio en todo el país.
  - **Cuántos precios:** **497 mil** registros diarios auditados y saneados (16 valores fuera de rango filtrados).
  - **Cuánto historial:** **6 años** de precios mes a mes (80 meses continuos, 2020 a 2026).
  - **Cuánto costó:** **S/ 0**, información pública y transparente del Estado Peruano.
- **Mensaje Central del Ponente:**  
  "Nuestra solución opera sobre datos abiertos auditables del regulador oficial. Garantizamos reproducibilidad absoluta y trazabilidad desde la fuente primaria."

---

### Diapositiva 08 / 13: Nuestra Solución
- **Título en Lámina:** NUESTRA SOLUCIÓN
- **Encabezado:** Una sola pregunta, respondida bien: **"Carga hoy"** o **"Puedes esperar"**
- **Propuesta de Valor:**  
  Eso es todo lo que el conductor necesita escuchar. Detrás hay seis años de datos; adelante, una frase clara.
- **Pilares de Arquitectura:**
  - **01 | Lee los precios:** Revisa las tendencias oficiales de los grifos del país.
  - **02 | Aprende el patrón:** Compara con seis años de historia y variables de mercado para determinar hacia dónde va la presión de precios.
- **Mensaje Central del Ponente:**  
  "No abrumamos al usuario con dashboards complejos. Transformamos modelos de clasificación y rezagos de mercado en una recomendación ejecutable en menos de dos segundos."

---

### Diapositiva 09 / 13: Cómo Funciona
- **Título en Lámina:** CÓMO FUNCIONA
- **Encabezado:** Cuatro pasos, sin tecnicismos
- **Flujo Operativo (Patrón 1: Modelo $\rightarrow$ Lenguaje):**
  1. **Tú eliges:** Tu ciudad y el combustible que usas (Regular o Premium). Dos toques en pantalla.
  2. **Lunetra revisa:** Seis años de precios de tu zona en Supabase en milisegundos.
  3. **Calcula:** Evalúa si es más probable que el precio suba o baje el próximo mes mediante Regresión Logística Regularizada (A2) calibrada.
  4. **Te responde:** "Carga hoy" o "Puedes esperar", indicando además el rango de precio justo (P10 a P90) vía Gemini Flash.
- **Mensaje Central del Ponente:**  
  "El usuario interactúa con una interfaz simple en Next.js. En el backend, Vercel Serverless ejecuta la inferencia tabular, aplica el umbral de decisión asimétrico y el motor generativo redacta la recomendación final."

---

### Diapositiva 10 / 13: La App en el Celular & Por Qué Hace Falta un Modelo
- **Título en Lámina:** LA APP EN EL CELULAR
- **Subtítulo:** Así se vería tu respuesta (Maqueta ilustrativa con datos reales)
- **Mensaje de la App:** **"Conviene cargar hoy"** | Rango oficial: S/ 13.39 a S/ 15.70 por galón.
- **Fundamento Metodológico (Por Qué Hace Falta Machine Learning):**
  1. **El precio llega con retraso:** El precio del crudo y derivados internacionales tarda de 2 a 6 semanas en reflejarse en el surtidor. Una regla fija ("si sube el petróleo, sube el grifo") yerra sistemáticamente.
  2. **Los dos errores no cuestan igual:** No avisar una subida le cuesta S/ 4.00 al conductor; avisar una que no llega solo le cuesta S/ 0.80. El modelo aprende a preferir el error barato mediante calibración del umbral ($P^* = 0.25$). Una hoja de cálculo no puede hacer esto.
- **Mensaje Central del Ponente:**  
  "Aquí demostramos por qué la IA es indispensable: captura relaciones temporales de rezagos de mercado y optimiza la decisión en favor del bolsillo del usuario penalizando los falsos negativos."

---

### Diapositiva 11 / 13: Lo que NO Hace
- **Título en Lámina:** LO QUE NO HACE
- **Encabezado:** Prometemos poco, y lo cumplimos bien
- **Límites Rígidos de Alcance (Transparencia Total):**
  - **Sin GPS:** No busca el grifo más cercano: los reportes oficiales están anonimizados y no traen coordenadas de latitud/longitud.
  - **Sin rutas:** No traza caminos ni compite con navegadores satelitales (Google Maps / Waze).
  - **Sin pagos:** No cobra ni gestiona transferencias dentro de la app; solo asesora.
  - **Sin instalar nada:** No requiere tiendas de aplicaciones (App Store / Play Store). Es una Web App moderna en Next.js alojada en Vercel, accesible al instante desde cualquier navegador móvil.
- **Mensaje Central del Ponente:**  
  "Evitamos la trampa clásica de prometer funcionalidades imposibles que descarrilan el proyecto. Nuestro alcance es honesto, viable y enfocado al 100% en la predicción y el ahorro."

---

### Diapositiva 12 / 13: Qué Nos Falta
- **Título en Lámina:** QUÉ NOS FALTA
- **Encabezado:** El camino que sigue, semana a semana
- **Hoja de Ruta (Semanas 7 a 13):**
  - **Semanas 7 a 9 (Fase M):** Ingestión macroeconómica, entrenamiento de Regresión Logística Regularizada y calibración del umbral asimétrico ($P^* = 0.25$) con datos 2020–2025.
  - **Semana 10 (Fase M - Despliegue):** Publicamos la aplicación web en **Vercel + Supabase** (Next.js y base de datos PostgreSQL Cloud): producción profesional, alta disponibilidad y sub-segundo de latencia.
  - **Semana 11 (Fase M - Piloto):** Pruebas guiadas con 10 conductores particulares de Lima para calibrar usabilidad.
  - **Semanas 12 y 13 (Fase P2 y T):** Medición de KRs frente al baseline de persistencia en test ciego (2026), llenado de Plantilla 4 y sustentación final.
- **Mensaje Central del Ponente:**  
  "Nuestro cronograma mitiga el mayor riesgo del curso desplegando en producción en la Semana 10. Tenemos asignadas las responsabilidades de datos, modelado e infraestructura en Vercel + Supabase para llegar con éxito a la PC2."

---

### Diapositiva 13 / 13: Cierre y Preguntas
- **Título en Lámina:** ¡Muchas Gracias!
- **Equipo:** Stefano Canales · Carlos Flores · Carlos Alcazar · Miguel Ángel Mori
- **Curso:** AD5018 — Inteligencia Artificial para Negocios · 19 de septiembre de 2026
- **Repositorio Oficial:** `https://github.com/Los-1000/tanquelleno-ai`
- **Mensaje Central del Ponente:**  
  "Lunetra IA demuestra cómo la inteligencia artificial aplicada a datos públicos abiertos resuelve un dolor cotidiano tangible. Quedamos a disposición del jurado para sus preguntas."
