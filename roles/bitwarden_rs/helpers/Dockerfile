ARG IMAGE=ubuntu:noble
FROM $IMAGE
ARG RELEASE
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update &&  apt install -q -y git build-essential libssl-dev libsqlite3-dev curl pkg-config
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh /dev/stdin --profile minimal -y --default-toolchain none
RUN mkdir /build && git clone https://github.com/dani-garcia/vaultwarden /build/vaultwarden
WORKDIR /build/vaultwarden
RUN git checkout $RELEASE
RUN . $HOME/.cargo/env && cargo build --features sqlite --release
RUN cp target/release/vaultwarden /output/bitwarden_rs
