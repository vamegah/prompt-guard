# Build stage
FROM node:24-alpine AS build

WORKDIR /app

ARG VITE_API_BASE_URL=/api/v1
ARG VITE_API_KEY=
ARG VITE_USER_ID=
ARG VITE_ORG_ID=
ARG VITE_ROLE=

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_API_KEY=$VITE_API_KEY
ENV VITE_USER_ID=$VITE_USER_ID
ENV VITE_ORG_ID=$VITE_ORG_ID
ENV VITE_ROLE=$VITE_ROLE

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:stable-alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
