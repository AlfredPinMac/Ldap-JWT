# Lab Guide: Pokémon Dashboard with LDAP + JWT + Pinia (Vue.js)

This lab implements the full architecture for centralized identity and authentication based on **LDAP** and distributed authorization using **JSON Web Tokens (JWT)** as a **Bearer Token**.

---

## 🏗️ 3-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ 1. LDAP Auth Service (:8000)                                │
│    • OpenLDAP (:389) + FastAPI (:8000)                      │
│    • Endpoint: POST /login -> Validates against LDAP & JWT  │
└───────────────────────────┬─────────────────────────────────┘
                            │ (1. Returns JWT)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Frontend Vue.js + Pinia (:5173 / :80)                    │
│    • Login: Authenticates against LDAP Service              │
│    • Pinia Store: Saves JWT in reactive state               │
│    • Axios Interceptor: Injects "Authorization: Bearer <JWT>"│
│    • Dashboard: Displays Pokémon collection                 │
│    • Form: Registers new Pokémon entries                    │
└───────────────────────────┬─────────────────────────────────┘
                            │ (2. Sends requests with Bearer JWT)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Backend Pokémon API (:5000)                              │
│    • Middleware: Validates presence & signature of JWT      │
│    • GET /api/pokemons  -> Lists all Pokémon                │
│    • POST /api/pokemons -> Adds new Pokémon                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Step-by-Step Instructions to Run the Services

### Terminal 1: LDAP Service + Auth API (Port 8000)

1. Inside the root directory:
   ```bash
   docker compose down
   docker compose up -d --build
   ```

2. Load initial LDAP users (if not previously populated):
   ```bash
   docker cp ldap/users.ldif openldap:/tmp/users.ldif
   docker exec openldap ldapadd -x -H ldap://localhost -D "cn=admin,dc=example,dc=com" -w adminpassword -f /tmp/users.ldif
   ```

   *Available test credentials:*
   - **Username:** `alice` | **Password:** `alice123`
   - **Username:** `bob` | **Password:** `bob123`

---

### Terminal 2: Pokémon Backend API (Port 5000)

1. Navigate to `pokemon-backend`:
   ```bash
   cd pokemon-backend
   ```

2. (Optional) Create and activate virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start backend server:
   ```bash
   python run.py
   ```
   *Running on `http://localhost:5000` with Swagger docs at `http://localhost:5000/docs`.*

---

### Terminal 3: Frontend Vue.js + Pinia (Port 5173 / Port 80)

1. Navigate to `pokemon-frontend`:
   ```bash
   cd pokemon-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start Vite dev server:
   ```bash
   npm run dev
   ```

4. Open in browser:
   `http://localhost:5173`

---

## 📹 Demonstration Video Workflow

During the recorded demonstration, follow this sequence:

1. **Open Browser Developer Tools**:
   - Press `F12` and keep both the **Console** and **Network** tabs accessible.

2. **LDAP Authentication Demo**:
   - On the login screen (`/login`), enter username `alice` and password `alice123`.
   - Click **Sign In with LDAP**.
   - Show in the console the `POST /login` call returning `200 OK` and delivering the JWT `access_token`.
   - Confirm Pinia saves the token and redirects to the Dashboard.

3. **Dashboard Demo (`GET /api/pokemons`)**:
   - On the Dashboard, highlight the console group: `[HTTP REQUEST] GET http://localhost:5000/api/pokemons`.
   - Verify the injected header: `Authorization: Bearer [PROTECTED]`.
   - Point out the loaded Pokémon collection with types, stats, and official sprites.
   - Click the **JWT** button on the navbar to show the active Bearer token in the modal.

4. **Add Pokémon Demo (`POST /api/pokemons`)**:
   - Click **+ New Pokémon** in the top navigation bar.
   - Select a quick preset (e.g. **Rayquaza**, **Dragonite**) or configure a custom one.
   - Click **Save Pokémon (POST)**.
   - Inspect the `POST /api/pokemons` request payload and status in console/network tab.
   - Verify redirection back to the Dashboard with the newly created entry rendered.

5. **Security Enforcement Demo (Unauthorized Access Rejection)**:
   - Make a direct request to `http://localhost:5000/api/pokemons` using `curl` without an Authorization header:
     ```bash
     curl -i http://localhost:5000/api/pokemons
     ```
   - Show that the API responds with `401 Unauthorized`.

---

## 🐙 GitHub Repository Setup

To push each individual component to GitHub:

### 1. LDAP Auth API Repository (`ldap-auth-api`)
```bash
cd "c:\Users\jayal\Documents\Universidad\9no Semestre\Ciberseguridad\ldap"
git init
git add fastapi/ ldap/ docker-compose.yml README.md .gitignore
git commit -m "feat: LDAP authentication API with JWT generation and CORS"
git branch -M main
git remote add origin <URL_REPO_1_GITHUB>
git push -u origin main
```

### 2. Pokémon Backend Repository (`pokemon-backend-api`)
```bash
cd "c:\Users\jayal\Documents\Universidad\9no Semestre\Ciberseguridad\ldap + Framework\pokemon-backend"
git add .
git commit -m "feat: Pokemon backend API with Bearer JWT validation"
git push -u origin main
```

### 3. Pokémon Frontend Repository (`pokemon-frontend-vue`)
```bash
cd "c:\Users\jayal\Documents\Universidad\9no Semestre\Ciberseguridad\ldap + Framework\pokemon-frontend"
git add .
git commit -m "feat: Vue 3 + Pinia Pokemon frontend with JWT interceptor and LDAP auth"
git push -u origin main
```
