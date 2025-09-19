local cjson = require "cjson"

local auth_header = ngx.var.http_authorization
if not auth_header then
    ngx.status = 401
    ngx.say(cjson.encode({
        error = "unauthorized",
        message = "Authorization header required"
    }))
    return
end

local token = auth_header:match("Bearer%s+(.+)")
if not token then
    ngx.status = 401
    ngx.say(cjson.encode({
        error = "unauthorized",
        message = "Bearer token required"
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

local user_id = payload.sub or "test-user-123"
local user_email = payload.email or "test@example.com"
local user_name = payload.name or "Test User"

ngx.ctx.user_id = user_id
ngx.ctx.user_email = user_email
ngx.ctx.user_name = user_name
ngx.ctx.user_groups = cjson.encode({"users", "mlflow-users"})
ngx.ctx.user_roles = cjson.encode({"user", "mlflow-reader"})
