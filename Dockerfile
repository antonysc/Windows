FROM golang:1.27.1-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY adapters/go ./adapters/go
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/windows-provider-check ./adapters/go/cmd/windows-provider-check

FROM alpine:3.22 AS certificates
RUN apk add --no-cache ca-certificates

FROM scratch
COPY --from=certificates /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=build /out/windows-provider-check /windows-provider-check
USER 65532:65532
ENTRYPOINT ["/windows-provider-check"]

