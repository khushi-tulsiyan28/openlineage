local cjson = require "cjson"
local http = require "resty.http"
local policy = require "access_policy"

cjson.encode_empty_table_as_object(false)

local function get_access_token()
    local auth = ngx.var.http_authorization or ""
    local token = auth:match("Bearer%s+(.+)")
    if token and #token > 0 then return token end
    local cookie = ngx.var.http_cookie or ""
    local from_cookie = cookie:match("access_token=([^;]+)")
    return from_cookie
end

local function decode_user_email(token)
    if not token then return nil end
    local parts = {}
    for p in token:gmatch("[^%.]+") do table.insert(parts, p) end
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

local function get_allowed_ids(email)
    return policy.get_allowed_experiments(email)
end

local function to_set(arr)
    local s = {}
    for _, v in ipairs(arr or {}) do s[tostring(v)] = true end
    return s
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

local token = get_access_token()
if not token then
    ngx.status = 401
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({ error = "unauthorized", message = "Access token required" }))
    return
end

local email = decode_user_email(token)
local allowed = to_set(get_allowed_ids(email))

local all, ferr = fetch_all_experiments()
if ferr then
    ngx.status = 502
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({ error = "bad_gateway", message = ferr }))
    return
end

local filtered = {}
for _, exp in ipairs(all.experiments or {}) do
    if allowed[tostring(exp.experiment_id)] then table.insert(filtered, exp) end
end

ngx.status = 200
ngx.header.content_type = "application/json"
ngx.say(cjson.encode({ experiments = filtered, next_page_token = cjson.null }))


