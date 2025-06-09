# CodeQuest Arena Frontend

Modern, high-performance frontend for CodeQuest Arena.  
Uses **React + Vite** for instant reloads, speedy DX, and scalable modular architecture.

---

## 🚀 Getting Started

### 1. Install Dependencies

```sh
cd frontend
npm install
```

### 2. Start the Development Server

```sh
npm run dev
```

The app will run locally at [http://localhost:3000](http://localhost:3000) (default Vite port).

---

## 📦 Project Structure

```
frontend/
├── public/            # Static files
├── src/
│   ├── api/           # API clients (per backend module)
│   ├── components/    # Shared/glassy UI components
│   ├── features/      # Feature modules (PRs, bugs, gamification, etc)
│   ├── hooks/         # Custom React hooks
│   ├── layouts/       # Layout/shell, main layout cards, etc.
│   ├── pages/         # Route-level components (Home, Dashboard, etc)
│   ├── styles/        # Global theme + glassmorphism CSS
│   ├── utils/         # Helpers, formatting, etc
│   ├── App.jsx        # Root app
│   └── main.jsx       # Mount point
├── index.html         # Entry HTML
├── package.json
└── vite.config.js
```

---

## 🛠️ Tech Stack

- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [React Router](https://reactrouter.com/) (for routes)
- [Axios](https://axios-http.com/) (API calls)
- Glassmorphism theme, dark mode by default, ready for theming

---

## 🔗 Connecting to the Backend

Set the backend API base URL in environment variables as needed (`VITE_API_URL`).  
Default: assumes backend is running at `http://localhost:8000/`.

---

## 🖥️ Build for Production

```sh
npm run build
```

Output goes to the `dist/` folder.

---

## ⚡️ Features Structure

- PR Integration: `/features/pr/`
- Bug Logging & Dispute: `/features/bug/`
- Gamification: `/features/gamification/`
- Redeem Center: `/features/redeem/`
- Analytics: `/features/analytics/`
- Notifications: `/features/notifications/`
- Security & Fairness: `/features/security/`
- Core glassy UI/UX: `/components/glass/`, `/styles/`

---

## ✨ UI/UX

- Glassmorphism styling with frosted effects, neon highlights
- Responsive, mobile-friendly
- Animations ready (see `/styles/`)

---

## 🤝 Contributions

Open to UI tweaks, bugfixes, and new feature suggestions!

---
