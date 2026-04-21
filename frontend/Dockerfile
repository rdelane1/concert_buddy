FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

RUN npm run build

EXPOSE 8080

CMD ["sh", "-c", "npm run start -- --port ${PORT:-8080}"]
