local cjson = require "cjson"

local user_id = ngx.ctx.user_id or "unknown"
local user_email = ngx.ctx.user_email or "unknown"
local user_name = ngx.ctx.user_name or "unknown"
local user_groups = ngx.ctx.user_groups or "[]"
local user_roles = ngx.ctx.user_roles or "[]"

ngx.header["X-User-ID"] = user_id
ngx.header["X-User-Email"] = user_email
ngx.header["X-User-Name"] = user_name
ngx.header["X-User-Groups"] = user_groups
ngx.header["X-User-Roles"] = user_roles

if ngx.var.http_authorization then
    ngx.header["X-Original-Authorization"] = ngx.var.http_authorization
end
