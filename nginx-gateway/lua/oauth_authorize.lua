local cjson = require "cjson"
local http = require "resty.http"

local tenant_id = os.getenv("ENTRA_TENANT_ID")
local client_id = os.getenv("ENTRA_CLIENT_ID")
local redirect_uri = os.getenv("OAUTH_REDIRECT_URI")
local audience = os.getenv("ENTRA_AUDIENCE")

local scope = "openid profile email"

local auth_url = string.format(
    "https://login.microsoftonline.com/%s/oauth2/v2.0/authorize?client_id=%s&response_type=code&redirect_uri=%s&scope=%s&response_mode=query",
    tenant_id,
    client_id,
    ngx.escape_uri(redirect_uri),
    ngx.escape_uri(scope)
)

if ngx.var.arg_redirect == "1" then
    return ngx.redirect(auth_url, 302)
end

ngx.header.content_type = "application/json"
ngx.say(cjson.encode({ authorization_url = auth_url }))
