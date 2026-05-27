# IoT Bay — Frontend

React + Vite SPA for the IoT Bay marketplace. See the [root README](../README.md) for full setup, features, and API documentation.

## Commands

```bash
npm install
npm run dev      # http://localhost:5173
npm run build
npm run lint
```

## API client

All requests go through `src/api/apiClient.js` with `credentials: "include"` so Flask session cookies are sent. Default base URL: `http://localhost:5000/api`.

Order-specific helpers live in `src/api/orders.js`.
