local cjson = require "cjson"

local M = {}

local POLICY_PATH = "/usr/local/openresty/nginx/policy/experiment_access.json"

local function safe_read_file(path)
    local f, err = io.open(path, "r")
    if not f then return nil, err end
    local content = f:read("*a")
    f:close()
    return content
end

function M.load_policy()
    local content, err = safe_read_file(POLICY_PATH)
    if not content then
        return {}
    end
    local ok, data = pcall(cjson.decode, content)
    if not ok or type(data) ~= "table" then
        return {}
    end
    -- Normalize keys to lowercase and values to string arrays
    local normalized = {}
    for key, value in pairs(data) do
        local email_lc = string.lower(tostring(key))
        local experiments = {}
        if type(value) == "table" and type(value.experiments) == "table" then
            for _, id in ipairs(value.experiments) do
                table.insert(experiments, tostring(id))
            end
        elseif type(value) == "table" then
            for _, id in ipairs(value) do
                table.insert(experiments, tostring(id))
            end
        end
        normalized[email_lc] = { experiments = experiments }
    end
    return normalized
end

function M.get_allowed_experiments(email)
    local policy = M.load_policy()
    local entry = policy[string.lower(email or "")] or {}
    ngx.log(ngx.ERR, "Policy lookup for email: ", email, " -> experiments: ", cjson.encode(entry.experiments or {}))
    return entry.experiments or {}
end

return M


