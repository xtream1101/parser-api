FROM alpine:3.5


RUN apk add --no-cache python3 ca-certificates

# Copy app over
COPY . /src/

# Install app dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r /src/requirements.txt

WORKDIR /src/

CMD ["gunicorn", "-b", "0.0.0.0:8000", "api:app"]
