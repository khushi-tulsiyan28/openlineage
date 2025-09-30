local cjson = require "cjson"
local http = require "resty.http"
local policy = require "access_policy"

cjson.encode_empty_table_as_object(false)

local function allowed_set()
    local set = {}
    local email = (ngx.ctx.user_email or ""):lower()
    for _, id in ipairs(policy.get_allowed_experiments(email)) do
        set[tostring(id)] = true
    end
    return set
end

local function backend_get_run(run_id)
    local httpc = http.new()
    local url = "http://172.18.0.9:5000/api/2.0/mlflow/runs/get?run_id=" .. ngx.escape_uri(run_id)
    local res, err = httpc:request_uri(url, { method = "GET" })
    if not res then return nil, err end
    local ok, data = pcall(cjson.decode, res.body or "")
    if not ok or type(data) ~= "table" then return nil, "decode_error" end
    return data, nil
end

local function deny()
    ngx.status = 403
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({ error = "forbidden", message = "You don't have access to artifacts of this run" }))
end

local args = ngx.req.get_uri_args()
local run_id = args["run_id"]
if not run_id then
    ngx.status = 400
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({ error = "bad_request", message = "run_id is required" }))
    return
end

local run_data, err = backend_get_run(run_id)
if not run_data or not run_data.run then
    deny(); return
end

local exp_id = tostring(run_data.run.info and run_data.run.info.experiment_id)
if not allowed_set()[exp_id] then
    deny(); return
end

local httpc = http.new()
local path = ngx.var.request_uri:gsub("^/mlflow/", "/")
local url = "http://172.18.0.9:5000" .. path
local res2, err2 = httpc:request_uri(url, { method = "GET" })
if not res2 then
    ngx.status = 502
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({ error = "bad_gateway", message = err2 }))
    return
end

ngx.status = res2.status
for k,v in pairs(res2.headers or {}) do
    ngx.header[k] = v
end
ngx.print(res2.body)


