FROM node:22-alpine AS build-stage

WORKDIR /app

COPY ./web/package*.json ./
COPY ./web/pnpm-lock.yaml ./

RUN npm config set registry https://registry.npmmirror.com/

RUN npm install -g pnpm

RUN pnpm install

COPY ./web .

RUN cd /app && pnpm build:build-only

FROM nginx:alpine
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

RUN apk update && \
    apk add --no-cache curl htop vim curl procps net-tools && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN rm /etc/nginx/conf.d/default.conf
RUN rm -rf /etc/nginx/sites-enabled/*

COPY docker/nginx/chatgit.conf /etc/nginx/sites-enabled/chatgit.conf

COPY --from=build-stage /app/dist /usr/share/nginx/html

RUN chown -R nginx:nginx /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
