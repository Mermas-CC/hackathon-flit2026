# Etapa 1: Construcción de los archivos estáticos de React
FROM node:20-slim AS build

WORKDIR /app

# Instalar pnpm para concordar con la instalación rápida del usuario
RUN npm install -g pnpm

# Copiar archivos de dependencias
COPY package.json pnpm-lock.yaml* ./

# Instalar dependencias
RUN pnpm install --frozen-lockfile

# Copiar todo el código y compilar la build de producción de Vite
COPY . .
RUN pnpm build

# Etapa 2: Servir los archivos construidos usando Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx corre en el puerto 80 por defecto
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
