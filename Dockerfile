FROM debian:bullseye-slim

RUN apt update \
        && apt install --assume-yes \
        wget \
        build-essential \
        uuid-dev \
        git \
        libsqlite3-dev \
        uuid-runtime \
        libmbedtls-dev \
        sqlite3

WORKDIR /tmp

RUN wget http://download.zeromq.org/zeromq-2.1.7.tar.gz \
        && tar xzf zeromq-2.1.7.tar.gz \
        && cd zeromq-2.1.7 \
        && ./configure \
        && make \
        && make install \
        && ldconfig

WORKDIR /app
RUN git clone https://github.com/tengelisconsulting/mongrel2 \
        && cd mongrel2 \
        && make \
        && make all install

        # cleanup
RUN apt remove --assume-yes \
        wget \
        git \
        build-essential \
        && rm -r /tmp/*
        # end cleanup

RUN rm -r /app/mongrel2

COPY ./entrypoint.sh ./entrypoint.sh
COPY ./conf.py ./conf.py

ENTRYPOINT [ "/app/entrypoint.sh" ]
