# Etapa 1: Construcción (Build)
FROM node:18-alpine AS build

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package.json package-lock.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código del frontend
COPY . .

# Generar los archivos listos para producción
RUN npm run build

# Etapa 2: Servidor de producción (Nginx)
FROM nginx:stable-alpine

# Copiar los archivos construidos desde la etapa anterior a la carpeta de Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Exponer el puerto 80 (puerto estándar web)
EXPOSE 80

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
