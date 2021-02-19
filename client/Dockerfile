FROM node:10-alpine3.9 as builder
WORKDIR /code
COPY . .
RUN npm install --registry=https://registry.npm.taobao.org && npm run build:prod
FROM nginx:1.19.2-alpine
COPY --from=builder /code/dist /usr/share/nginx/html
