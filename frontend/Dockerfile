# Stage 1: Build the Vue.js application
FROM node:18-alpine as build-stage

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install
# Install flatpickr date picker
RUN npm install flatpickr vue-flatpickr-component --save

# Copy the rest of the application code
COPY . .

# Pass API base URL as build argument (can be overridden in docker-compose.yml)
ARG VITE_API_BASE_URL=http://localhost:5001
# Create production .env file with the provided API URL
RUN echo "VITE_API_BASE_URL=${VITE_API_BASE_URL}" > .env.production

# Build the application
# Variables need to be available during the build
RUN npm run build

# Stage 2: Serve the built application using Nginx
FROM nginx:stable-alpine

# Make sure the html directory exists in both standard locations
RUN mkdir -p /usr/share/nginx/html /etc/nginx/html

# Copy built assets from build stage to both possible locations
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY --from=build-stage /app/dist /etc/nginx/html

# Create Nginx config that handles browser requests properly
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
\
    # Handle API requests including OPTIONS/CORS \
    location ~ ^/(api|rankings|bracket|games|schedule)/ { \
        if ($request_method = OPTIONS) { \
            add_header Access-Control-Allow-Origin "*"; \
            add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE, PATCH"; \
            add_header Access-Control-Allow-Headers "Content-Type, Authorization, Accept, X-Requested-With"; \
            add_header Access-Control-Max-Age 1728000; \
            add_header Content-Type "text/plain charset=UTF-8"; \
            add_header Content-Length 0; \
            return 204; \
        } \
\
        # Forward requests to backend \
        proxy_pass http://backend:5001; \
        proxy_http_version 1.1; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
    } \
\
    # Serve static frontend files \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
\
    # Redirect server error pages to static page \
    error_page 500 502 503 504 /50x.html; \
    location = /50x.html { \
        root /usr/share/nginx/html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx when the container launches
CMD ["nginx", "-g", "daemon off;"] 