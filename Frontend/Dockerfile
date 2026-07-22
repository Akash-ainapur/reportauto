FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build --if-present

FROM node:20-slim
WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /app ./

EXPOSE 3000
USER appuser
CMD ["npm", "start"]