FROM oven/bun:1

ENV BUN_INSTALL=/usr/local
RUN bun add -g nuekit@2.0.0-beta.2
COPY fswatch.poll.js /usr/local/install/global/node_modules/nuekit/src/tools/fswatch.js

WORKDIR /app/frontend
EXPOSE 4000
CMD ["nue", "dev", "-p", "4000"]
