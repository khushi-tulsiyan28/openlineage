local cjson = require "cjson"
local http = require "resty.http"
local policy = require "access_policy"

cjson.encode_empty_table_as_object(false)

local function get_email()
    return (ngx.ctx.user_email or ""):lower()
end

local function allowed_set()
    local set = {}
    for _, id in ipairs(policy.get_allowed_experiments(get_email())) do
        set[tostring(id)] = true
    end
    return set
end

local function proxy()
    local httpc = http.new()
    local path = ngx.var.request_uri:gsub("^/mlflow/", "/")
    local url = "http://172.18.0.9:5000" .. path
    ngx.req.read_body()
    local res, err = httpc:request_uri(url, {
        method = ngx.req.get_method(),
        headers = { ["Content-Type"] = ngx.req.get_headers()["Content-Type"] or "application/json" },
        body = ngx.req.get_body_data()
    })
    if not res then
        ngx.status = 502
        ngx.say(cjson.encode({ error = "bad_gateway", message = err }))
        return nil
    end
    return res
end

local res = proxy()
if not res then return end

local ok, data = pcall(cjson.decode, res.body or "")
if not ok or type(data) ~= "table" then
    ngx.status = res.status
    ngx.say(res.body or "")
    return
end

if type(data.runs) == "table" then
    local allow = allowed_set()
    local filtered = {}
    for _, run in ipairs(data.runs) do
        local exp_id = tostring((run.data and run.data.experiment_id) or run.experiment_id)
        if allow[exp_id] then table.insert(filtered, run) end
    end
    data.runs = filtered
end

ngx.status = 200
ngx.header.content_type = "application/json"
ngx.say(cjson.encode(data))


