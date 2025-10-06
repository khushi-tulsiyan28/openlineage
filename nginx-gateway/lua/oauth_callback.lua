local cjson = require "cjson"
local http = require "resty.http"

local tenant_id = os.getenv("ENTRA_TENANT_ID")
local client_id = os.getenv("ENTRA_CLIENT_ID")
local client_secret = os.getenv("ENTRA_CLIENT_SECRET")
local redirect_uri = os.getenv("OAUTH_REDIRECT_URI")
local mlflow_url = os.getenv("MLFLOW_PUBLIC_URL")

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
        ngx.escape_uri(client_secret),
        ngx.escape_uri(code),
        redirect_uri
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
    local safe_body = res.body or "{}"
    ngx.say([[ 
        <html>
            <head><title>Authorization Failed</title></head>
            <body style="font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 720px; margin: 40px auto;">
                <h2>⚠️ Authorization failed</h2>
                <p>Microsoft returned an error. Details below will help troubleshoot.</p>
                <pre style="background:#f5f5f5; padding:12px; border-radius:8px; white-space:pre-wrap;">]] .. safe_body .. [[</pre>
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

local cookie_attrs = {
    "Path=/",
    "HttpOnly",
    "SameSite=Lax"
}
ngx.header["Set-Cookie"] = string.format("access_token=%s; %s", token_data.access_token, table.concat(cookie_attrs, "; "))

local function decode_jwt_email(token)
    local parts = {}
    for part in string.gmatch(token or "", "[^%.]+") do table.insert(parts, part) end
    if #parts ~= 3 then return nil end
    local payload = parts[2]
    local pad = 4 - (#payload % 4)
    if pad ~= 4 then payload = payload .. string.rep("=", pad) end
    local ok, json_payload = pcall(ngx.decode_base64, payload)
    if not ok or not json_payload then return nil end
    local ok2, obj = pcall(cjson.decode, json_payload)
    if not ok2 or type(obj) ~= "table" then return nil end
    return (obj.email or obj.preferred_username or obj.upn)
end

local user_email = (decode_jwt_email(token_data.access_token) or ""):lower()

-- Debug logging
ngx.log(ngx.ERR, "DEBUG: user_email = ", user_email)

local experiment_access = {
    ["kushit@techdwarfs.com"] = { experiments = {"1", "2"} }
}

local function get_allowed_ids()
    local entry = experiment_access[user_email]
    if not entry then return {} end
    return entry.experiments or {}
end

local function fetch_all_experiments()
    local httpc2 = http.new()
    local url = "http://openlineage-mlflow-1:5000/api/2.0/mlflow/experiments/search?max_results=1000"
    local r, e = httpc2:request_uri(url, { method = "GET" })
    if not r then return nil, e end
    local ok, data = pcall(cjson.decode, r.body or "")
    if not ok or type(data) ~= "table" then return {experiments={}}, nil end
    if type(data.experiments) ~= "table" then data.experiments = {} end
    return data, nil
end

local function to_set(arr)
    local s = {}
    for _, v in ipairs(arr or {}) do s[tostring(v)] = true end
    return s
end

local all, ferr = fetch_all_experiments()
if ferr then
    ngx.status = 200
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({ experiments = {}, next_page_token = cjson.null }))
    return
end

local allowed = to_set(get_allowed_ids())
local filtered = {}
for _, exp in ipairs(all.experiments or {}) do
    if allowed[tostring(exp.experiment_id)] then
        table.insert(filtered, exp)
    end
end

ngx.status = 200
ngx.header.content_type = "application/json"
ngx.say(cjson.encode({ experiments = filtered, next_page_token = cjson.null }))
