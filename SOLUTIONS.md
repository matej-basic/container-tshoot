# Solutions

These are the fixes for the scenarios in [README.md](README.md). Each section gives the change that makes the scenario work and the reason the original fails.

## broken-app

`broken-app/Containerfile` copies the script to a different name than the one the start script runs:

```dockerfile
COPY app.py /app/ap.py
```

The `RUN` step below it writes `/start.sh`, which runs `python3 /app/app.py`. That file is not in the image, so Python stops with `No such file or directory`. Copy the script under the name the start script expects:

```dockerfile
COPY app.py /app/app.py
```

After a rebuild the container prints

```
Starting app
Hello from the fixed container!
```

and exits with code 0. Exiting is correct here: the script prints one line and ends.

## webapp-port

The first fault is the type of `PORT`. `os.getenv` always returns a string, so `PORT` is `"8080"`, and `socket.bind` wants the port number as an integer. Convert it in `webapp-port/app.py`:

```python
PORT = int(os.getenv("PORT", "8080"))
```

The second fault is the listen address. The server binds to `127.0.0.1`, which inside a container is the container's own loopback interface. `-p 8080:8080` forwards host traffic to the container's network interface, where nothing listens, so the host connection is reset. A request from inside the container works, which is how you can tell the two apart. Listen on all interfaces:

```python
httpd = socketserver.TCPServer(("0.0.0.0", PORT), handler)
```

With both changes, `curl http://localhost:8080/` returns a directory listing of `/app`, the working directory that `SimpleHTTPRequestHandler` serves.

The empty log has a separate cause. Python buffers standard output when it is not writing to a terminal, so the `Serving on port` line stays in the buffer. The request log lines go to standard error, which is not buffered, so those do show up once requests arrive. To see the startup line, run the container with `-t` or pass `-e PYTHONUNBUFFERED=1`.

## multicontainer-app

`multicontainer-app/podman-compose.yml` gives the web service `DB_HOST=localhost`. Every service runs in its own container with its own network namespace, so `localhost` in the web container is the web container, and nothing listens on port 3306 there. Compose puts both services on a shared network where each service name resolves to its container. Point the app at the database service, `db`:

```yaml
    environment:
      - DB_HOST=db
```

Run `down` and then `up -d` again so the web container starts with the new value. The page then shows `Connected to MySQL!` and lists `information_schema`, `mysql`, `performance_schema` and `sys`.

On a fresh start the page can still show a connection error for the first 15 to 20 seconds. `depends_on` only makes Compose start `db` before `web`; it does not wait until MySQL accepts connections. Reload once MySQL is ready.

## WordPress example

The top-level `podman-compose.yml` has nothing to fix. Its WordPress service reaches MySQL at `db:3306`, the database service name on the shared `wordpress_net` network, which is the same idea as the `multicontainer-app` fix.
