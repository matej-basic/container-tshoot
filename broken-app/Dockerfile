FROM python:3.9

RUN mkdir /app
COPY app.py /app/ap.py

RUN echo '#!/bin/sh' > /start.sh \
    && echo 'echo "Starting app"' >> /start.sh \
    && echo 'python3 /app/app.py' >> /start.sh \
    && chmod +x /start.sh

CMD ["/start.sh"]
HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD pidof python3 || exit 1