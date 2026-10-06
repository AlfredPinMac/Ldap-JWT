# Guía de la Práctica: Dashboard de Pokémones con LDAP + JWT + Pinia (Vue.js)

Esta práctica implementa la arquitectura completa de autenticación centralizada basada en **LDAP** y autorización distribuida con **JSON Web Tokens (JWT)** como **Bearer Token**.

---

## 🏗️ Arquitectura de los 3 Repositorios

```
┌─────────────────────────────────────────────────────────────┐
│ 1. LDAP Auth Service (:8000)                                │
│    • OpenLDAP (:389) + FastAPI (:8000)                      │
│    • Endpoint: POST /login -> Valida con LDAP y genera JWT  │
└───────────────────────────┬─────────────────────────────────┘
                            │ (1. Retorna JWT)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Frontend Vue.js + Pinia (:5173)                          │
│    • Login: Autentica contra LDAP Service                   │
│    • Pinia Store: Guarda JWT en estado reactivo             │
│    • Interceptor Axios: Inyecta "Authorization: Bearer <JWT>"│
│    • Dashboard: Lista Pokémones                             │
│    • Formulario: Alta de nuevos Pokémones                   │
└───────────────────────────┬─────────────────────────────────┘
                            │ (2. Envía requests con Bearer JWT)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Backend Pokémon API (:5000)                              │
│    • Middleware: Valida presencia y firma del Bearer JWT    │
│    • GET /api/pokemons  -> Lista Pokémones                  │
│    • POST /api/pokemons -> Agrega nuevo Pokémon             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Paso a Paso para Levantar los 3 Servicios

### Terminal 1: Servicio LDAP + Auth API (Puerto 8000)

1. En la carpeta raíz `ldap`:
   ```bash
   docker compose down
   docker compose up -d --build
   ```

2. Cargar los usuarios LDAP iniciales (si no se han cargado previamente):
   ```bash
   docker cp ldap/users.ldif openldap:/tmp/users.ldif
   docker exec openldap ldapadd -x -H ldap://localhost -D "cn=admin,dc=example,dc=com" -w adminpassword -f /tmp/users.ldif
   ```

   *Credenciales de prueba disponibles:*
   - **Usuario:** `alice` | **Contraseña:** `alice123`
   - **Usuario:** `bob` | **Contraseña:** `bob123`

---

### Terminal 2: Pokémon Backend API (Puerto 5000)

1. Ir a la carpeta `pokemon-backend`:
   ```bash
   cd pokemon-backend
   ```

2. (Opcional) Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Iniciar el backend:
   ```bash
   python run.py
   ```
   *Estará corriendo en `http://localhost:5000` con Swagger en `http://localhost:5000/docs`.*

---

### Terminal 3: Frontend Vue.js + Pinia (Puerto 5173)

1. Ir a la carpeta `pokemon-frontend`:
   ```bash
   cd pokemon-frontend
   ```

2. Instalar dependencias (si es primera vez):
   ```bash
   npm install
   ```

3. Iniciar el servidor Vite:
   ```bash
   npm run dev
   ```

4. Abrir en el navegador:
   `http://localhost:5173`

---

## 📹 Guía para Grabar el Video Demostrativo

En el video entregable, sigue este flujo para mostrar claramente los requerimientos solicitados:

1. **Abrir la Consola de Desarrollador del Navegador**:
   - Presiona `F12` y abre la pestaña **Console** (y mantén visible la pestaña **Network** si deseas).

2. **Demostración de Login con LDAP**:
   - En la pantalla de login (`http://localhost:5173/login`), selecciona o ingresa el usuario `alice` y contraseña `alice123`.
   - Haz clic en **Iniciar Sesión con LDAP**.
   - Muestra en la consola cómo se envía la petición `POST /login` al API de LDAP y se recibe el JWT (`access_token`).
   - Muestra cómo Pinia almacena el token y redirige al Dashboard.

3. **Demostración del Dashboard (GET /api/pokemons)**:
   - Al entrar al Dashboard, muestra en la consola el grupo `[HTTP REQUEST] GET http://localhost:5000/api/pokemons`.
   - Señala claramente la línea:
     `🔑 [JWT INJECTED VIA PINIA] Authorization: Bearer <token>`
   - Muestra cómo la lista de Pokémones iniciales (Pikachu, Charizard, Blastoise, etc.) se renderiza con sus estadísticas y tipos.
   - También puedes hacer clic en el botón **JWT** en la barra superior o en **Recargar GET** para evidenciar la inyección en cada consulta.

4. **Demostración de Alta de Pokémon (POST /api/pokemons)**:
   - Haz clic en el botón **+ Nuevo Pokémon** en la barra superior.
   - Selecciona una plantilla rápida (por ejemplo **Rayquaza**, **Dragonite**, o crea uno personalizado).
   - Haz clic en **Guardar Pokémon (POST)**.
   - Muestra en la consola el request `[HTTP REQUEST] POST http://localhost:5000/api/pokemons` con el token Bearer presente en los headers y los datos en el body.
   - Muestra cómo la aplicación redirige automáticamente al Dashboard y el nuevo Pokémon aparece en el listado.

5. **Demostración de Seguridad (Token requerido)**:
   - (Opcional/Recomendado): Muestra en Swagger (`http://localhost:5000/docs`) o con `curl` cómo si intentas hacer `GET /api/pokemons` sin el header `Authorization: Bearer <token>`, el backend responde `401 Unauthorized`.

---

## 🐙 Configuración de los 3 Repositorios de GitHub

Para subir cada proyecto a su propio repositorio en GitHub:

### 1. Repositorio LDAP Auth API (`ldap-auth-api`)
```bash
cd c:\Users\jayal\Documents\Universidad\9no Semestre\Ciberseguridad\ldap
git init
git add fastapi/ ldap/ docker-compose.yml README.md .gitignore
git commit -m "feat: LDAP authentication API with JWT generation and CORS"
git branch -M main
git remote add origin <URL_REPO_1_GITHUB>
git push -u origin main
```

### 2. Repositorio Pokémon Backend (`pokemon-backend-api`)
```bash
cd c:\Users\jayal\Documents\Universidad\9no Semestre\Ciberseguridad\ldap\pokemon-backend
git init
git add .
git commit -m "feat: Pokemon backend API with Bearer JWT validation"
git branch -M main
git remote add origin <URL_REPO_2_GITHUB>
git push -u origin main
```

### 3. Repositorio Pokémon Frontend (`pokemon-frontend-vue`)
```bash
cd c:\Users\jayal\Documents\Universidad\9no Semestre\Ciberseguridad\ldap\pokemon-frontend
git init
git add .
git commit -m "feat: Vue 3 + Pinia Pokemon frontend with JWT interceptor and LDAP auth"
git branch -M main
git remote add origin <URL_REPO_3_GITHUB>
git push -u origin main
```
