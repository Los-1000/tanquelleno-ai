# Fuente de Datos: Grifos Georreferenciados de Lima y Callao

**Incorporada en:** Fase M (Semana 7)
**Relevancia:** es la fuente que levanta el semáforo ROJO de geolocalización declarado en la Fase R.

---

## 1. Por qué importa esta fuente

La Plantilla 2 (Data Readiness) declaró que el archivo nacional anonimizado **carece totalmente de variables de ubicación**, y en consecuencia la Plantilla 1 delimitó el alcance del MVP excluyendo mapas, rutas GPS y la función de "grifo más cercano".

Esta fuente aporta, por cada estación de Lima Metropolitana y Callao:

- `lat` / `lon` — coordenadas exactas
- `distrito` — 39 distritos identificados
- `marca` — cadena comercial
- `descuento` — descuento de aplicativo en soles por galón, variable que **no existía en ninguna fuente previa**

Para Lima y Callao, por tanto, la restricción de alcance deja de aplicar. Para el resto del país sigue vigente.

---

## 2. Archivos

| Archivo | Filas | Descripción |
|---|---:|---|
| `premium_lima_callao_20260918.csv` | 199 | Corte transversal del 18/09/2026: una fila por estación. |
| `historico_grifos_lima_callao.csv` | 796 | Cuatro snapshots (16, 17 y 18 de setiembre de 2026) × 199 estaciones. |
| `mymaps_lima_callao_20260918.csv` | 199 | El mismo corte, con la columna `Nombre` preformateada para importar en Google MyMaps. Es una presentación, no un conjunto de datos independiente. |

---

## 3. Diccionario de columnas

| Columna | Tipo | Descripción |
|---|:---:|---|
| `scraped_at` | ISO-8601 con offset | Momento de captura. Solo en el histórico. Ej.: `2026-09-18T14:01:39-0500` |
| `codigo_osinergmin` | texto | Código de registro de la estación ante Osinergmin. Clave primaria. |
| `marca` | texto | Cadena comercial (Repsol, COESTI/Primax, Primax afiliada). |
| `zona` | texto | `LIMA` o `CALLAO`. |
| `distrito` | texto | Distrito de la estación. |
| `direccion` | texto | Dirección declarada. |
| `lat`, `lon` | decimal | Coordenadas en grados decimales (WGS 84). |
| `premium_lista` | S//galón | Precio de lista de gasolina premium. |
| `descuento` | S//galón | Descuento por aplicativo de la marca. |
| `premium_final` | S//galón | `premium_lista − descuento`: lo que paga el conductor. |
| `regular_lista` | S//galón | Precio de lista de gasolina regular. |
| `diesel_lista` | S//galón | Precio de lista de diésel. |

---

## 4. Cobertura y límites declarados

- **199 estaciones**, frente a las ~8,825 del padrón nacional. Es una muestra de las cadenas con aplicativo, **no un censo** del mercado limeño.
- **3 marcas únicamente.** No incluye Petroperú, Pecsa ni estaciones independientes, que son precisamente las que suelen poblar la cola barata del mercado. Cualquier percentil calculado sobre esta fuente describe el mercado de marca, no el mercado completo.
- **Serie temporal insuficiente.** Cuatro snapshots en tres días no permiten modelar dinámica de precios por grifo. La fuente se usa como corte transversal; para convertirla en serie hay que programar la captura diaria (pendiente 5 de la Fase M).
- `diesel_lista` y `regular_lista` tienen valores ausentes en las estaciones que no expenden ese producto.

---

## 5. Defecto conocido del archivo histórico

El scraper hace *append* de cada snapshot sin escribir el salto de línea final, de modo que la última fila de un snapshot queda pegada a la primera del siguiente:

```
..."26.99""2026-09-16T22:06:15-0500","158833","Repsol",...
```

Leer el archivo con `pd.read_csv()` directamente aborta con `ParserError: Expected 13 fields in line 200, saw 25`, o descarta silenciosamente una fila por frontera.

**No leer estos archivos con `pd.read_csv()` directamente.** Usar siempre:

```python
from tanquelleno.datos import cargar_historico_lima_callao
historico = cargar_historico_lima_callao()   # repara las uniones al leer
```

El test `test_historico_del_scraper_se_lee_completo` verifica que los cuatro snapshots contengan los mismos 199 grifos.

---

## 6. Naturaleza jurídica

Precios de venta al público exhibidos obligatoriamente por las estaciones y reportados a Osinergmin en el marco del Sistema PRICE. Información de acceso público, procesada con fines exclusivamente académicos.
