local cjson = require "cjson"
local http = require "resty.http"
local policy = require "access_policy"

cjson.encode_empty_table_as_object(false)

local function get_token()
    local auth = ngx.var.http_authorization or ""
    local t = auth:match("Bearer%s+(.+)")
    if t and #t > 0 then return t end
    local cookie = ngx.var.http_cookie or ""
    return cookie:match("access_token=([^;]+)")
end

local function decode_claims(token)
    if not token then return {} end
    local parts = {}
    for p in token:gmatch("[^%.]+") do table.insert(parts, p) end
    if #parts ~= 3 then return {} end
    local payload = parts[2]
    local pad = 4 - (#payload % 4)
    if pad ~= 4 then payload = payload .. string.rep("=", pad) end
    local ok, b = pcall(ngx.decode_base64, payload)
    if not ok or not b then return {} end
    local ok2, obj = pcall(cjson.decode, b)
    if not ok2 or type(obj) ~= "table" then return {} end
    return obj
end

local function allowed_ids(email)
    return policy.get_allowed_experiments(email)
end

local function fetch_all_experiments()
    local httpc = http.new()
    local url = "http://mlflow_backend/api/2.0/mlflow/experiments/search?max_results=1000"
    local res, err = httpc:request_uri(url, { method = "GET" })
    if not res then return nil, err end
    local ok, data = pcall(cjson.decode, res.body or "")
    if not ok or type(data) ~= "table" then return { experiments = {} }, nil end
    if type(data.experiments) ~= "table" then data.experiments = {} end
    return data, nil
end

local function to_set(arr)
    local s = {}
    for _, v in ipairs(arr or {}) do s[tostring(v)] = true end
    return s
end

local token = get_token()
if not token then
    ngx.status = 401
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({ error = "unauthorized", message = "Access token required" }))
    return
end

local claims = decode_claims(token)
local email = (claims.email or claims.preferred_username or claims.upn or ""):lower()

local allowed = to_set(allowed_ids(email))
local all, ferr = fetch_all_experiments()
local filtered = {}
if not ferr then
    for _, exp in ipairs(all.experiments or {}) do
        if allowed[tostring(exp.experiment_id)] then table.insert(filtered, exp) end
    end
end

ngx.status = 200
ngx.header.content_type = "application/json"
ngx.say(cjson.encode({
    user = {
        sub = claims.sub,
        email = email,
        name = claims.name,
        tid = claims.tid,
        aud = claims.aud
    },
    experiments = filtered,
    next_page_token = cjson.null
}))


