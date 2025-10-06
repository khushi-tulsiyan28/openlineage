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

local function strip_bom_and_trim(s)
    if type(s) ~= "string" then return "" end
    local bom = string.char(0xEF, 0xBB, 0xBF)
    if s:sub(1, 3) == bom then
        s = s:sub(4)
    end
    s = s:match("^%s*(.-)%s*$") or s
    return s
end

function M.load_policy()
    local content, err = safe_read_file(POLICY_PATH)
    if not content then
        return {}
    end
    local cleaned = strip_bom_and_trim(content)
    local ok, data = pcall(cjson.decode, cleaned)
    if not ok or type(data) ~= "table" then
        return {}
    end

    local normalized = { users = {}, groups = {} }

    local function normalize_subject_table(src, dst)
        for key, value in pairs(src or {}) do
            local subject_key = string.lower(tostring(key))
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
            dst[subject_key] = { experiments = experiments }
        end
    end

    if data.users or data.groups then
        normalize_subject_table(data.users or {}, normalized.users)
        normalize_subject_table(data.groups or {}, normalized.groups)
    else
        normalize_subject_table(data, normalized.users)
    end

    ngx.log(ngx.ERR, "DEBUG policy loaded users=", cjson.encode(normalized.users or {}),
        " groups=", cjson.encode(normalized.groups or {}))
    return normalized
end

function M.get_allowed_experiments(email)
    local policy = M.load_policy()
    local entry = (policy.users or {})[string.lower(email or "")] or {}
    ngx.log(ngx.ERR, "Policy lookup (user) for email=", email, " -> ", cjson.encode(entry.experiments or {}))
    return entry.experiments or {}
end

function M.get_allowed_experiments_union(email, groups)
    local policy = M.load_policy()
    local result_set = {}

    local user_entry = (policy.users or {})[string.lower(email or "")] or {}
    for _, id in ipairs(user_entry.experiments or {}) do
        result_set[tostring(id)] = true
    end

    if type(groups) == "table" then
        for _, gid in ipairs(groups) do
            local ge = (policy.groups or {})[string.lower(tostring(gid))] or {}
            for _, id in ipairs(ge.experiments or {}) do
                result_set[tostring(id)] = true
            end
        end
    end

    local result = {}
    for id, _ in pairs(result_set) do table.insert(result, id) end
    ngx.log(ngx.ERR, "Policy union for email=", email, ", groups=", cjson.encode(groups or {}), " -> ", cjson.encode(result))
    return result
end

return M


