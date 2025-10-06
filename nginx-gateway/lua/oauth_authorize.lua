local cjson = require "cjson"
local http = require "resty.http"

local tenant_id = os.getenv("ENTRA_TENANT_ID")
local client_id = os.getenv("ENTRA_CLIENT_ID")
local redirect_uri = os.getenv("OAUTH_REDIRECT_URI")
local audience = os.getenv("ENTRA_AUDIENCE")

local fallback_audience = client_id and (#client_id > 0) and ("api://" .. client_id) or nil
local effective_audience = (audience and #audience > 0) and audience or fallback_audience
local api_scope = effective_audience and (effective_audience .. "/access_as_user") or nil
local scope = api_scope and ("openid profile email " .. api_scope) or "openid profile email"

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
