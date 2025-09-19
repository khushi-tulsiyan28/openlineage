FROM openresty/openresty:1.21.4.1-0-alpine

RUN apk add --no-cache \
    curl \
    openssl \
    git \
    make \
    gcc \
    musl-dev \
    lua5.1 \
    lua5.1-dev

RUN cd /tmp && \
    git clone https://github.com/ledgetech/lua-resty-http.git && \
    cp -r lua-resty-http/lib/resty /usr/local/openresty/lualib/ && \
    git clone https://github.com/cdbattags/lua-resty-jwt.git && \
    cp -r lua-resty-jwt/lib/resty/jwt* /usr/local/openresty/lualib/resty/ && \
    git clone https://github.com/openresty/lua-resty-string.git && \
    cp -r lua-resty-string/lib/resty/string.lua /usr/local/openresty/lualib/resty/ && \
    rm -rf /tmp/*

COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY conf.d/ /usr/local/openresty/nginx/conf/conf.d/
COPY lua/ /usr/local/openresty/nginx/lua/

RUN mkdir -p /var/cache/nginx /var/log/nginx /etc/nginx/ssl

RUN chown -R nobody:nobody /var/cache/nginx /var/log/nginx

EXPOSE 8080

CMD ["/usr/local/openresty/bin/openresty", "-g", "daemon off;"]
