# tender-ingestion-service

> 📥 Ingesta de licitaciones públicas (PLACSP, TED) de **Keedio Tender Radar**: leer →
> normalizar → filtrar (CPV/keywords) → deduplicar → publicar en `tender-api`.

## Pipeline

```
conectores            normalizadores        filtros                 publicación
PLACSP (ATOM)   ─►    placsp_normalizer ─►  cpv + keyword + dedupe ─►  POST /api/tenders
TED (JSON)      ─►    ted_normalizer
```

- **Conectores** (`connectors/`): descargan y parsean la fuente a entradas crudas. `parse()` se
  testea con fixtures sin red; `fetch_raw()` hace la descarga real (mockeable).
- **Normalizadores** (`normalizers/`): entrada cruda → `TenderPayload` (importes, fechas y CPV
  saneados). `common_normalizer` tiene las utilidades (formato europeo de importes, fechas ISO).
- **Filtros** (`filters/`): `cpv_filter` (prefijos preferidos/excluidos), `keyword_filter`
  (positivas/negativas del perfil Keedio), `duplicate_filter` (dentro del lote).
- **Publicación** (`publishers/`): `api_client` (POST idempotente a tender-api), `event_publisher`
  (emite `DomainEvent` de tender-contracts; MVP: log).
- **Job** (`jobs/daily_ingestion_job.py`): orquesta todo y devuelve estadísticas; un conector
  caído no tumba el resto.

## Ejecutar

```bash
python -m venv .venv && . .venv/Scripts/activate    # Linux/mac: source .venv/bin/activate
pip install -e ../tender-shared-contracts
pip install pydantic pydantic-settings httpx pytest ruff

# Ejecutar la ingesta (usa .env / variables de entorno)
python -m tender_ingestion.main

pytest -q          # 18 tests (conectores + normalizadores + filtros + job), sin red
ruff check src tests
```

## Notas

- **PLACSP** publica ATOM con CODICE embebido; el parser extrae los campos ATOM y, *best-effort*,
  CPV/importe/plazo/órgano (por nombre local de etiqueta, ignorando namespaces). Lo no hallado
  queda en `None` — se completará al leer el pliego (fase 2, `tender-document-service`).
- **Idempotencia**: la deduplicación entre ejecuciones la garantiza `tender-api` (upsert por
  `source`+`source_id`); el `duplicate_filter` evita reprocesar dentro del mismo lote.
- Listas de CPV/keywords configurables por entorno (ver `.env.example`).

## Acceso a fuentes reales (importante)

Verificado el 2026-06-24:

- **PLACSP**: los feeds de sindicación `/sindicacion/sindicacion_643/*.atom` devuelven una página
  de error *"Su certificado no está autorizado a acceder a la Plataforma"* (redirección al
  portal). Es decir, requieren **certificado / acceso autorizado** (o la URL de open-data
  correcta). El conector ahora detecta respuestas no-ATOM y lanza `PlacspAccessError` con un
  diagnóstico claro en vez de un `ParseError` críptico. Configura la fuente con `PLACSP_FEED_URL`.
- **TED v3** (`/notices/search`): responde **405** a GET; la API espera **POST** con un cuerpo de
  consulta (y probablemente API key). El `TedConnector` parsea JSON; falta adaptar la llamada al
  contrato real de TED v3.

Mientras tanto, el radar se puede poblar sembrando licitaciones vía `POST /api/tenders` (ver
demo) y puntuándolas con `tender-ai-analysis-service`.
