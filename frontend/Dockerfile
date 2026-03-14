FROM node:20-alpine

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY . .

RUN corepack enable && pnpm build

CMD ["sh", "-c", "corepack enable && pnpm start --hostname 0.0.0.0 --port 3000"]
