local cjson = require "cjson"
local http = require "resty.http"

cjson.encode_empty_table_as_object(false)

local experiment_access = {
    ["kushit@techdwarfs.com"] = {
        experiments = {"381747126836502912", "663922813976858922"},
        permissions = {"read", "write"}
    }
}

local function get_allowed_experiments()
    local email = (ngx.ctx.user_email or ""):lower()
    local uid = (ngx.ctx.user_id or ""):lower()
    local entry = experiment_access[email] or experiment_access[uid]
    if not entry then return {} end
    return entry.experiments or {}
end

local function array_to_set(arr)
    local s = {}
    for _, v in ipairs(arr or {}) do s[tostring(v)] = true end
    return s
end

local function backend_search()
    local httpc = http.new()
    local uri = ngx.var.request_uri
    local path = uri:gsub("^/mlflow/", "/")
    local backend_url = "http://mlflow_backend" .. path
    local res, err = httpc:request_uri(backend_url, {
        method = ngx.req.get_method(),
        headers = { ["Content-Type"] = "application/json" },
        body = ngx.arg[1]
    })
    if not res then
        ngx.status = 502
        ngx.say(cjson.encode({ error = "bad_gateway", message = err }))
        return nil
    end
    return res
end

local res = backend_search()
if not res then return end

local ok, data = pcall(cjson.decode, res.body or "")
if not ok or type(data) ~= "table" then
    ngx.status = res.status
    ngx.say(res.body or "")
    return
end

if type(data.experiments) ~= "table" then data.experiments = {} end
local allowed = array_to_set(get_allowed_experiments())
local filtered = {}
for _, exp in ipairs(data.experiments) do
    local id = tostring(exp.experiment_id)
    if allowed[id] then table.insert(filtered, exp) end
end

local out = {
    experiments = filtered,
    next_page_token = data.next_page_token ~= nil and data.next_page_token or cjson.null
}

ngx.status = 200
ngx.header.content_type = "application/json"
ngx.say(cjson.encode(out))

