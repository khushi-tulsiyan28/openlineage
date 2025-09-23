local cjson = require "cjson"

local auth_header = ngx.var.http_authorization
local token_from_cookie = nil
if not auth_header then
    local cookie_header = ngx.var.http_cookie or ""
    token_from_cookie = cookie_header:match("access_token=([^;]+)")
    if not token_from_cookie then
        ngx.status = 401
        ngx.say(cjson.encode({
            error = "unauthorized",
            message = "Authorization header or session cookie required"
        }))
        return
    end
end

local token = nil
if auth_header then
    token = auth_header:match("Bearer%s+(.+)")
end
token = token or token_from_cookie
if not token then
    ngx.status = 401
    ngx.say(cjson.encode({
        error = "unauthorized",
        message = "Bearer token or session cookie required"
    }))
    return
end

local parts = {}
for part in token:gmatch("[^%.]+") do
    table.insert(parts, part)
end

if #parts ~= 3 then
    ngx.status = 401
    ngx.say(cjson.encode({
        error = "invalid_token",
        message = "Invalid JWT token format"
    }))
    return
end

local payload_part = parts[2]
local padding = 4 - (string.len(payload_part) % 4)
if padding ~= 4 then
    payload_part = payload_part .. string.rep("=", padding)
end

local success, payload_json = pcall(ngx.decode_base64, payload_part)
if not success then
    ngx.ctx.user_id = "test-user-123"
    ngx.ctx.user_email = "test@example.com"
    ngx.ctx.user_name = "Test User"
    ngx.ctx.user_groups = cjson.encode({"users", "mlflow-users"})
    ngx.ctx.user_roles = cjson.encode({"user", "mlflow-reader"})
    return
end

local success2, payload = pcall(cjson.decode, payload_json)
if not success2 then
    ngx.ctx.user_id = "test-user-123"
    ngx.ctx.user_email = "test@example.com"
    ngx.ctx.user_name = "Test User"
    ngx.ctx.user_groups = cjson.encode({"users", "mlflow-users"})
    ngx.ctx.user_roles = cjson.encode({"user", "mlflow-reader"})
    return
end

local user_id = payload.sub or payload.preferred_username or payload.upn or payload.email or "test-user-123"
local user_email = payload.email or payload.preferred_username or payload.upn or "test@example.com"
local user_name = payload.name or payload.preferred_username or payload.upn or "Test User"

ngx.ctx.user_id = user_id
ngx.ctx.user_email = user_email
ngx.ctx.user_name = user_name
ngx.ctx.user_groups = cjson.encode({"users", "mlflow-users"})
ngx.ctx.user_roles = cjson.encode({"user", "mlflow-reader"})
