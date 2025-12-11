FROM node:22-slim AS base
RUN corepack enable

WORKDIR /app


FROM base AS deps


COPY package.json pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile


FROM deps AS build

# Copy actual source
COPY . .

# If t3-env uses process.env during build, set the required variables here:
# ARG VITE_API_URL
# ENV VITE_API_URL=$VITE_API_URL

# Build the frontend
RUN pnpm build


# ------------------------------------------------------------
# 4A) PRODUCTION — Serve static files via NGINX (recommended)
# ------------------------------------------------------------
FROM nginx:1.25-alpine AS nginx

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Add your custom config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built frontend to NGINX static directory
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]


# ------------------------------------------------------------
# 4B) OPTIONAL — Pure static output (no server)
# ------------------------------------------------------------
# FROM build AS static
# CMD ["pnpm", "preview"]
