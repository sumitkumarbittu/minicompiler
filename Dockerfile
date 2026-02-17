FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    clang \
    llvm \
    graphviz \
    build-essential \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY . /app
ENV PATH="/app:${PATH}"

ENTRYPOINT ["/app/minipycc"]
