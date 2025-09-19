-- OAuth Authorization Endpoint
local cjson = require "cjson"
local http = require "resty.http"

-- Get environment variables
local tenant_id = os.getenv("ENTRA_TENANT_ID") or "5f892d7b-6294-4f75-aa09-20fb450b9bf2"
local client_id = os.getenv("ENTRA_CLIENT_ID") or "1c3c2a07-a8a5-4358-883f-9030f73125e3"
local redirect_uri = os.getenv("OAUTH_REDIRECT_URI") or "http://localhost:8081/oauth/callback"

-- Build authorization URL
local auth_url = string.format(
    "https://login.microsoftonline.com/%s/oauth2/v2.0/authorize?client_id=%s&response_type=code&redirect_uri=%s&scope=openid profile email https://graph.microsoft.com/User.Read&response_mode=query",
    tenant_id,
    client_id,
    ngx.escape_uri(redirect_uri)
)

-- Return JSON response
ngx.header.content_type = "application/json"
ngx.say(cjson.encode({
    authorization_url = auth_url
}))
