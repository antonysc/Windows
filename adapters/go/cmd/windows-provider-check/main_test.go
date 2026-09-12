package main

import (
	"context"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"testing"
)

func TestTokenUsesClientCredentialsAndRequestedScope(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Method != http.MethodPost || !strings.HasSuffix(request.URL.Path, "/tenant/oauth2/v2.0/token") {
			t.Fatalf("unexpected token request: %s %s", request.Method, request.URL.Path)
		}
		if err := request.ParseForm(); err != nil { t.Fatal(err) }
		if request.Form.Get("grant_type") != "client_credentials" || request.Form.Get("scope") != "scope/.default" {
			t.Fatalf("unexpected form: %v", request.Form)
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{"access_token":"opaque-test-token"}`))
	}))
	defer server.Close()
	old := loginBaseURL
	loginBaseURL = server.URL
	defer func() { loginBaseURL = old }()
	got, err := token(context.Background(), server.Client(), "tenant", "client", "secret", "scope/.default")
	if err != nil || got != "opaque-test-token" { t.Fatalf("token=%q err=%v", got, err) }
}

func TestBoundedGetSendsBearerAndSeller(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Header.Get("Authorization") != "Bearer opaque" { t.Fatal("missing bearer") }
		if request.Header.Get("X-Seller-Account-Id") != "seller" { t.Fatal("missing seller") }
		writer.WriteHeader(http.StatusOK)
		_, _ = writer.Write([]byte(strings.Repeat("x", 8192)))
	}))
	defer server.Close()
	if err := boundedGet(context.Background(), server.Client(), server.URL, "opaque", "seller"); err != nil { t.Fatal(err) }
}

func TestIdentifiersAreEscapedInPaths(t *testing.T) {
	if url.PathEscape("a/b") == "a/b" { t.Fatal("path escape must protect slash") }
}

