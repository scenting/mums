# Base image
FROM django:1.10

# Install apt dependencies
RUN \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
        netcat \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
RUN \
    sed -i 's/\r//' /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENV HOME /home/user
RUN useradd --create-home --home-dir $HOME user && \
    chown -R user:user $HOME

WORKDIR /app
USER user

ENTRYPOINT ["/entrypoint.sh"]
