# container-tshoot

Hands-on exercises in finding and fixing broken containers. Each of the three scenario directories holds a container image or a compose project that builds but does not work. Run it, look at what goes wrong, find the cause and change the files until it works.

The fixes are in [SOLUTIONS.md](SOLUTIONS.md). Try each scenario before you open it.

## What you need

- Podman with podman-compose, or `podman compose` if it finds a compose provider. The build files are named `Containerfile` and the compose files `podman-compose.yml`, so the commands below use Podman.
- Docker with Compose v2 works too, with two differences. `docker build` looks for a file named `Dockerfile`, so pass `-f Containerfile`. Docker Compose has the same limit for the `build:` line in `multicontainer-app`, so that section shows how to build the image first. Checked with Docker 24.0.7 and Compose 2.23.3.
- Network access. The scenarios pull `python:3.9`, `python:3.11-slim`, `mysql:8` and `wordpress:latest` from Docker Hub, and pip installs Flask and the MySQL connector during one build.
- `curl` or a browser.

Docker Compose does not pick up the file name `podman-compose.yml` on its own, so every compose command here names it with `-f`.

`webapp-port`, `multicontainer-app` and the WordPress example all use port 8080 on the host. Stop one before you start the next.

## broken-app

A Python script that should print a greeting and exit.

```sh
cd broken-app
podman build -t broken-app .
podman run --rm broken-app
```

With Docker: `docker build -f Containerfile -t broken-app .`, then `docker run --rm broken-app`.

The container prints `Starting app`, then

```
python3: can't open file '/app/app.py': [Errno 2] No such file or directory
```

and exits with code 2.

Hint: the path in the error is inside the image, not on your machine. Open a shell in the image with `podman run --rm -it --entrypoint sh broken-app` and compare what is there with what `/start.sh` tries to run.

## webapp-port

A small web server built on Python's `http.server`, meant to answer on port 8080. It has two faults, and the second one shows only after the first is fixed.

```sh
cd webapp-port
podman build -t webapp-port .
podman run --rm -p 8080:8080 webapp-port
```

Then, in a second terminal:

```sh
curl http://localhost:8080/
```

With Docker, build with `docker build -f Containerfile -t webapp-port .` and use the same `run` command with `docker`.

First the container exits straight away with a traceback that ends in

```
TypeError: an integer is required (got type str)
```

Once that is fixed the container stays up and `podman ps` shows port 8080 published, but curl from the host gets

```
curl: (56) Recv failure: Connection reset by peer
```

`podman logs` shows nothing, not even the `Serving on port` line. That is Python's output buffering and not one of the two faults.

Hint: read the traceback from the bottom up. Which value has the wrong type, and where does it come from? For the second fault, send a request from inside the container:

```sh
podman exec <container> python3 -c 'import urllib.request; print(urllib.request.urlopen("http://localhost:8080/").status)'
```

If it works there and not from the host, look at which address the server listens on.

## multicontainer-app

A Flask app that lists the databases on a MySQL 8 server. MySQL runs in a second container, and both are defined in `multicontainer-app/podman-compose.yml`.

```sh
cd multicontainer-app
podman-compose -f podman-compose.yml up -d --build
curl http://localhost:8080/
```

With Docker, build the web image under the name Compose would give it, then start the project without `--build`:

```sh
cd multicontainer-app
docker build -f web/Containerfile -t multicontainer-app-web web
docker compose -f podman-compose.yml up -d
```

MySQL needs about 20 seconds to initialise on the first start. Both containers keep running, but the page says

```
Error connecting to MySQL
2003: Can't connect to MySQL server on 'localhost:3306' (111 Connection refused)
```

and it keeps saying so after MySQL is ready.

Hint: the error names the host the app tried. Ask where MySQL is running, seen from inside the web container. `podman-compose -f podman-compose.yml ps` lists the containers.

Stop it with `podman-compose -f podman-compose.yml down -v` (or `docker compose -f podman-compose.yml down -v`). The `-v` also removes the database volume.

## WordPress example

`podman-compose.yml` at the top of the repository runs WordPress with MySQL. Nothing in it is broken. It is a working two-container setup to compare with `multicontainer-app`.

```sh
podman-compose -f podman-compose.yml up -d
```

After about 15 seconds http://localhost:8080/ redirects to the WordPress installer. The container names are fixed (`wordpress_db` and `wordpress_app`), so only one copy can run at a time. Remove it with `podman-compose -f podman-compose.yml down -v`.
