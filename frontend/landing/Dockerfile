FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Output stage - just copy the dist folder
FROM scratch AS export
COPY --from=build /app/dist /dist
