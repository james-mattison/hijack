FROM alpine:latest

COPY hijack.py /bin/hijack
RUN apk add python3

RUN chmod +x /bin/hijack
RUN ln -s /bin/hijack /bin/hj

ENTRYPOINT ["/bin/hijack"]
