# MentorLingua Web

## Requisitos
- Node.js 18+

## Rodar localmente

```bash
cd frontend
npm install
npm run dev
```

## Variáveis de ambiente

- `VITE_API_URL` (ex.: `http://localhost:8000`)

## Arquitetura (pronta para migração para React Native)

- `src/core` -> apiClient + storage (pode trocar por AsyncStorage no mobile)
- `src/services` -> camada de chamadas REST
- `src/features` -> telas por domínio
- `src/shared` -> componentes e layouts reutilizáveis
- `src/hooks` -> hooks de estado
