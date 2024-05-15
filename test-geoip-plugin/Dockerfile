FROM  kong/kong-gateway:3.6.1.3

USER root

RUN apt update && apt-get install software-properties-common -y && apt update

RUN add-apt-repository ppa:maxmind/ppa

RUN apt update && apt install unzip libmaxminddb0 libmaxminddb-dev mmdb-bin

RUN luarocks install lua-resty-ipmatcher 

RUN mkdir /usr/local/share/lua/5.1/kong/plugins/gaius-geoip

COPY ./kong/plugins/gaius-geoip /usr/local/share/lua/5.1/kong/plugins/gaius-geoip

EXPOSE 8001
EXPOSE 8000
