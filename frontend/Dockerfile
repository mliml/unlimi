# Multi-stage build for both landing and app

# Stage 1: Build landing page
FROM node:18-alpine AS landing-builder
WORKDIR /app/landing
COPY landing/package*.json ./
RUN npm ci
COPY landing/ ./
RUN npm run build

# Stage 2: Build main app
FROM node:18-alpine AS app-builder
WORKDIR /app/app
COPY app/package*.json ./
RUN npm ci
COPY app/ ./
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Stage 3: Production nginx image
FROM nginx:alpine
# Copy built files from both builders
COPY --from=landing-builder /app/landing/dist /usr/share/nginx/html/landing
COPY --from=app-builder /app/app/dist /usr/share/nginx/html/app
# Copy nginx config will be done via volume mount in docker-compose
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
