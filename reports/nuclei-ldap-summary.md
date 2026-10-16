# Reporte de Vulnerabilidades con Nuclei - LDAP Authentication API

## 📋 Resumen del Escaneo
- **Objetivo analizado:** `http://127.0.0.1:8000` (FastAPI LDAP Auth Service)
- **Herramienta:** ProjectDiscovery Nuclei v3.11.1
- **Fecha:** Octubre 2026
- **Total de plantillas evaluadas:** 6,330+ (CVEs, exposures, misconfigurations, auth, APIs)
- **Total de hallazgos:** 14 alertas (Informational / Misconfiguration)

---

## 🔍 Hallazgos Principales

### 1. CORS Misconfiguration: Permissive Wildcard / Arbitrary Origin
- **Severidad:** Media / Info
- **Detalle:** El middleware de CORS en `fastapi/app/main.py` está configurado con `allow_origins=["*"]`, permitiendo solicitudes desde cualquier origen arbitrario (`cors_origin="https://127.0.0.1.f3xaf.com"`).
- **Impacto:** Cualquier sitio web malicioso podría inducir al navegador de la víctima a interactuar con los endpoints de autenticación y leer respuestas no deseadas.
- **Remediación:** Restringir `allow_origins` exclusivamente a los dominios del frontend autorizados (e.g., `["http://localhost:5173", "http://localhost"]`).

### 2. Exposición de Documentación y Especificación OpenAPI
- **Rutas identificadas:**
  - `GET /docs` (Swagger UI)
  - `GET /redoc` (ReDoc)
  - `GET /openapi.json` (Especificación completa del API)
- **Severidad:** Info / Reconocimiento
- **Impacto:** Facilita a un atacante el mapeo de rutas, parámetros esperados, esquemas de solicitud (`LoginRequest`, `TokenResponse`) y códigos de error.
- **Remediación:** En entornos de producción, desactivar o proteger la documentación:
  ```python
  app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
  ```

### 3. Cabeceras de Seguridad HTTP Faltantes
Nuclei detectó la ausencia de cabeceras estándar para protección contra ataques web:
- `Content-Security-Policy (CSP)`
- `Strict-Transport-Security (HSTS)`
- `X-Frame-Options` (Protección contra Clickjacking)
- `X-Content-Type-Options: nosniff` (Prevención de MIME-sniffing)
- `Referrer-Policy`
- `Permissions-Policy`
- `Cross-Origin-Opener-Policy (COOP)`
- `Cross-Origin-Embedder-Policy (COEP)`
- `Cross-Origin-Resource-Policy (CORP)`
- `X-Permitted-Cross-Domain-Policies`

**Remediación:** Agregar un middleware en FastAPI que inyecte estas cabeceras en todas las respuestas HTTP.

---

## 📁 Archivos Relacionados
- `reports/nuclei-ldap-results.jsonl`: Formato estructurado JSONL con cada comprobación y evidencia HTTP.
- `reports/nuclei-ldap-report.txt`: Registro en texto plano de las coincidencias.
