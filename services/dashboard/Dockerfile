# Multi-stage build.
# Stage 1: build the React app
# Stage 2: serve with nginx

FROM node:18-slim AS builder

WORKDIR /app
COPY package.json .
RUN npm install
COPY public/ public/
COPY src/ src/
RUN npm run build

# --- Final stage ---
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Custom nginx config to support React Router and proxy to gateway
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
