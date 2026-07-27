FROM node:22-alpine3.22 AS client-build

WORKDIR /app/client

COPY client/package.json client/package-lock.json ./
RUN npm ci

COPY client/ ./
RUN npm run build

FROM node:22-alpine3.22 AS server-runtime

WORKDIR /app/server

ENV NODE_ENV=production
ENV PORT=3000

COPY server/package.json server/package-lock.json ./
RUN npm ci --omit=dev

COPY server/ ./
COPY --from=client-build /app/client/dist /app/client/dist

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:3000/api/ping || exit 1

CMD ["node", "./bin/www"]