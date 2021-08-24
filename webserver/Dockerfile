FROM openresty/openresty:1.19.3.2-3-alpine-fat

RUN apk add --no-cache perl curl git openssh libbson mongo-c-driver-dev
RUN opm get ledgetech/lua-resty-http SkyLothar/lua-resty-jwt

RUN luarocks install lua-mongo

COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY nginx-default.conf /etc/nginx/conf.d/default.conf

RUN mkdir /etc/nginx/lua

COPY ./scripts /etc/nginx/lua

EXPOSE 8080