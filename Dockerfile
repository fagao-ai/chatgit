FROM node:22-alpine AS build-stage

WORKDIR /app

COPY ./web/package*.json ./
COPY ./web/pnpm-lock.yaml ./

RUN npm config set registry https://registry.npmmirror.com/

RUN npm install -g pnpm

RUN pnpm install

COPY ./web .

RUN cd /app && pnpm build-only

FROM python:3.12-slim AS production-stage

WORKDIR /app

COPY . /app

RUN rm -rf /app/web

COPY ./docker/supervisor /etc/supervisor

RUN test -d /data/logs || mkdir -p /data/logs

RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list.d/debian.sources \
    && sed -i s@/security.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends htop vim curl procps net-tools nginx \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple \
    && pip install uv \
    && uv venv \
    && uv sync

COPY --from=build-stage /app/dist /usr/share/nginx/html

RUN rm -rf /etc/nginx/sites-enabled/*

COPY docker/nginx/chatgit.conf /etc/nginx/sites-enabled/chatgit.conf

EXPOSE 80

ENTRYPOINT [ "sh", "/app/docker/entrypoint.sh" ]