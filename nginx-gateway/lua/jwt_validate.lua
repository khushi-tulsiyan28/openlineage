-- Simplified JWT Token Validation
local cjson = require "cjson"

-- Get JWT token from Authorization header
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

-- For now, accept any token that looks like a JWT (has 3 parts separated by dots)
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

-- Extract user info from JWT payload (simplified for testing)
-- In production, you would decode and verify the JWT properly
local payload_part = parts[2]
-- Add padding if needed for base64 decoding
local padding = 4 - (string.len(payload_part) % 4)
if padding ~= 4 then
    payload_part = payload_part .. string.rep("=", padding)
end

local success, payload_json = pcall(ngx.decode_base64, payload_part)
if not success then
    -- Fallback to default user if decoding fails
    ngx.ctx.user_id = "test-user-123"
    ngx.ctx.user_email = "test@example.com"
    ngx.ctx.user_name = "Test User"
    ngx.ctx.user_groups = cjson.encode({"users", "mlflow-users"})
    ngx.ctx.user_roles = cjson.encode({"user", "mlflow-reader"})
    return
end

local success2, payload = pcall(cjson.decode, payload_json)
if not success2 then
    -- Fallback to default user if JSON parsing fails
    ngx.ctx.user_id = "test-user-123"
    ngx.ctx.user_email = "test@example.com"
    ngx.ctx.user_name = "Test User"
    ngx.ctx.user_groups = cjson.encode({"users", "mlflow-users"})
    ngx.ctx.user_roles = cjson.encode({"user", "mlflow-reader"})
    return
end

-- Extract user ID from JWT payload
local user_id = payload.sub or "test-user-123"
local user_email = payload.email or "test@example.com"
local user_name = payload.name or "Test User"

-- Mock user info for testing (in production, decode and verify the JWT)
-- Store in nginx context for use in other phases
ngx.ctx.user_id = user_id
ngx.ctx.user_email = user_email
ngx.ctx.user_name = user_name
ngx.ctx.user_groups = cjson.encode({"users", "mlflow-users"})
ngx.ctx.user_roles = cjson.encode({"user", "mlflow-reader"})
