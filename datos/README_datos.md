# Catálogo y Documentación de Fuentes de Datos

**Proyecto:** Lunetra IA — Asistente Inteligente de Combustibles  
**Equipo:** Stefano Canales · Carlos Flores · Carlos Alcazar · Miguel Ángel Mori  
**Curso:** AD5018 — Inteligencia Artificial para Negocios (UTEC, Framework PROMPT v2.0)  
**Ubicación:** `datos/`  

---

## 1. Inventario de Archivos en el Directorio

El directorio de datos contiene los siguientes insumos verificados:

| Archivo | Tamaño en Disco | Filas / Dimensiones | Descripción del Contenido | Formato |
|---|---|---|---|:---:|
| `precios_combustibles_anonimizados_20260301_part1.csv` | 29.6 MB | 497,156 filas · 11 columnas | Precios diarios por estación de servicio a nivel nacional (59 días: 01/01/2026 al 28/02/2026). Identificador de grifo anonimizado (`ANON_CO_LOCAL_VENTA`). | CSV |
| `precios_combustibles_datos_crudos.csv` | 1.1 MB | 11,227 filas · 8 columnas | Serie histórica consolidada de precios promedio departamentales mensuales (80 meses continuos: ene 2020 – ago 2026) en 24 departamentos. | CSV |
| `historico_precios_combustibles_peru_2020_2026.xlsx` | 337 KB | 4 hojas de cálculo | Versión consolidada en Excel con hojas: `Resumen`, `Promedio Nacional` (80×20), `Lima` (80×16) y `Datos Crudos` (11,227×7). | XLSX |

> **Nota Metodológica de Integridad:**  
> Los archivos `precios_combustibles_datos_crudos.csv` e `historico_precios_combustibles_peru_2020_2026.xlsx` provienen exactamente de la misma fuente documental. En el marco del inventario del curso cuentan como **un único conjunto de datos con dos presentaciones**, no como dos conjuntos independientes.

---

## 2. Origen Oficial y Entidad Proveedora

- **Organismo Emisor:** Organismo Supervisor de la Inversión en Energía y Minería (**Osinergmin**) — División de Supervisión Regional, Supervisión de Comercialización de Hidrocarburos Líquidos.
- **Sistemas de Registro:**
  - Sistema de Control de Órdenes de Pedido (**SCOP-DOCS**).
  - Sistema de Información de Precios de Combustibles (**PRICE**), plataforma base que alimenta la aplicación ciudadana *Facilito*.
- **Patrón Oficial de URL para Reportes Mensuales:**
  Los reportes mensuales en formato PDF se publican siguiendo la estructura estándar:
  ```
  https://www.osinergmin.gob.pe/seccion/centro_documental/hidrocarburos/SCOP/SCOP-DOCS/<AÑO>/Reporte-Mensual-Precios-<Mes>-<Año>.pdf
  ```
  *Ejemplo representativo:*
  `https://www.osinergmin.gob.pe/seccion/centro_documental/hidrocarburos/SCOP/SCOP-DOCS/2024/Reporte-Mensual-Precios-Mayo-2024.pdf`

---

## 3. Licencia y Uso de la Información

- **Naturaleza Jurídica:** Información pública de libre acceso del Estado Peruano en el marco del Texto Único Ordenado de la Ley N.° 27806 (Ley de Transparencia y Acceso a la Información Pública) y la Política Nacional de Datos Abiertos coordinada por la Presidencia del Consejo de Ministros (PCM).
- **Finalidad Académica y de Investigación:** Los datos son procesados exclusivamente con fines educativos, de desarrollo de producto analítico y sin vulneración de derechos comerciales ni de propiedad intelectual.

---

## 4. Política de Versionamiento en el Repositorio Git

- **Archivos Menores a 5 MB:** `precios_combustibles_datos_crudos.csv` y `historico_precios_combustibles_peru_2020_2026.xlsx` se versionan directamente en el árbol de Git.
- **Archivo Mayor (`part1.csv`, 29.6 MB):**
  - Dado que GitHub permite archivos individuales de hasta 100 MB (recomendando no superar los 50 MB para agilidad de clonado), este archivo puede versionarse directamente en el repositorio o gestionarse mediante Git LFS (*Large File Storage*).
  - En caso de clonar el repositorio en entornos con ancho de banda restringido, el script `analisis/perfilado_datos.py` está configurado para buscar el archivo en la ruta local `datos/` o alternativamente en la carpeta superior `Downloads/`.

---

## 5. Diccionario Básico de Columnas

### Archivo Diario (`part1.csv`)
1. `fecha_emision`: Fecha del reporte en el sistema minorista.
2. `fecha_corte`: Fecha de corte administrativo.
3. `id`: Identificador secuencial del registro.
4. `fe_eval`: Fecha de evaluación del precio (formato numérico `YYYYMMDD`).
5. `g_premium`: Precio de Gasolina Premium (Soles por galón).
6. `g_regular`: Precio de Gasolina Regular (Soles por galón).
7. `diesel`: Precio de Diésel vehicular (Soles por galón).
8. `gnv`: Precio de Gas Natural Vehicular (Soles por $m^3$ o $kg$).
9. `glp_g`: Precio de Gas Licuado de Petróleo a granel vehicular (Soles por galón).
10. `glp_e`: Precio de Gas Licuado de Petróleo envasado (Soles por $kg$).
11. `ANON_CO_LOCAL_VENTA`: Código alfanumérico anonimizado correspondiente al establecimiento de venta (persona jurídica).

### Archivo Mensual Departamental (`datos_crudos.csv`)
1. `anio`: Año calendario (2020 a 2026).
2. `mes_num`: Número del mes (1 a 12).
3. `mes`: Nombre textual del mes.
4. `departamento`: Uno de los 24 departamentos del Perú.
5. `combustible`: Denominación original según el reporte de Osinergmin.
6. `precio_soles_galon`: Precio promedio registrado para el departamento y mes.
7. `archivo_fuente`: Nombre del reporte PDF de origen en SCOP-DOCS.
8. `combustible_norm`: Denominación normalizada post-regulación.
