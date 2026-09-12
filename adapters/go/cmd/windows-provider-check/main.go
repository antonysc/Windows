// Command windows-provider-check performs one bounded read-only connectivity
// request for either Azure or Microsoft Store. It never prints credentials or
// provider response bodies.
package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
)

var (
	loginBaseURL = "https://login.microsoftonline.com"
	azureBaseURL = "https://management.azure.com"
	storeBaseURL = "https://api.store.microsoft.com"
)

type tokenResponse struct {
	AccessToken string `json:"access_token"`
}

func required(environment, name string) (string, error) {
	value := strings.TrimSpace(os.Getenv(environment))
	if value == "" {
		return "", fmt.Errorf("missing protected variable %s", name)
	}
	return value, nil
}

func token(ctx context.Context, client *http.Client, tenant, clientID, clientSecret, scope string) (string, error) {
	form := url.Values{
		"client_id":     {clientID},
		"client_secret": {clientSecret},
		"grant_type":    {"client_credentials"},
		"scope":         {scope},
	}
	endpoint := strings.TrimRight(loginBaseURL, "/") + "/" + url.PathEscape(tenant) + "/oauth2/v2.0/token"
	request, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, strings.NewReader(form.Encode()))
	if err != nil {
		return "", err
	}
	request.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	request.Header.Set("User-Agent", "windows-provider-check/1")
	response, err := client.Do(request)
	if err != nil {
		return "", fmt.Errorf("Entra token endpoint unreachable: %w", err)
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		_, _ = io.Copy(io.Discard, io.LimitReader(response.Body, 4096))
		return "", fmt.Errorf("Entra token endpoint returned HTTP %d", response.StatusCode)
	}
	var result tokenResponse
	if err := json.NewDecoder(io.LimitReader(response.Body, 1<<20)).Decode(&result); err != nil {
		return "", errors.New("Entra token response was invalid")
	}
	if strings.TrimSpace(result.AccessToken) == "" {
		return "", errors.New("Entra token response contained no access token")
	}
	return result.AccessToken, nil
}

func boundedGet(ctx context.Context, client *http.Client, endpoint, accessToken, sellerID string) error {
	request, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return err
	}
	request.Header.Set("Accept", "application/json")
	request.Header.Set("Authorization", "Bearer "+accessToken)
	request.Header.Set("User-Agent", "windows-provider-check/1")
	if sellerID != "" {
		request.Header.Set("X-Seller-Account-Id", sellerID)
	}
	response, err := client.Do(request)
	if err != nil {
		return fmt.Errorf("provider endpoint unreachable: %w", err)
	}
	defer response.Body.Close()
	_, _ = io.Copy(io.Discard, io.LimitReader(response.Body, 4096))
	if response.StatusCode != http.StatusOK {
		return fmt.Errorf("provider endpoint returned HTTP %d", response.StatusCode)
	}
	return nil
}

func checkAzure(ctx context.Context, client *http.Client) error {
	tenant, err := required("AZURE_DEV_TENANT_ID", "tenant_id")
	if err != nil { return err }
	clientID, err := required("AZURE_DEV_CLIENT_ID", "client_id")
	if err != nil { return err }
	secret, err := required("AZURE_DEV_CLIENT_SECRET", "client_secret")
	if err != nil { return err }
	subscription, err := required("AZURE_DEV_SUBSCRIPTION_ID", "subscription_id")
	if err != nil { return err }
	accessToken, err := token(ctx, client, tenant, clientID, secret, "https://management.azure.com/.default")
	if err != nil { return err }
	endpoint := strings.TrimRight(azureBaseURL, "/") + "/subscriptions/" + url.PathEscape(subscription) + "?api-version=2022-12-01"
	return boundedGet(ctx, client, endpoint, accessToken, "")
}

func checkStore(ctx context.Context, client *http.Client) error {
	tenant, err := required("MS_STORE_PROD_TENANT_ID", "tenant_id")
	if err != nil { return err }
	clientID, err := required("MS_STORE_PROD_CLIENT_ID", "client_id")
	if err != nil { return err }
	secret, err := required("MS_STORE_PROD_CLIENT_SECRET", "client_secret")
	if err != nil { return err }
	seller, err := required("MS_STORE_PROD_SELLER_ID", "seller_id")
	if err != nil { return err }
	product, err := required("MS_STORE_PROD_PRODUCT_ID", "product_id")
	if err != nil { return err }
	accessToken, err := token(ctx, client, tenant, clientID, secret, "https://api.store.microsoft.com/.default")
	if err != nil { return err }
	endpoint := strings.TrimRight(storeBaseURL, "/") + "/submission/v1/product/" + url.PathEscape(product) + "/metadata?languages=en&includelanguagelist=false"
	return boundedGet(ctx, client, endpoint, accessToken, seller)
}

func run(pod string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 12*time.Second)
	defer cancel()
	client := &http.Client{Timeout: 10 * time.Second}
	switch pod {
	case "azure":
		return checkAzure(ctx, client)
	case "microsoft-store":
		return checkStore(ctx, client)
	default:
		return errors.New("pod must be azure or microsoft-store")
	}
}

func main() {
	pod := flag.String("pod", "", "azure or microsoft-store")
	flag.Parse()
	if err := run(*pod); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Printf("%s read-only check verified\n", *pod)
}

