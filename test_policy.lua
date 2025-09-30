-- Test script to verify policy loading
local cjson = require "cjson"

-- Mock the policy data
local policy_data = {
  ["kushit@techdwarfs.com"] = { experiments = {"381747126836502912", "663922813976858922"} }
}

local function get_allowed_experiments(email)
    local entry = policy_data[(email or ""):lower()]
    if not entry then return {} end
    return entry.experiments or {}
end

-- Test the function
local email = "kushit@techdwarfs.com"
local experiments = get_allowed_experiments(email)
print("Email:", email)
print("Allowed experiments:", cjson.encode(experiments))

