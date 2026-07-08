# --- Fase 1: build ---
FROM node:22-slim AS builder
WORKDIR /app

# Copio prima i file delle dipendenze (cache di layer, come nel backend)
COPY package.json package-lock.json ./
RUN npm ci

# Copio il resto e compilo
COPY . .
RUN npm run build

# --- Fase 2: runtime ---
FROM node:22-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copio solo l'output standalone + asset statici
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]