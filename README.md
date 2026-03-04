# Data_Mining_Pset2_Gabriela_Coloma

**Problem Set 2 - Data Mining**

**Nombre:** Gabriela Coloma  
**Código:** 00325312

---

## Resumen

El proyecto implementa un pipeline de datos para NYC TLC (Taxi & Limousine Commission) siguiendo una arquitectura medallion (Bronze → Silver → Gold). Los datos se extraen desde archivos Parquet públicos, se transforman con dbt, y se almacenan en PostgreSQL con particionamiento declarativo. La orquestación se realiza en Mage AI, desplegado con Docker Compose, y las credenciales se gestionan con Mage Secrets.

---

## Diagrama de arquitectura

<img width="500" height="463" alt="Screenshot 2026-03-04 at 1 42 21 AM" src="https://github.com/user-attachments/assets/29c56d6e-d5ac-41ce-a7b0-ca694bee1d63" />

---

## Cobertura de datos

<img width="253" height="514" alt="Screenshot 2026-03-04 at 1 47 02 AM" src="https://github.com/user-attachments/assets/e9b5259d-7624-44f5-80ec-fecfb788beaa" />

**Nota:** Proyecto ajustado a solo 2024 por limitaciones de espacio en disco.

---

## Pasos para levantar contenedores y configurar proyecto

**Clonar este repositorio:**
```bash
git clone <repo_url>
cd PSet2
```

**Levantar servicios:**
```bash
docker compose up -d
```

**Apagar servicios:**
```bash
docker compose down
```

**Servicios:**
- `warehouse`: PostgreSQL (5432)
- `warehouse_ui`: pgAdmin (8080)
- `scheduler`: Mage (6789)

**Acceso a interfaces:**
- Mage: http://localhost:6789
- pgAdmin: http://localhost:8080
  - Email: `admin@admin.com`
  - Password: `admin`

**Configurar pgAdmin (primera vez):**
1. Register Server → Name: `warehouse`
2. Connection: Host=`warehouse`, Port=`5432`, DB=`ny_taxi`, User=`root`, Pass=`root`

---

## Gestión de secretos

Todos los secretos se configuraron en Mage Secrets (Settings → Workspace → Secrets), no están en el código ni en el repo. Se llaman desde el código con la función `get_secret_value()`.

| Nombre secreto | Para qué sirve | Cada cuánto se cambia | Responsable |
|----------------|----------------|-----------------------|-------------|
| `POSTGRES_HOST` | Hostname del servidor PostgreSQL | Solo si cambia infra | Yo |
| `POSTGRES_PORT` | Puerto de conexión a Postgres | Nunca | Yo |
| `POSTGRES_DB` | Nombre de la base de datos | Solo si se crea otra | Yo |
| `POSTGRES_USER` | Usuario para entrar a Postgres | Solo si se compromete | Yo |
| `POSTGRES_PASSWORD` | Contraseña de Postgres | Cada 90 días o si hay fuga | Yo |

**Ejemplo de uso:**
```python
from mage_ai.data_preparation.shared.secrets import get_secret_value
host = get_secret_value("POSTGRES_HOST")
```

---

## Pipelines

Existen 6 pipelines principales:

### 1. `ingest_bronze_yellow`
**Propósito:** Ingesta de datos Yellow Taxi desde NYC TLC (Parquet)  
**Bloques:**
- `loader_yellow_taxi.py` (Data Loader)
- `exporter_to_postgres.py` (Data Exporter)

**Destino:** `bronze.taxi_trips`

**Parámetros:**
- `service_type`: 'yellow'
- `year`: 2024
- `month`: 1-12

**Segmentación:** Por mes  
**Límites y reintentos:** Manejo de HTTP 404 con validación de disponibilidad

---

### 2. `ingest_bronze_green`
**Propósito:** Ingesta de datos Green Taxi  
**Estructura:** Idéntica a yellow, cambia solo el `service_type` a 'green'

---

### 3. `taxi_zones`
**Propósito:** Carga del lookup de zonas NYC TLC (CSV estático)  
**Destino:** `bronze.taxi_zones`

---

### 4. `dbt_build_silver`
**Propósito:** Transformación Bronze → Silver (views)  
**Bloques:**
- `stg_taxi_zones` (DBT)
- `stg_taxi_trips` (DBT)
- `int_trips_enriched` (DBT)

**Tecnología:** dbt  
**Materialización:** Views  
**Dependencias:** Auto-detectadas por dbt con `{{ ref() }}`

---

### 5. `dbt_build_gold`
**Propósito:** Transformación Silver → Gold (tablas particionadas)  
**Bloques:**
1. `creating_partitions` (Python Data Exporter - crea estructuras particionadas)
2. `dim_date` (DBT)
3. `dim_zone` (DBT)
4. `dim_service_type` (DBT)
5. `dim_payment_type` (DBT)
6. `dim_vendor` (DBT)
7. `fct_trips` (DBT)

**Dependencias:**
- Todos los dims dependen de `creating_partitions`
- `fct_trips` depende de todos los dims + `int_trips_enriched`

---

### 6. `quality_checks`
**Propósito:** Validación de calidad de datos  
**Bloque:** `run_tests_dbt` (Generic dbt command: `test`)  
**Tests:** 32 tests (unique, not_null, relationships, accepted_values)

---

## Trigger configurado

### Schedule Trigger: `ingest_monthly`
**Pipeline:** `ingest_bronze_yellow`  
**Tipo:** Schedule  
**Frecuencia:** Semanal (domingos 2:00 AM)  
**Estado:** Inactive (configurado para demostración)

### Pipeline Chaining (Manual)
**Flujo documentado:**
```
ingest_bronze_yellow ──┐
                       ├──→ dbt_build_silver → dbt_build_gold → quality_checks
ingest_bronze_green ───┘
```

**Política:** Event triggers automáticos requieren Mage Enterprise. En desarrollo se ejecutan manualmente en secuencia.

---

## Esquemas de datos

### Bronze (Schema: `bronze`)
**Tablas:**
- `bronze.taxi_trips`
- `bronze.taxi_zones`

**Columnas principales (taxi_trips):**
- Todos los campos originales del Parquet
- `service_type` (TEXT) → 'yellow' o 'green'
- `source_month` (TEXT) → '2024-01', '2024-02', etc.
- `ingest_ts` (TIMESTAMPTZ) → Momento de inserción

**Características:**
- Datos crudos sin transformaciones
- Idempotencia no garantizada (puede haber duplicados si se reejecuta)

---

### Silver (Schema: `analytics_silver`)
**Views:**
- `stg_taxi_zones`: Zonas con limpieza básica
- `stg_taxi_trips`: Viajes filtrados (solo 2024) y renombrados
- `int_trips_enriched`: Viajes enriquecidos con cálculos derivados

**Características:**
- Materialización: Views (datos siempre frescos)
- Filtros aplicados: solo año 2024
- Campos calculados: `trip_duration_min`

---

### Gold (Schema: `analytics_gold`)
**Tablas:**

**Dimensiones:**
- `dim_date` (366 filas) → Date spine 2024
- `dim_zone` (265 filas, HASH partitioned) → Zonas NYC
- `dim_service_type` (2 filas, LIST partitioned) → Yellow/Green
- `dim_payment_type` (6 filas, LIST partitioned) → Métodos de pago
- `dim_vendor` (4 filas) → Proveedores de tecnología

**Fact:**
- `fct_trips` (~37M filas, RANGE partitioned por mes)

**Columnas principales (fct_trips):**
- `trip_key` (BIGINT, PK) → Surrogate key con row_number()
- `pickup_date` (DATE) → Fecha de pickup
- `pu_zone_key`, `do_zone_key` (INT) → FKs a dim_zone
- `service_type_key` (VARCHAR) → FK a dim_service_type
- `payment_type_key` (INT) → FK a dim_payment_type
- `vendor_key` (INT) → FK a dim_vendor
- `pickup_date_key` (INT) → FK a dim_date
- Métricas: `trip_distance`, `fare_amount`, `tip_amount`, `total_amount`, etc.

**Características:**
- Materialización: Tablas (para soportar particionamiento)
- PKs en todas las dimensiones
- FKs validados con dbt tests (relationships)
- Particionamiento declarativo (RANGE, HASH, LIST)

---

## Particionamiento

### Estrategias implementadas

**1. RANGE Partitioning - `fct_trips` (pickup_date)**
- 12 particiones mensuales: `fct_trips_2024_01` a `fct_trips_2024_12`
- Ejemplo: `FOR VALUES FROM ('2024-01-01') TO ('2024-02-01')`

**2. HASH Partitioning - `dim_zone` (zone_key)**
- 4 particiones: `dim_zone_p0` a `dim_zone_p3`
- Distribución: `MODULUS 4, REMAINDER 0-3`

**3. LIST Partitioning - `dim_service_type` (service_type_key)**
- 2 particiones: `dim_service_type_yellow`, `dim_service_type_green`

**4. LIST Partitioning - `dim_payment_type` (payment_type_key)**
- 3 particiones: `card` (1), `cash` (2), `other` (3,4,5,6)

### Evidencia de particionamiento

**Comando `\d+`:**
```sql
\d+ analytics_gold.fct_trips

Partitioned table "analytics_gold.fct_trips"
Partition key: RANGE (pickup_date)
Partitions: fct_trips_2024_01 FOR VALUES FROM ('2024-01-01') TO ('2024-02-01'),
            fct_trips_2024_02 FOR VALUES FROM ('2024-02-01') TO ('2024-03-01'),
            ...
```

**EXPLAIN (Partition Pruning):**

Query 1 - RANGE:
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT COUNT(*), AVG(fare_amount), SUM(total_amount)
FROM analytics_gold.fct_trips
WHERE pickup_date >= '2024-02-01' AND pickup_date < '2024-03-01';

-- Resultado: Seq Scan on analytics_gold.fct_trips_2024_02
-- Interpretación: Solo 1 de 12 particiones escaneada
```

Query 2 - HASH:
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT borough, zone, service_zone
FROM analytics_gold.dim_zone
WHERE zone_key = 112;

-- Resultado: Index Scan ... on analytics_gold.dim_zone_p0
-- Interpretación: Solo 1 de 4 particiones accedida
```

---

## dbt - Transformaciones

### Materializations

| Layer | Schema | Materialization | Razón |
|-------|--------|-----------------|-------|
| Silver | analytics_silver | view | Transformaciones ligeras, datos siempre frescos |
| Gold | analytics_gold | table | Particionamiento + mejor performance analítico |

### Logs de ejecución

**dbt run (Gold):**
```
Running with dbt=1.8.7
Found 6 models, 32 tests

1 of 6 OK created table model analytics_gold.dim_date ........ [INSERT 366 in 0.45s]
2 of 6 OK created table model analytics_gold.dim_zone ........ [INSERT 265 in 0.52s]
3 of 6 OK created table model analytics_gold.dim_service_type [INSERT 2 in 0.38s]
4 of 6 OK created table model analytics_gold.dim_payment_type [INSERT 6 in 0.41s]
5 of 6 OK created table model analytics_gold.dim_vendor ...... [INSERT 4 in 0.39s]
6 of 6 OK created table model analytics_gold.fct_trips ....... [INSERT 37M in 1245s]

Done. PASS=6 WARN=0 ERROR=0 SKIP=0 TOTAL=6
```

**dbt test:**
```
Running with dbt=1.8.7
Found 9 models, 32 data tests

1 of 32 PASS test unique_dim_date_date_key .............. [PASS in 0.23s]
...
32 of 32 PASS test unique_stg_taxi_zones_zone_id ........ [PASS in 0.19s]

Done. PASS=32 WARN=0 ERROR=0 SKIP=0 TOTAL=32
```

---

## Validaciones / Volumetría

**Verificaciones realizadas:**
- ✅ Bronze: ~37M filas cargadas para 2024
- ✅ Silver: Views funcionando correctamente
- ✅ Gold: 37M filas en fct_trips, dims con row counts esperados
- ✅ Tests: 32/32 pasando
- ✅ Particiones: 12 particiones creadas y pobladas uniformemente

**Idempotencia:**
- Bronze: NO garantizada (puede duplicar en reejecuciones)
- Gold: SÍ garantizada (dbt trunca y reinserta en cada ejecución)

---

## Troubleshooting

### Problema 1: "Port 5432 already in use"
**Síntoma:** Error al levantar Docker  
**Causa:** PostgreSQL local corriendo  
**Solución:**
```bash
sudo systemctl stop postgresql
# O cambiar puerto en docker-compose.yml: "5433:5432"
```

---

### Problema 2: "Disk full" durante ingesta
**Síntoma:** `No space left on device`  
**Causa:** Volumen Docker lleno  
**Solución:**
1. Reducir dataset (solo 2024)
2. `docker system prune -a --volumes`
3. Aumentar límite Docker: Settings → Resources → Disk: 120GB

---

### Problema 3: dbt test falla - "relation does not exist"
**Síntoma:** Tests fallan antes de materializar  
**Causa:** Orden incorrecto de ejecución  
**Solución:**
```bash
dbt run --select gold    # Primero materializar
dbt test                 # Luego testear
```

---

### Problema 4: pgAdmin no conecta
**Síntoma:** `Connection refused`  
**Causa:** Hostname incorrecto  
**Solución:** Usar `warehouse` (no `localhost`) como hostname

---

### Problema 5: Mage secrets retornan None
**Síntoma:** `KeyError: None`  
**Causa:** Variables de entorno mal configuradas  
**Solución:**
```python
from mage_ai.data_preparation.shared.secrets import get_secret_value
host = get_secret_value("POSTGRES_HOST")  # ✅
```

---

### Problema 6: PostgreSQL crashea durante tests
**Síntoma:** `database system is in recovery mode`  
**Causa:** Recursos insuficientes  
**Solución:**
- Aumentar RAM Docker: Settings → Resources → Memory: 8GB
- Cerrar aplicaciones pesadas
- Ejecutar tests en lotes

---

## Runbook

**Ejecución completa del pipeline:**

1. Levantar stack: `docker compose up -d`
2. Ejecutar ingesta bronze:
   - Pipeline `ingest_bronze_yellow` → Run
   - Pipeline `ingest_bronze_green` → Run
   - Pipeline `taxi_zones` → Run
3. Ejecutar transformación silver:
   - Pipeline `dbt_build_silver` → Run
4. Ejecutar transformación gold:
   - Pipeline `dbt_build_gold` → Run (esperar ~25-30 min)
5. Ejecutar validaciones:
   - Pipeline `quality_checks` → Run (esperar ~5-10 min)

**Si falla:**
- Revisar logs en Mage
- Verificar espacio en disco
- Reintentar ejecución (gold es idempotente)
- Si falla por auth/secrets, revisar Mage Secrets

---

## Checklist de aceptación

☑ Mage y Postgres se comunican por nombre de servicio  
☑ Todos los secretos están en Mage Secrets; no hay secretos en el repo  
☑ Pipelines de bronze ingresan datos 2024 exitosamente  
☑ Trigger schedule configurado (inactive para demo)  
☑ Pipeline chaining documentado y probado manualmente  
☑ Esquemas bronze/silver/gold con datos poblados  
☑ Particionamiento declarativo implementado (RANGE, HASH, LIST)  
☑ Partition pruning verificado con EXPLAIN ANALYZE  
☑ dbt materializations configuradas correctamente (views en silver, tables en gold)  
☑ 32 tests dbt pasando (unique, not_null, relationships, accepted_values)  
☑ Idempotencia verificada en gold  
☑ Volumetría validada: ~37M filas en fct_trips  
☑ Troubleshooting documentado con 6+ problemas y soluciones  
☑ Runbook de ejecución disponible

---

## Evidencias

Se encuentran en la carpeta `evidencias/` con:
- Configuración de Mage Secrets (nombres visibles, valores ocultos)
- Trigger schedule configurado (captura)
- Pipeline tree de `dbt_build_gold` mostrando dependencias
- Tablas gold con registros en pgAdmin
- Logs de `dbt run` y `dbt test` (32/32 PASS)
- EXPLAIN ANALYZE mostrando partition pruning
- Notebook `data_analysis.ipynb` con 20 preguntas de negocio respondidas

---

**Fin del README**
