# Economity — Arquitectura del Sistema

Economity es una aplicación de finanzas personales con registro de transacciones asistido por IA multimodal (voz, imagen, texto), asesoría financiera conversacional mediante agentes especializados, y mecánicas de gamificación para fomentar hábitos económicos saludables.

---

## Estructura del Repositorio

```
talenthackathon-economity-core/
├── backend/          # API REST + WebSockets + Agentes IA (FastAPI + Python)
└── frontend/         # Interfaz de usuario (Astro + React + Tailwind)
```

---

## Visión General de la Arquitectura

```mermaid
graph TB
    subgraph Cliente["Cliente (Browser)"]
        UI["Astro + React SPA"]
        Clerk["Clerk Auth SDK"]
    end

    subgraph Proxy["Proxy SSR (Astro Node)"]
        APIProxy["pages/api/[...path].ts"]
    end

    subgraph Backend["Backend (FastAPI)"]
        REST["Routers REST"]
        WS["WebSocket /ws/asesor"]
        Auth["JWT Middleware (Clerk RS256)"]
        Services["Servicios de Negocio"]
        AISystem["Sistema de Agentes IA"]
    end

    subgraph Datos["Capa de Datos"]
        PG[("PostgreSQL 15")]
        Chroma[("ChromaDB\n(Vectores RAG)")]
    end

    subgraph LLMs["APIs Externas"]
        GPT4o["OpenAI GPT-4o"]
        GPT4mini["OpenAI GPT-4o-mini"]
        Whisper["OpenAI Whisper"]
    end

    UI -->|"Bearer JWT"| APIProxy
    Clerk -->|"Emite token"| UI
    APIProxy -->|"HTTP forward"| REST
    APIProxy -->|"WS upgrade"| WS
    REST --> Auth
    WS --> Auth
    Auth --> Services
    Services --> PG
    Services --> AISystem
    AISystem --> Chroma
    AISystem --> GPT4o
    AISystem --> GPT4mini
    AISystem --> Whisper
```

---

## Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Frontend | Astro (SSR) | 6.1 |
| UI Components | React | 19.2 |
| Estilos | Tailwind CSS | 4.2 |
| Autenticación | Clerk | latest |
| Gráficos | Recharts | 2.15 |
| Backend | FastAPI + Uvicorn | ≥0.100 |
| ORM | SQLAlchemy | ≥2.0 |
| Base de Datos | PostgreSQL | 15 |
| Base Vectorial | ChromaDB | latest |
| IA / LLMs | OpenAI GPT-4o / mini | latest |
| Transcripción | OpenAI Whisper | whisper-1 |
| Orquestación IA | LangChain | ≥0.1 |
| Contenedores | Docker / Podman Compose | — |

---

## Flujo de Autenticación

```mermaid
sequenceDiagram
    actor Usuario
    participant Browser
    participant Clerk
    participant Proxy as Proxy SSR
    participant API as FastAPI
    participant DB as PostgreSQL

    Usuario->>Browser: Accede a la app
    Browser->>Clerk: Verifica sesión activa
    alt Sin sesión
        Clerk-->>Browser: Redirige a /login
        Usuario->>Clerk: Credenciales
        Clerk-->>Browser: JWT (RS256, sub = Clerk User ID)
    end
    Browser->>Proxy: Request + Bearer JWT
    Proxy->>API: Forward request
    API->>Clerk: Valida firma con JWKS URL
    API->>DB: Busca Usuario por sub (Clerk ID)
    DB-->>API: usuario.tenant_id (UUID)
    API-->>Browser: Respuesta autorizada
```

La identidad del usuario es el `sub` del JWT (Clerk User ID, ej. `user_abc123`). El `tenant_id` (UUID) se resuelve siempre desde la base de datos — nunca se confía en el cliente para proveerlo (Zero-Trust).

---

## Flujo de Registro de Transacción por Voz

```mermaid
sequenceDiagram
    actor Usuario
    participant UI as DataCapture.tsx
    participant Proxy
    participant Upload as /upload/audio
    participant Whisper as OpenAI Whisper
    participant LLM as GPT-4o-mini
    participant DB as PostgreSQL

    Usuario->>UI: Graba "Gasté $500 en gasolina"
    UI->>Proxy: POST /upload/audio (audio/webm)
    Proxy->>Upload: Forward
    Upload->>Whisper: Transcripción de audio
    Whisper-->>Upload: "Gasté $500 en gasolina"
    Upload->>LLM: Extracción estructurada (Pydantic)
    Note over Upload,LLM: Regex override: "gasté" → es_ingreso=False
    LLM-->>Upload: {monto:500, descripcion:"Gasolina", es_ingreso:false, ...}
    Upload->>DB: resolve_sub_categoria_id(...)
    Upload-->>UI: {monto:500, es_ingreso:false, sub_categoria_id:5, ...}
    UI->>UI: Muestra preview al usuario
    Usuario->>UI: Confirma
    UI->>Proxy: POST /transacciones/ {monto:-500, ...}
    Proxy->>DB: INSERT Transaccion (monto negativo = gasto)
    DB-->>UI: TransaccionResponse
```

---

## Arquitectura del Sistema de Agentes IA

```mermaid
graph TD
    Input["Mensaje del Usuario (WebSocket)"] --> Router

    subgraph Clasificador["Router Semántico (GPT-4o-mini)"]
        Router{"clasificar_intencion_async()"}
    end

    Router -->|CONSULTA_FISCAL| FiscalAgent
    Router -->|PROYECCION_MATEMATICA| MathAgent
    Router -->|ANALISIS_DATOS| DataAgent
    Router -->|SOPORTE_GENERAL| SupportAgent
    Router -->|BLOQUEADO| Guardrail["Respuesta de bloqueo\n(Anti prompt-injection)"]

    subgraph FiscalAgent["Agente Fiscal (RAG)"]
        F1["ChromaDB — leyes_fiscales"] --> F2["GPT-4o-mini + contexto legal"]
    end

    subgraph MathAgent["Agente Matemático (Tool Calling)"]
        M1["calcular_interes_compuesto()"] --> M2["GPT-4o-mini formatea resultado"]
    end

    subgraph DataAgent["Agente de Datos (Tool Calling)"]
        D1["obtener_resumen_transacciones(tenant_id)"] --> D2["GPT-4o-mini analiza patrones"]
    end

    subgraph SupportAgent["Agente de Soporte (Coach)"]
        S1["GPT-4o-mini temp=0.7\n(tono sarcástico-motivacional)"]
    end

    FiscalAgent --> Output["Respuesta al Usuario"]
    MathAgent --> Output
    DataAgent --> Output
    SupportAgent --> Output
    Guardrail --> Output
```

---

## Modelo de Datos Simplificado

```mermaid
erDiagram
    Tenant ||--o{ Usuario : tiene
    Tenant ||--o{ CuentaFinanciera : posee
    Tenant ||--o{ Transaccion : agrupa
    Usuario ||--o{ CuentaFinanciera : administra
    Usuario ||--o{ MetaFinanciera : define
    Usuario ||--o{ PortafolioInversion : mantiene
    Usuario ||--|| PerfilGamificacion : tiene
    CuentaFinanciera ||--o{ Transaccion : registra
    Transaccion }o--|| SubCategoria : clasifica
    SubCategoria }o--|| Categoria : pertenece
    InstrumentoCatalogo ||--o{ PortafolioInversion : referencia

    Tenant {
        UUID id PK
        string nombre
    }
    Usuario {
        string id PK
        UUID tenant_id FK
        int score_resiliencia
        decimal flujo_caja_libre_mensual
    }
    Transaccion {
        UUID id PK
        UUID cuenta_id FK
        UUID tenant_id FK
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
```

> El signo del campo `monto` determina el tipo de transacción: **positivo = ingreso**, **negativo = gasto**.

---

## Convenciones del Proyecto

- **Aislamiento por tenant:** Toda consulta a la DB filtra por `tenant_id` resuelto desde el JWT, nunca desde el cliente.
- **Montos firmados:** El frontend envía y el backend almacena `monto` con signo para simplificar agregaciones.
- **Keyword override:** La clasificación `es_ingreso` del LLM puede ser sobreescrita por patrones regex (`gasté`, `gané`, etc.) para mayor determinismo.
- **Bootstrap idempotente:** `system_init.py` crea categorías, subcategorías y logros en producción sin depender de scripts de seed.
- **Contexto financiero fresco:** El WebSocket del asesor recalcula el resumen financiero en cada mensaje para evitar respuestas con datos obsoletos.

---

## Documentación Detallada

- [Backend — API, Agentes IA y Despliegue Local](./backend/README.md)
