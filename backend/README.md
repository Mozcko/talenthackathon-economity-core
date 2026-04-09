# Economity — Backend

API REST y sistema de agentes IA construido con **FastAPI**, **SQLAlchemy**, **LangChain** y **OpenAI**. Gestiona usuarios, transacciones financieras, portafolios de inversión, metas y asesoría conversacional en tiempo real.

---

## Índice

1. [Despliegue Local con Docker](#despliegue-local-con-docker)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Arquitectura de Capas](#arquitectura-de-capas)
4. [API — Endpoints](#api--endpoints)
5. [Sistema de Agentes IA](#sistema-de-agentes-ia)
6. [Extracción Multimodal](#extracción-multimodal)
7. [Modelo de Datos](#modelo-de-datos)
8. [Autenticación y Seguridad](#autenticación-y-seguridad)
9. [Gamificación](#gamificación)
10. [Variables de Entorno](#variables-de-entorno)
11. [Testing](#testing)

---

## Despliegue Local con Docker

### Prerrequisitos

- [Docker](https://docs.docker.com/get-docker/) ≥ 24 **o** [Podman](https://podman.io/) ≥ 4.x con `podman-compose`
- Clave de API de OpenAI (`OPENAI_API_KEY`)
- Proyecto de Clerk configurado (para autenticación)

### 1. Clonar el repositorio

```bash
git clone https://github.com/Mozcko/talenthackathon-economity-core.git
cd talenthackathon-economity-core/backend
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con los valores reales:

```env
# Base de datos — NO modificar si usas Docker Compose
DATABASE_URL=postgresql://economity_admin:economity_password@db:5432/economity_dev

# ChromaDB — NO modificar si usas Docker Compose
CHROMA_URL=http://chromadb:8000

# Autenticación Clerk (Opción A — recomendada)
# Obtener en: Clerk Dashboard > API Keys > JWKS URL
CLERK_JWKS_URL=https://tu-dominio.clerk.accounts.dev/.well-known/jwks.json

# Autenticación simétrica (Opción B — solo para desarrollo/testing)
# JWT_SECRET_KEY=una-clave-secreta-para-tests

# OpenAI (obligatorio)
OPENAI_API_KEY=sk-...
```

> **Nota:** El campo `DATABASE_URL` usa el nombre de servicio `db` (hostname interno de Docker), no `localhost`.

### 3. Construir y levantar los servicios

```bash
# Con Docker
docker compose up --build

# Con Podman
podman-compose up --build
```

Esto levanta **3 contenedores**:

| Servicio | Imagen | Puerto local | Descripción |
|----------|--------|-------------|-------------|
| `db` | `postgres:15-alpine` | `5432` | Base de datos relacional |
| `chromadb` | `chromadb/chroma:latest` | `8001` | Base de datos vectorial (RAG) |
| `api` | Dockerfile local | `8000` | FastAPI + Agentes IA |

El servicio `api` espera a que `db` pase su health check antes de iniciar. Al arrancar ejecuta automáticamente:
- `Base.metadata.create_all()` — crea todas las tablas si no existen (con reintentos)
- `initialize_system_data()` — inicializa categorías, subcategorías y logros (idempotente)

### 4. Verificar el despliegue

```bash
# Health check de la API
curl http://localhost:8000/

# Documentación interactiva (Swagger UI)
# Abrir en el navegador:
http://localhost:8000/docs

# Documentación alternativa (ReDoc)
http://localhost:8000/redoc
```

### 5. Flujo de arranque

```mermaid
sequenceDiagram
    participant DC as Docker Compose
    participant DB as PostgreSQL
    participant Chroma as ChromaDB
    participant API as FastAPI (lifespan)

    DC->>DB: Inicia contenedor
    DC->>Chroma: Inicia contenedor
    DB-->>DC: healthcheck OK
    DC->>API: Inicia contenedor
    loop Hasta 10 intentos (3s entre c/u)
        API->>DB: create_all() tables
        DB-->>API: OK
    end
    API->>API: initialize_system_data()
    Note over API: Crea categorías, subcategorías\ny logros si no existen
    API-->>DC: Servidor listo en :8000
```

### 6. Comandos útiles

```bash
# Ver logs en tiempo real
docker compose logs -f api

# Reiniciar solo la API (sin reconstruir)
docker compose restart api

# Acceder a la base de datos directamente
docker compose exec db psql -U economity_admin -d economity_dev

# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes (¡borra todos los datos!)
docker compose down -v

# Reconstruir solo la imagen de la API
docker compose build api
```

### 7. Despliegue sin Docker (modo desarrollo)

```bash
# Requiere: PostgreSQL y ChromaDB corriendo localmente

cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Ajustar DATABASE_URL y CHROMA_URL en .env para apuntar a localhost

uvicorn src.main:app --reload --port 8000
```

---

## Estructura del Proyecto

```
backend/
├── src/
│   ├── main.py                  # Punto de entrada, lifespan, CORS, routers
│   ├── core/
│   │   ├── config.py            # Settings (Pydantic BaseSettings)
│   │   ├── database.py          # Engine, SessionLocal, get_db()
│   │   └── security.py          # Validación JWT Clerk (RS256 / HS256)
│   ├── models/                  # ORM SQLAlchemy
│   │   ├── user.py              # Usuario, CuentaFinanciera
│   │   ├── tenant.py            # Tenant (aislamiento multi-tenant)
│   │   ├── transaction.py       # Transaccion, Categoria, SubCategoria
│   │   ├── goal.py              # MetaFinanciera
│   │   ├── investment.py        # InstrumentoCatalogo, PortafolioInversion
│   │   └── gamification.py      # PerfilGamificacion, LogroUsuario
│   ├── schemas/                 # Pydantic v2 request/response
│   ├── api/
│   │   └── routers/             # Un archivo por dominio
│   │       ├── user.py
│   │       ├── transaction.py
│   │       ├── upload.py        # Extracción IA (sin guardar)
│   │       ├── investment.py
│   │       ├── goal.py
│   │       ├── gamification.py
│   │       ├── dashboard.py
│   │       ├── category.py
│   │       ├── tenant.py
│   │       └── chat.py          # WebSocket /ws/asesor
│   └── services/
│       ├── transaction.py       # CRUD + hook gamificación + actualiza saldo
│       ├── dashboard.py         # Resumen financiero calculado desde transacciones
│       ├── category.py          # resolve_sub_categoria_id()
│       ├── gamification.py      # XP, streaks, logros
│       ├── system_init.py       # Bootstrap de datos de referencia (producción)
│       └── ai/
│           ├── router.py        # Clasificador semántico de intenciones
│           ├── memory.py        # Formateo del historial de conversación
│           ├── multimodal_parser.py  # Parser síncrono (ruta /transacciones)
│           └── agents/
│               ├── extraction_agent.py  # Extracción multimodal asíncrona
│               ├── data_agent.py        # Análisis de gastos con tool-calling
│               ├── math_agent.py        # Proyecciones de inversión
│               ├── fiscal_agent.py      # RAG sobre leyes fiscales
│               └── support_agent.py    # Coach motivacional
├── test/                        # Pruebas unitarias (pytest)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── pytest.ini
```

---

## Arquitectura de Capas

```mermaid
graph TB
    subgraph HTTP["Capa HTTP / WebSocket"]
        Routers["Routers FastAPI\n(11 módulos)"]
        WS["WebSocket /ws/asesor"]
    end

    subgraph Auth["Autenticación"]
        JWTMiddleware["get_current_user_token()\nValidación Clerk JWKS (RS256)"]
        TenantResolve["_get_tenant_id(db, user_id)\nZero-Trust: clerk_id → tenant UUID"]
    end

    subgraph Business["Servicios de Negocio"]
        TxService["transaction.py\ncreate + balance update + gamification hook"]
        DashService["dashboard.py\nSUM(monto) desde transacciones"]
        CatService["category.py\nresolve_sub_categoria_id()"]
        GamService["gamification.py\nXP, streaks, logros"]
        SysInit["system_init.py\nBootstrap idempotente"]
    end

    subgraph AI["Sistema IA"]
        Router["router.py\nClasificador de intención"]
        Agents["5 Agentes Especializados"]
        ExtrAgent["extraction_agent.py\nWhisper + GPT-4o-mini + Vision"]
    end

    subgraph Data["Capa de Datos"]
        ORM["SQLAlchemy ORM"]
        PG[("PostgreSQL")]
        Chroma[("ChromaDB")]
    end

    HTTP --> Auth
    Auth --> Business
    Auth --> AI
    Business --> ORM
    AI --> ORM
    AI --> Chroma
    ORM --> PG
```

---

## API — Endpoints

### Usuarios y Cuentas `/usuarios`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/usuarios/` | Crear usuario |
| `GET` | `/usuarios/{user_id}` | Obtener perfil |
| `POST` | `/usuarios/{user_id}/cuentas/` | Crear cuenta financiera |
| `GET` | `/usuarios/{user_id}/cuentas/` | Listar cuentas |

### Transacciones `/transacciones`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/transacciones/` | Registrar transacción manual |
| `GET` | `/transacciones/cuenta/{cuenta_id}` | Historial de cuenta |
| `POST` | `/transacciones/cuenta/{id}/audio` | Registrar por voz (Whisper + GPT) |
| `POST` | `/transacciones/cuenta/{id}/imagen` | Registrar por ticket foto (GPT-4o Vision) |
| `DELETE` | `/transacciones/{id}` | Eliminar transacción |

### Extracción IA (preview sin guardar) `/upload`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/upload/texto` | Extraer datos de texto libre |
| `POST` | `/upload/audio` | Transcribir audio y extraer |
| `POST` | `/upload/imagen` | Analizar imagen de ticket |

### Inversiones `/inversiones`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/inversiones/tierlist` | Tier list personalizada de instrumentos |
| `POST` | `/inversiones/portafolio` | Registrar inversión |
| `GET` | `/inversiones/portafolio` | Ver portafolio |

### Metas Financieras `/metas`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/metas/` | Crear meta |
| `GET` | `/metas/` | Listar metas del usuario |
| `PATCH` | `/metas/{id}/progreso` | Sumar avance (`?monto_a_sumar=500`) |
| `DELETE` | `/metas/{id}` | Eliminar meta |

### Otros

| Prefijo | Descripción |
|---------|-------------|
| `/dashboard/summary` | Resumen: saldo, flujo, score, meta próxima |
| `/gamification/profile` | XP, nivel, racha |
| `/gamification/achievements` | Logros desbloqueados |
| `/categorias/` | Catálogo completo de categorías y subcategorías |
| `/organizaciones/` | Gestión de tenant |
| `WS /ws/asesor` | Chat con el asesor IA |

---

## Sistema de Agentes IA

El asesor financiero es un sistema multi-agente que recibe preguntas por WebSocket, clasifica la intención y delega a un agente especializado.

### Flujo del WebSocket `/ws/asesor`

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant WS as chat.py
    participant Ctx as get_dashboard_summary()
    participant Router as clasificar_intencion_async()
    participant Agent as Agente Especializado
    participant DB as PostgreSQL / ChromaDB

    FE->>WS: {token: "Bearer ..."}
    WS->>WS: validar_token_ws() → user_id
    WS->>DB: Lookup Usuario → tenant_uuid
    WS-->>FE: {type:"status", content:"autenticado"}

    FE->>WS: {content: "¿Cuánto gasté este mes?", history: [...]}
    WS->>Ctx: get_dashboard_summary(db, tenant_uuid, user_id)
    Ctx->>DB: SELECT SUM(monto) FROM transacciones WHERE tenant_id=...
    Ctx-->>WS: {saldo_total, flujo, score, ...}
    WS->>Router: clasificar_intencion_async(mensaje)
    Router-->>WS: "ANALISIS_DATOS"
    WS->>Agent: analizar_datos_async(pregunta, contexto, tenant_uuid)
    Agent->>DB: obtener_resumen_transacciones(tenant_uuid)
    DB-->>Agent: historial de transacciones
    Agent-->>WS: análisis + insights
    WS-->>FE: {type:"message", content:"análisis..."}
    WS-->>FE: {type:"status", content:"idle"}
```

### Agentes Especializados

```mermaid
graph LR
    subgraph Clasificador
        C["Router Semántico\nGPT-4o-mini (temp=0)\nGuardrail anti-injection"]
    end

    C -->|CONSULTA_FISCAL| FA
    C -->|PROYECCION_MATEMATICA| MA
    C -->|ANALISIS_DATOS| DA
    C -->|SOPORTE_GENERAL| SA
    C -->|BLOQUEADO| BL["Respuesta de bloqueo"]

    subgraph FA["Agente Fiscal"]
        FA1["ChromaDB — leyes_fiscales\n(top-3 chunks por similitud)"]
        FA2["GPT-4o-mini\nResponde SOLO con contexto recuperado"]
        FA1 --> FA2
    end

    subgraph MA["Agente Matemático"]
        MA1["Tool: calcular_interes_compuesto()\ncapital, aportación, tasa, años"]
        MA2["GPT-4o-mini formatea resultado"]
        MA1 --> MA2
    end

    subgraph DA["Agente de Datos"]
        DA1["Tool: obtener_resumen_transacciones(tenant_id)\nConsulta PostgreSQL en tiempo real"]
        DA2["GPT-4o-mini analiza patrones"]
        DA1 --> DA2
    end

    subgraph SA["Agente de Soporte"]
        SA1["GPT-4o-mini (temp=0.7)\nPersonalidad: coach sarcástico-motivacional"]
    end
```

| Agente | Modelo | Técnica | Fuente de datos |
|--------|--------|---------|----------------|
| Fiscal | GPT-4o-mini | RAG | ChromaDB (leyes_fiscales) |
| Matemático | GPT-4o-mini | Tool calling | Cálculo local (interés compuesto) |
| Datos | GPT-4o-mini | Tool calling | PostgreSQL (transacciones reales) |
| Soporte | GPT-4o-mini | Prompt engineering | Historial de conversación |

---

## Extracción Multimodal

El módulo `extraction_agent.py` procesa tres tipos de entrada para extraer transacciones estructuradas.

```mermaid
flowchart TD
    Input([Entrada del usuario]) --> TypeCheck{Tipo de entrada}

    TypeCheck -->|Texto| TextFlow
    TypeCheck -->|Audio| AudioFlow
    TypeCheck -->|Imagen| ImageFlow

    subgraph TextFlow["Flujo Texto"]
        T1["GPT-4o-mini\nwith_structured_output(DatosExtraidos)"]
        T2["Regex keyword override\ngasté/pagué → es_ingreso=False\ngané/cobré → es_ingreso=True"]
        T1 --> T2
    end

    subgraph AudioFlow["Flujo Audio"]
        A1["OpenAI Whisper\naudio → texto transcrito"]
        A2["→ Flujo Texto"]
        A1 --> A2
    end

    subgraph ImageFlow["Flujo Imagen"]
        I1["GPT-4o Vision\nbase64 image → extracción"]
        I2["Forzar es_ingreso=False\n(ticket = siempre gasto)"]
        I1 --> I2
    end

    T2 --> Resolve
    A2 --> Resolve
    I2 --> Resolve

    subgraph Resolve["Resolución de Categoría"]
        R1["resolve_sub_categoria_id(db, categoria_sugerida, es_ingreso)"]
        R2["JOIN SubCategoria → Categoria\nFiltro por tipo_flujo (Ingreso/Egreso)"]
        R1 --> R2
    end

    Resolve --> Output([DatosExtraidos + sub_categoria_id])
```

### Esquema `DatosExtraidos`

```python
class DatosExtraidos(BaseModel):
    monto: float              # Siempre positivo (el signo se aplica al guardar)
    descripcion: str          # Ej. "Gasolina Pemex", "Sueldo Enero"
    es_ingreso: bool          # True SOLO para salario/venta/cobro
    categoria_sugerida: str   # Ej. "Transporte/Gasolina", "Sueldo/Nómina"
    es_riesgoso: bool         # True para apuestas, alcohol, compras impulsivas
```

---

## Modelo de Datos

```mermaid
erDiagram
    Tenant {
        UUID id PK
        string nombre
        datetime created_at
    }
    Usuario {
        string id PK
        UUID tenant_id FK
        string nombre_completo
        string perfil_riesgo
        int score_resiliencia
        decimal flujo_caja_libre_mensual
    }
    CuentaFinanciera {
        UUID id PK
        string usuario_id FK
        UUID tenant_id FK
        string nombre
        string tipo
        decimal saldo_actual
    }
    Transaccion {
        UUID id PK
        UUID cuenta_id FK
        UUID tenant_id FK
        int sub_categoria_id FK
        decimal monto
        datetime fecha_operacion
        string descripcion
    }
    Categoria {
        int id PK
        string nombre
        string tipo_flujo
    }
    SubCategoria {
        int id PK
        int categoria_id FK
        string nombre
        bool is_risky
        string risk_level
    }
    MetaFinanciera {
        UUID id PK
        string usuario_id FK
        UUID tenant_id FK
        string nombre
        decimal monto_objetivo
        decimal progreso_actual
        date fecha_limite
    }
    InstrumentoCatalogo {
        int id PK
        string tipo
        string entidad
        decimal tasa_rendimiento_actual
        decimal monto_minimo_apertura
        int score_minimo_requerido
        bool beneficio_fiscal
    }
    PortafolioInversion {
        UUID id PK
        string usuario_id FK
        int instrumento_id FK
        UUID tenant_id FK
        decimal saldo_invertido
    }
    PerfilGamificacion {
        int id PK
        string usuario_id FK
        int xp_total
        string nivel_actual
        int racha_dias
    }

    Tenant ||--o{ Usuario : "tiene"
    Tenant ||--o{ CuentaFinanciera : "posee"
    Tenant ||--o{ Transaccion : "agrupa"
    Usuario ||--o{ CuentaFinanciera : "administra"
    Usuario ||--o{ MetaFinanciera : "define"
    Usuario ||--o{ PortafolioInversion : "mantiene"
    Usuario ||--|| PerfilGamificacion : "tiene"
    CuentaFinanciera ||--o{ Transaccion : "registra"
    Transaccion }o--o| SubCategoria : "clasifica"
    SubCategoria }o--|| Categoria : "pertenece"
    InstrumentoCatalogo ||--o{ PortafolioInversion : "referencia"
```

### Categorías predefinidas (`system_init.py`)

| Categoría | Tipo | Subcategorías (ejemplos) |
|-----------|------|--------------------------|
| Ingresos | Ingreso | Sueldo/Nómina, Freelance/Honorarios, Venta |
| Supervivencia Esenciales | Egreso | Renta/Vivienda, Despensa/Súper, Transporte/Gasolina |
| Crecimiento y Salud | Egreso | Gym/Deporte, Educación/Cursos, Médico |
| Dopamina y Riesgo | Egreso ⚠️ | Apuestas/Casino, Alcohol, Antros/Fiesta, Skins/Games |
| Otros | Egreso | Varios/Sin categoría |

---

## Autenticación y Seguridad

```mermaid
flowchart TD
    Request["HTTP Request\nAuthorization: Bearer {token}"] --> Extract["Extraer token"]
    Extract --> Mode{¿Qué auth\nestá configurada?}

    Mode -->|CLERK_JWKS_URL| RS256["Obtener llave pública\nvía JWKS URL\nVerificar RS256"]
    Mode -->|JWT_SECRET_KEY| HS256["Verificar HS256\ncon clave simétrica"]
    Mode -->|Ninguna| Error1["HTTP 500\nAuth no configurada"]

    RS256 --> Validate
    HS256 --> Validate

    subgraph Validate["Validación del Payload"]
        V1["¿Tiene campo 'sub'?"]
        V2["user_id = payload['sub']\n(Clerk ID: 'user_abc123')"]
        V1 --> V2
    end

    Validate --> TenantLookup["DB: SELECT tenant_id\nFROM usuarios WHERE id = user_id"]
    TenantLookup --> ZeroTrust["Zero-Trust:\ntenant_uuid validado"]
    ZeroTrust --> Route["Continúa al handler"]
```

**Principios de seguridad implementados:**
- **Zero-Trust:** El `tenant_id` siempre se resuelve desde la DB, nunca desde el cliente
- **Aislamiento por tenant:** Toda consulta filtra por `tenant_id` en la capa de servicio
- **Guardrail de prompt injection:** El clasificador semántico bloquea intentos de manipulación del agente
- **Monto firmado:** El signo del monto lo define el backend (nunca el cliente) basado en `es_ingreso`

---

## Gamificación

```mermaid
flowchart LR
    Tx["Transacción creada"] --> Hook["Hook en create_transaccion()"]

    Hook --> Streak["update_streak()\n+1 día de racha"]
    Hook --> XP["award_xp(amount=10)\nevent: expense_created"]
    Hook --> RiskyCheck{¿SubCategoria\nes_risky?}
    RiskyCheck -->|Sí| HonestyXP["award_honesty_xp()\nBono por registrar gasto riesgoso"]

    subgraph Levels["Sistema de Niveles"]
        L1["Bronce — 0 XP"]
        L2["Plata — 500 XP"]
        L3["Oro — 1500 XP"]
        L4["Platino — 3500 XP"]
        L5["Mítico — 7000 XP"]
    end

    XP --> Levels
    HonestyXP --> Levels
```

Rutas adicionales de XP:
- `audio_log_bonus` (+5 XP) — por registrar transacción por voz
- `image_log_bonus` (+10 XP) — por registrar transacción por foto de ticket

---

## Variables de Entorno

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `DATABASE_URL` | ✅ | Cadena de conexión PostgreSQL |
| `OPENAI_API_KEY` | ✅ | Clave de API de OpenAI |
| `CLERK_JWKS_URL` | ⚠️ uno de los dos | URL JWKS para validación RS256 (Clerk) |
| `JWT_SECRET_KEY` | ⚠️ uno de los dos | Clave simétrica HS256 (solo dev/testing) |
| `CHROMA_URL` | — | URL de ChromaDB (default: `http://localhost:8001`) |
| `DEEPSEEK_API_KEY` | — | Opcional, no usado activamente |
| `CLAUDECODE_API_KEY` | — | Opcional, no usado activamente |

---

## Testing

```bash
# Activar el entorno virtual
source venv/bin/activate

# Ejecutar todas las pruebas
venv/bin/pytest -v

# Ejecutar un módulo específico
venv/bin/pytest test/test_transaction_service.py -v

# Con reporte de cobertura (requiere pytest-cov)
venv/bin/pytest --cov=src --cov-report=term-missing
```

Las pruebas unitarias usan `MagicMock` y `AsyncMock` para aislar la base de datos y los servicios externos (OpenAI, Clerk). No requieren servicios externos levantados.

```
test/
├── test_transaction_service.py    # CRUD de transacciones + gamification hook
├── test_dashboard_service.py      # Resumen financiero calculado desde transacciones
├── test_upload.py                 # Endpoints de extracción IA (/upload/*)
├── test_gamification_service.py   # XP, niveles, logros
├── test_category_service.py       # Resolución de subcategorías
├── test_user_service.py           # Usuarios y cuentas
├── test_goal_service.py           # Metas financieras
├── test_tenant_service.py         # Multi-tenant
├── test_investment_service.py     # Portafolio e instrumentos
└── test_ws_client.py              # Cliente WebSocket del asesor
```
