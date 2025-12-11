# Make VITE_API_URL available before copying source
ARG VITE_API_URL

FROM node:22-slim AS base
RUN corepack enable
WORKDIR /app

FROM base AS deps
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM deps AS build

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Must come after ENV is set
COPY . .

# Build frontend
RUN pnpm build
