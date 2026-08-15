FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y curl gnupg ca-certificates && \
    curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
      gpg --dearmor -o /usr/share/keyrings/mongodb.gpg && \
    echo "deb [ signed-by=/usr/share/keyrings/mongodb.gpg ] \
      https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" \
      > /etc/apt/sources.list.d/mongodb-org.list && \
    apt-get update && \
    apt-get install -y mongodb-database-tools rclone && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /backup
COPY backup.sh .
RUN chmod +x backup.sh

CMD ["./backup.sh"]
