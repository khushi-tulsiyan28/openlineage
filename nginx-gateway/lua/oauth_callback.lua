local cjson = require "cjson"
local http = require "resty.http"

local tenant_id = os.getenv("ENTRA_TENANT_ID") or "5f892d7b-6294-4f75-aa09-20fb450b9bf2"
local client_id = os.getenv("ENTRA_CLIENT_ID") or "1c3c2a07-a8a5-4358-883f-9030f73125e3"
local client_secret = os.getenv("ENTRA_CLIENT_SECRET") or "821236ef-db35-4c48-b5e9-9161190eef72"
local redirect_uri = os.getenv("OAUTH_REDIRECT_URI") or "http://localhost:8081/oauth/callback"
local mlflow_url = os.getenv("MLFLOW_PUBLIC_URL") or "http://localhost:5000"

local code = ngx.var.arg_code
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

if res.status ~= 200 then
    ngx.log(ngx.ERR, "Token exchange failed with status: ", res.status, " body: ", res.body)
    ngx.status = 400
    ngx.header.content_type = "text/html"
    ngx.say([[
        <html>
            <head><title>Authorization Failed</title></head>
            <body style="font-family: -apple-system, Segoe UI, Roboto, sans-serif;">
                <h2>⚠️ Authorization failed</h2>
                <p>Please check your credentials and try again.</p>
            </body>
        </html>
    ]])
    return
end

local token_data = cjson.decode(res.body)
if not token_data.access_token then
    ngx.log(ngx.ERR, "No access token in response: ", res.body)
    ngx.status = 400
    ngx.header.content_type = "text/html"
    ngx.say([[
        <html>
            <head><title>Authorization Failed</title></head>
            <body style="font-family: -apple-system, Segoe UI, Roboto, sans-serif;">
                <h2>⚠️ Authorization failed</h2>
                <p>No access token received from Microsoft.</p>
            </body>
        </html>
    ]])
    return
end

ngx.redirect(mlflow_url, 302)
