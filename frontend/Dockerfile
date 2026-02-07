# ---------- builder ----------
FROM node:18-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ---------- production ----------
FROM nginx:alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html
COPY infrastructure/docker/nginx/frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
