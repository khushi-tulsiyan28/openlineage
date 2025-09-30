local cjson = require "cjson"
local http = require "resty.http"

cjson.encode_empty_table_as_object(false)

local experiment_access = {
    ["kushit@techdwarfs.com"] = {
        experiments = {"381747126836502912", "663922813976858922"}
    }
}

local function get_allowed()
    local email = (ngx.ctx.user_email or ""):lower()
    local uid = (ngx.ctx.user_id or ""):lower()
    local entry = experiment_access[email] or experiment_access[uid]
    if not entry then return {} end
    return entry.experiments or {}
end

local function set_of(arr)
    local s = {}
    for _, v in ipairs(arr or {}) do s[tostring(v)] = true end
    return s
end

local function proxy_to_backend()
    local httpc = http.new()
    local path = ngx.var.request_uri:gsub("^/mlflow/", "/")
    local url = "http://172.18.0.9:5000" .. path
    local res, err = httpc:request_uri(url, { method = "GET" })
    if not res then
        ngx.status = 502
        ngx.say(cjson.encode({ error = "bad_gateway", message = err }))
        return nil
    end
    return res
end

local res = proxy_to_backend()
if not res then return end

local ok, data = pcall(cjson.decode, res.body or "")
if not ok or type(data) ~= "table" then
    ngx.status = res.status
    ngx.say(res.body or "")
    return
end

if type(data.experiments) == "table" then
    local allowed = set_of(get_allowed())
    local filtered = {}
    for _, exp in ipairs(data.experiments) do
        if allowed[tostring(exp.experiment_id)] then
            table.insert(filtered, exp)
        end
    end
    data.experiments = filtered
    if data.next_page_token == nil then data.next_page_token = cjson.null end
end

ngx.status = 200
ngx.header.content_type = "application/json"
ngx.say(cjson.encode(data))


