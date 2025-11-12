# Node.js Worker Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json tsconfig.json ./
COPY apps/workers/package.json ./apps/workers/
COPY packages/shared ./packages/shared

# Install pnpm and dependencies
RUN npm install -g pnpm@8.15.4
WORKDIR /app/apps/workers
RUN pnpm install --frozen-lockfile

# Copy source code
COPY apps/workers ./

# Build TypeScript
RUN pnpm build

# Create non-root user
RUN addgroup -g 1001 -S appuser && adduser -S -u 1001 -G appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run the worker
CMD ["node", "dist/index.js"]

