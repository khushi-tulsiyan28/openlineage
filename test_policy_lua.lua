-- Test script to verify policy loading
local cjson = require "cjson"

-- Mock the policy data exactly as in the file
local policy_data = {
  ["kushit@techdwarfs.com"] = { 
    experiments = {"1", "2"} 
  }
}

local function get_allowed_experiments(email)
    local entry = policy_data[(email or ""):lower()]
    if not entry then 
        print("No entry found for email:", email)
        return {} 
    end
    print("Found entry for email:", email, "experiments:", cjson.encode(entry.experiments))
    return entry.experiments or {}
end

-- Test the function
local email = "kushit@techdwarfs.com"
local experiments = get_allowed_experiments(email)
print("Email:", email)
print("Allowed experiments:", cjson.encode(experiments))
print("Count:", #experiments)

