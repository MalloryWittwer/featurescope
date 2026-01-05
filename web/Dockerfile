FROM node:18-alpine

WORKDIR /app

COPY public/ ./public
COPY src/ ./src
COPY package.json .

RUN npm install

EXPOSE 3000

CMD ["npm", "start"]