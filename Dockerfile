FROM python:3

# RUN apk update && apk upgrade && apk add --no-cache zlib-dev musl-dev libc-dev gcc

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY kubesh.py .
COPY kubesh.linux.spec .
COPY library .

ENTRYPOINT [ "pyinstaller", "--clean", "kubesh.linux.spec" ]