local cjson = require "cjson"
local http = require "resty.http"
local resolver = require "resolve_groups"
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

local function allowed_ids_union(email, groups)
    return policy.get_allowed_experiments_union(email, groups)
end

local function fetch_all_experiments()
    local httpc = http.new()
    local url = "http://openlineage-mlflow-1:5000/api/2.0/mlflow/experiments/search?max_results=1000"
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
local tenant_id = os.getenv("ENTRA_TENANT_ID")
local client_id = os.getenv("ENTRA_CLIENT_ID")
local client_secret = os.getenv("ENTRA_CLIENT_SECRET")
ngx.log(ngx.ERR, "DEBUG oauth_me: email=", email, ", aud=", tostring(claims.aud), ", tid=", tostring(claims.tid))
ngx.log(ngx.ERR, "DEBUG oauth_me: env tenant set=", tostring(tenant_id ~= nil and #tenant_id > 0), ", client_id set=", tostring(client_id ~= nil and #client_id > 0), ", client_secret set=", tostring(client_secret ~= nil and #client_secret > 0))

local groups = resolver.resolve_groups(claims, tenant_id, client_id, client_secret)
do
    local norm = {}
    for _, gid in ipairs(groups or {}) do table.insert(norm, tostring(gid)) end
    groups = norm
end
-- Optional hard gate via header only: X-Required-Group-Id can be a single id or comma-separated list
local header_required = ngx.var.http_x_required_group_id
if not header_required or #header_required == 0 then
    ngx.status = 401
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({ error = "unauthorized", message = "Missing X-Required-Group-Id header" }))
    return
end

local required_set = {}
for token in tostring(header_required):gmatch("[^,]+") do
    local trimmed = token:match("^%s*(.-)%s*$")
    if trimmed and #trimmed > 0 then required_set[string.lower(trimmed)] = true end
end
local user_set = {}
for _, gid in ipairs(groups or {}) do user_set[string.lower(gid)] = true end
local ok_member = false
for req in pairs(required_set) do if user_set[req] then ok_member = true; break end end
if not ok_member then
    ngx.status = 401
    ngx.header.content_type = "application/json"
    ngx.say(cjson.encode({ error = "unauthorized", message = "User not in required group(s)", required_groups = required_set }))
    return
end
ngx.log(ngx.ERR, "DEBUG oauth_me: resolved_groups_count=", tostring(#(groups or {})), ", token_groups_present=", tostring(type(claims.groups) == "table" and #(claims.groups) > 0))

local allowed_user = policy.get_allowed_experiments(email)
local allowed_ids = allowed_ids_union(email, groups)
ngx.log(ngx.ERR, "DEBUG policy allowed for ", email, ": ", cjson.encode(allowed_ids))
local allowed = to_set(allowed_ids)

local group_experiments = {}
local pol = policy.load_policy()
if type(groups) == "table" then
    for _, gid in ipairs(groups) do
        local ge = ((pol.groups or {})[string.lower(tostring(gid))] or {}).experiments or {}
        group_experiments[gid] = ge
    end
end
local all, ferr = fetch_all_experiments()
local filtered = {}
local brief = {}
if not ferr then
    for _, exp in ipairs(all.experiments or {}) do
        local eid = tostring(exp.experiment_id)
        if allowed[eid] then
            table.insert(filtered, exp)
            table.insert(brief, { id = eid, name = exp.name })
        end
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
        aud = claims.aud,
        groups = claims.groups
    },
    experiments = filtered,
    allowed_ids = allowed_ids,
    allowed_experiments_brief = brief,
    resolved_groups = groups,
    policy = {
        user = allowed_user,
        groups = group_experiments,
        union = allowed_ids,
        policy_loaded_users = pol and pol.users or {},
        policy_loaded_groups = pol and pol.groups or {}
    },
    next_page_token = cjson.null
}))


