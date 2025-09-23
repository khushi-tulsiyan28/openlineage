local cjson = require "cjson"
local http = require "resty.http"

local tenant_id = os.getenv("ENTRA_TENANT_ID")
local client_id = os.getenv("ENTRA_CLIENT_ID")
local client_secret = os.getenv("ENTRA_CLIENT_SECRET")
local code = ngx.var.arg_code
local redirect_uri = ngx.var.arg_redirect_uri or "http://localhost:8081/oauth/callback"

if not code then
    ngx.status = 400
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({
        error = "missing_authorization_code",
        message = "Authorization code is required"
    }))
    return
end

local httpc = http.new()
local token_url = string.format("https://login.microsoftonline.com/%s/oauth2/v2.0/token", tenant_id)

local res, err = httpc:request_uri(token_url, {
    method = "POST",
    headers = {
        ["Content-Type"] = "application/x-www-form-urlencoded"
    },
    body = string.format(
        "client_id=%s&client_secret=%s&code=%s&redirect_uri=%s&grant_type=authorization_code",
        client_id,
        client_secret,
        ngx.escape_uri(code),
        ngx.escape_uri(redirect_uri)
    )
})

if not res then
    ngx.log(ngx.ERR, "Token exchange failed: ", err)
    ngx.status = 500
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({
        error = "token_exchange_failed",
        message = "Failed to exchange authorization code for token"
    }))
    return
end

ngx.header.content_type = "application/json"
ngx.say(res.body)
