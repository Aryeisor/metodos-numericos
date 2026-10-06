# Frontend Vue compilado y servido por nginx (modo tipo producción para Docker).
# El modo desarrollo (npm run dev) no usa este archivo.

# --- Etapa 1: compilación ---
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# En Docker la API se pide al mismo origen (nginx hace de proxy a /api/), así
# que la URL base es relativa. Vite toma las variables VITE_* del entorno del
# proceso con prioridad sobre los archivos .env.
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# --- Etapa 2: servidor estático ---
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
