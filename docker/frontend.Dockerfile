# SEO Monster - Frontend Dockerfile
# React + Vite application

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/pnpm-lock.yaml* ./

# Install pnpm and dependencies
RUN npm install -g pnpm && \
    pnpm install --frozen-lockfile

# Copy source code
COPY frontend/ .

# Build the application
RUN pnpm run build

# Production stage - serve with nginx
FROM nginx:alpine

# Copy custom nginx config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user
RUN adduser -D -u 1000 seomonster && \
    chown -R seomonster:seomonster /usr/share/nginx/html && \
    chown -R seomonster:seomonster /var/cache/nginx && \
    chown -R seomonster:seomonster /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R seomonster:seomonster /var/run/nginx.pid

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
