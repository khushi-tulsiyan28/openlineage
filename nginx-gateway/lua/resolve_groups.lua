local cjson = require "cjson"
local http = require "resty.http"

local M = {}

local cache = ngx.shared.jwt_cache

local function table_is_empty(t)
    return type(t) ~= "table" or next(t) == nil
end

local function cache_key(sub_or_email)
    return "groups:" .. (sub_or_email or "unknown")
end

local function get_app_token(tenant_id, client_id, client_secret)
    if not (tenant_id and client_id and client_secret) then return nil, "missing_app_creds" end
    local httpc = http.new()
    local token_url = string.format("https://login.microsoftonline.com/%s/oauth2/v2.0/token", tenant_id)
    local res, err = httpc:request_uri(token_url, {
        method = "POST",
        headers = { ["Content-Type"] = "application/x-www-form-urlencoded" },
        body = string.format(
            "client_id=%s&client_secret=%s&grant_type=client_credentials&scope=%s",
            ngx.escape_uri(client_id), ngx.escape_uri(client_secret), ngx.escape_uri("https://graph.microsoft.com/.default")
        )
    })
    if not res then return nil, err end
    if res.status ~= 200 then return nil, "token_status_" .. (res.status or 0) end
    local ok, data = pcall(cjson.decode, res.body or "")
    if not ok or type(data) ~= "table" then return nil, "token_parse_failed" end
    return data.access_token, nil
end

local function graph_get_member_objects(app_token, user_id_or_upn)
    local httpc = http.new()
    local url = string.format("https://graph.microsoft.com/v1.0/users/%s/getMemberObjects", ngx.escape_uri(user_id_or_upn))
    local res, err = httpc:request_uri(url, {
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
            ["Authorization"] = "Bearer " .. app_token
        },
        body = cjson.encode({ securityEnabledOnly = false })
    })
    if not res then return nil, err end
    if res.status ~= 200 then return nil, "graph_status_" .. (res.status or 0) end
    local ok, data = pcall(cjson.decode, res.body or "")
    if not ok or type(data) ~= "table" then return nil, "graph_parse_failed" end
    return data.value or {}, nil
end

function M.resolve_groups(claims, tenant_id, client_id, client_secret)
    claims = claims or {}
    if type(claims.groups) == "table" and not table_is_empty(claims.groups) then
        return claims.groups
    end

    local subject_key = claims.sub or claims.oid or claims.email or claims.upn or claims.preferred_username or ""
    local ck = cache_key(subject_key)
    local cached = cache and cache:get(ck)
    if cached then
        local ok, arr = pcall(cjson.decode, cached)
        if ok and type(arr) == "table" then return arr end
    end

    local app_token, terr = get_app_token(tenant_id, client_id, client_secret)
    if not app_token then
        ngx.log(ngx.ERR, "resolve_groups: app token error: ", terr)
        return {}
    end

    local user_ref = claims.oid or claims.sub or claims.upn or claims.preferred_username or claims.email
    if not user_ref then return {} end
    local groups, gerr = graph_get_member_objects(app_token, user_ref)
    if gerr then
        ngx.log(ngx.ERR, "resolve_groups: graph error: ", gerr)
        return {}
    end

    if cache then
        cache:set(ck, cjson.encode(groups), 900)
    end
    return groups
end

return M


