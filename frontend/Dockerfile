FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG BACKEND_URL=http://localhost:8000

ENV BACKEND_URL=$BACKEND_URL

RUN npm run build

EXPOSE 8080

CMD ["sh", "-c", "npm run start -- --port ${PORT:-8080}"]
