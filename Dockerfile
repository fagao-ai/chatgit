FROM python:3.12-slim

WORKDIR /app

COPY . /app

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

ENTRYPOINT [ "sh", "/app/docker/entrypoint.sh" ]