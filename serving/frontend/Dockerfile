FROM node:18-slim
WORKDIR /app
COPY serving/frontend/package*.json ./
RUN npm install
COPY serving/frontend/ .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]