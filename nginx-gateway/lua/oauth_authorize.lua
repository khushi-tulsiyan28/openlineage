local cjson = require "cjson"
local http = require "resty.http"

local tenant_id = os.getenv("ENTRA_TENANT_ID")
local client_id = os.getenv("ENTRA_CLIENT_ID")
local redirect_uri = os.getenv("OAUTH_REDIRECT_URI") or "http://localhost:8081/oauth/callback"

local auth_url = string.format(
    "https://login.microsoftonline.com/%s/oauth2/v2.0/authorize?client_id=%s&response_type=code&redirect_uri=%s&scope=openid profile email https://graph.microsoft.com/User.Read&response_mode=query",
    tenant_id,
    client_id,
    ngx.escape_uri(redirect_uri)
)

ngx.header.content_type = "application/json"
ngx.say(cjson.encode({
    authorization_url = auth_url
}))
