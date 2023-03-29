FROM python:3.11.2-slim

LABEL org.opencontainers.image.source=https://github.com/hiboma/summaru/pulls

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV POETRY_HOME=/usr/local/poetry
ENV PATH="/usr/local/poetry/bin:$PATH"
ENV RUST_VERSION stable
ENV PATH $PATH:/root/.cargo/bin

RUN apt-get -y update && \
    apt-get upgrade -qqy && \
    apt-get -y install curl git build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN pip install --upgrade pip

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain ${RUST_VERSION}
RUN rustup install stable

WORKDIR               /app
COPY pyproject.toml   /app/pyproject.toml
COPY poetry.lock      /app/poetry.lock

RUN poetry config cache-dir /app/.cache
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-interaction --no-root
RUN poetry config --list

COPY summaru_index.py /app/summaru_index.py
COPY bot.py           /app/bot.py
COPY config.py        /app/config.py
COPY components       /app/components
COPY tests            /app/tests
COPY block_kit.py     /app/block_kit.py
COPY help.py          /app/help.py
COPY summaru_gpt.py   /app/summaru_gpt.py

ENTRYPOINT ["poetry", "run"]
