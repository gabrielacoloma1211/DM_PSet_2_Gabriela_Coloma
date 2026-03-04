# Data_Mining_Pset2_Gabriela_Coloma

**Problem Set 2 - Data Mining**

**Nombre:** Gabriela Coloma  
**Código:** 00325312

---

## Resumen

El proyecto implementa un pipeline de datos para NYC TLC (Taxi & Limousine Commission) siguiendo una arquitectura medallion (Bronze → Silver → Gold). Los datos se extraen desde archivos Parquet públicos, se transforman con dbt, y se almacenan en PostgreSQL con particionamiento declarativo. La orquestación se realiza en Mage AI, desplegado con Docker Compose, y las credenciales se gestionan con Mage Secrets.

---

## Diagrama de arquitectura

**Bronze Layer (Schema: `bronze`):**  
Capa de datos crudos sin transformaciones. Almacena los datos tal como llegan de las fuentes externas (archivos Parquet y CSV de NYC TLC). Incluye las tablas `taxi_trips` (viajes yellow y green) y `taxi_zones` (lookup de zonas). La ingesta se realiza mediante pipelines Python en Mage que descargan, validan e insertan los datos en PostgreSQL. Los datos conservan todos los campos originales más metadatos de ingesta (`service_type`, `source_month`, `ingest_ts`).

**Silver Layer (Schema: `analytics_silver`):**  
Capa de datos limpios y estandarizados. Transforma los datos crudos de bronze aplicando filtros, renombrado de columnas, y cálculos derivados. Se materializa como views dbt para mantener los datos siempre actualizados sin duplicación. Incluye `stg_taxi_zones` (zonas con limpieza básica), `stg_taxi_trips` (viajes filtrados solo para 2024), e `int_trips_enriched` (viajes enriquecidos con métricas calculadas como duración de viaje).

**Gold Layer (Schema: `analytics_gold`):**  
Capa analítica con modelo dimensional (Star Schema). Organiza los datos en dimensiones y tablas de hechos optimizadas para consultas de negocio. Las dimensiones incluyen `dim_date` (366 días de 2024), `dim_zone` (265 zonas NYC), `dim_service_type` (Yellow/Green), `dim_payment_type` (6 métodos de pago), y `dim_vendor` (4 proveedores). La tabla de hechos `fct_trips` contiene ~37M viajes con métricas de negocio. Todas las tablas se materializan físicamente en PostgreSQL con particionamiento declarativo (RANGE, HASH, LIST) para optimizar el performance de queries analíticos.

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
- `warehouse_ui`: pgAdmin (8081)
- `scheduler`: Mage (6789)

**Acceso a interfaces:**
- Mage: http://localhost:6789
- pgAdmin: http://localhost:8081

**Configurar pgAdmin (primera vez):**
1. Register Server → Name: `warehouse`
2. Connection: Consultar credenciales en `docker-compose.yml`

---


## 4. Pipelines

Existen 6 pipelines principales organizados por capa de la arquitectura medallion:

### Pipelines Bronze

#### `ingest_bronze_yellow`
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

---

#### `ingest_bronze_green`
**Propósito:** Ingesta de datos Green Taxi  
**Estructura:** Idéntica a yellow, cambia solo el `service_type` a 'green'

---

#### `taxi_zones`
**Propósito:** Carga del lookup de zonas NYC TLC (CSV estático)  
**Destino:** `bronze.taxi_zones`

---

**Esquema Bronze resultante:**

**Tablas:**
- `bronze.taxi_trips` 
- `bronze.taxi_zones` 

**Columnas principales (taxi_trips):**
- Todos los campos originales del Parquet (vendorid, pickup/dropoff datetime, passenger_count, trip_distance, fare_amount, etc.)
- `service_type` (TEXT) → 'yellow' o 'green'
- `source_month` (TEXT) → '2024-01', '2024-02', etc.
- `ingest_ts` (TIMESTAMPTZ) → Momento de inserción UTC

**Características:**
- Datos crudos sin transformaciones
- Almacenamiento completo del payload original
- Idempotencia no garantizada (puede haber duplicados si se reejecuta)

---

### Pipelines Silver

#### `dbt_build_silver`
**Propósito:** Transformación Bronze → Silver (views)  
**Bloques:**
- `stg_taxi_zones` (DBT)
- `stg_taxi_trips` (DBT)
- `int_trips_enriched` (DBT)

**Tecnología:** dbt  
**Materialización:** Views  
**Dependencias:** Auto-detectadas por dbt con `{{ ref() }}`

---

**Esquema Silver resultante:**

**Views:**
- `stg_taxi_zones`: Zonas con limpieza básica (normalización de nombres)
- `stg_taxi_trips`: Viajes filtrados (solo 2024) con campos renombrados a convención estándar
- `int_trips_enriched`: Viajes enriquecidos con joins a zonas y cálculos derivados

**Características:**
- Materialización: Views (datos siempre frescos, sin duplicación)
- Filtros aplicados: solo año 2024, elimina registros con datos anómalos
- Campos calculados: `trip_duration_min` (diferencia entre dropoff y pickup)
- Renombrado consistente: `pickup_location_id`, `dropoff_location_id`, etc.

---

### Pipelines Gold

#### `dbt_build_gold`
**Propósito:** Transformación Silver → Gold (tablas particionadas con modelo dimensional)  
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

**Esquema Gold resultante:**

**Dimensiones:**
- `dim_date` → Date spine completo 2024 con atributos temporales
- `dim_zone` (HASH partitioned) → Zonas NYC con borough, zona, service_zone
- `dim_service_type` (LIST partitioned) → Yellow Taxi / Green Taxi
- `dim_payment_type` (LIST partitioned) → Credit Card, Cash, No Charge, Dispute, Unknown, Voided
- `dim_vendor` → Unknown/NULL, Creative Mobile Technologies, VeriFone, Other

**Fact Table:**
- `fct_trips` (RANGE partitioned por mes en 12 particiones)

**Columnas principales (fct_trips):**
- `trip_key` (BIGINT, PK) → Surrogate key generado con row_number()
- `pickup_date` (DATE) → Fecha de pickup (columna de particionamiento)
- `pickup_datetime`, `dropoff_datetime` (TIMESTAMP) → Timestamps completos
- `pu_zone_key`, `do_zone_key` (INT) → Foreign Keys a dim_zone
- `service_type_key` (VARCHAR) → Foreign Key a dim_service_type
- `payment_type_key` (INT) → Foreign Key a dim_payment_type
- `vendor_key` (INT) → Foreign Key a dim_vendor
- `pickup_date_key` (INT) → Foreign Key a dim_date
- **Métricas:** `passenger_count`, `trip_distance`, `trip_duration_min`, `fare_amount`, `tip_amount`, `tolls_amount`, `total_amount`
- **Metadata:** `source_month`, `ingest_ts`

**Características:**
- Materialización: Tables
- Primary Keys en todas las dimensiones
- Foreign Keys validados con dbt tests (relationships)
- Particionamiento declarativo optimizado por tipo de consulta:
  - RANGE en fct_trips (filtros por fecha)
  - HASH en dim_zone (distribución uniforme)
  - LIST en dim_service_type y dim_payment_type (categorías discretas)

---

### Pipeline de Validación

#### `quality_checks`
**Propósito:** Validación de calidad de datos en todas las capas  
**Bloque:** `run_tests_dbt` (Generic dbt command: `test`)  
**Tests:** 32 tests automatizados

**Cobertura:**
- **unique:** PKs de dimensiones y fact table
- **not_null:** Campos críticos (PKs, fechas, FKs)
- **relationships:** Integridad referencial fact → dims
- **accepted_values:** Validación de categorías (service_type: yellow/green)

**Tiempo de ejecución:** ~5-10 minutos para 37M filas

---

## Triggers configurado

### Schedule Trigger: `ingest_monthly`
**Pipeline:** `yellow_taxi_trips`  
**Tipo:** Schedule  
**Frecuencia:** Semanal (domingos 2:00 AM)  
**Estado:** Inactive (configurado para demostración)

### Schedule Trigger: `ingest_bronze_green`
**Pipeline:** `green_taxi_trips`  
**Tipo:** Schedule  
**Frecuencia:** Semanal (domingos 2:00 AM)  
**Estado:** Inactive (configurado para demostración)

### API Trigger

Además del Schedule Trigger, se configuraron **API Triggers** para automatizar la ingesta mensual secuencial.

## `trigger_yellow_taxi.py` y `trigger_green_taxi.py`

**Tipo:** Custom Python Script (externo a Mage)  
**Propósito:** Disparar el pipeline de ingesta mes por mes para todo 2024  
**Tecnología:** Python + requests (Mage API)

**Funcionamiento:**

1. **Dispara el pipeline** con parámetros `service_type`, `year`, `month`
2. **Espera a que termine** cada ejecución (polling cada 30 segundos)
3. **Verifica el estado** (completed/failed/canceled)
4. **Avanza al siguiente mes** solo si el anterior fue exitoso
5. **Gestiona errores** con logs descriptivos

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

**EXPLAIN (Partition Pruning):**
<img width="943" height="658" alt="Screenshot 2026-03-04 at 2 06 10 AM" src="https://github.com/user-attachments/assets/672bba04-d432-42dd-bdd1-5dadd794df0e" />
<img width="1007" height="606" alt="Screenshot 2026-03-04 at 2 06 23 AM" src="https://github.com/user-attachments/assets/2ba0fb53-a0e2-4fc3-8982-228c091f6dc5" />


```

---

## dbt - Transformaciones

### Materializations

| Layer | Schema | Materialization | Razón |
|-------|--------|-----------------|-------|
| Silver | analytics_silver | view | Transformaciones ligeras, datos siempre frescos |
| Gold | analytics_gold | table | Particionamiento + mejor performance analítico |

### Logs de ejecución

**dbt run (Silver):**
<img width="1002" height="661" alt="Screenshot 2026-03-04 at 2 08 20 AM" src="https://github.com/user-attachments/assets/3929f7da-4ce6-4715-91b6-ede4d36d9106" />
<img width="977" height="658" alt="Screenshot 2026-03-04 at 2 08 31 AM" src="https://github.com/user-attachments/assets/1976a840-f109-4f2d-8347-e5a382314e28" />
<img width="1019" height="634" alt="Screenshot 2026-03-04 at 2 08 43 AM" src="https://github.com/user-attachments/assets/fb6d58d0-f365-49e6-9ff8-fbff3624e7bb" />


**dbt run (Gold):**
```
<img width="880" height="662" alt="Screenshot 2026-03-04 at 2 07 16 AM" src="https://github.com/user-attachments/assets/5396f472-0625-4c1a-b493-9309b632e58d" />

```

**dbt test:**
```
<img width="1015" height="655" alt="Screenshot 2026-03-04 at 2 07 42 AM" src="https://github.com/user-attachments/assets/357f5537-5219-43c1-8147-c5a50dc298b4" />

```

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
host = get_secret_value("POSTGRES_HOST")  
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


## Checklist de aceptación

☑ Docker Compose levanta Postgres + Mage
☑ Credenciales en Mage Secrets y .env (solo .env.example en repo)
☑ Pipeline ingest_bronze mensual e idempotente + tabla de cobertura
☑ dbt corre dentro de Mage: dbt_build_silver, dbt_build_gold, quality_checks
☑ Silver materialized = views; Gold materialized = tables
☑ Gold tiene esquema estrella completo
☑ Particionamiento: RANGE en fct_trips, HASH en dim_zone, LIST en dim_service_type y dim_payment_type
☑ README incluye \d+ y EXPLAIN (ANALYZE, BUFFERS) con pruning
☑ dbt test pasa desde Mage
☑ Notebook responde 20 preguntas usando solo gold.*
☑ Triggers configurados y evidenciados

---

## Evidencias

Se encuentran en la carpeta `evidencias/`
