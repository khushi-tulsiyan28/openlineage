local cjson = require "cjson"

local experiment_access = {
    ["test-user-123"] = {
        experiments = {"0", "1", "5", "8"},
        permissions = {"read", "write"}
    },
    ["admin-user"] = {
        experiments = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"},
        permissions = {"read", "write", "admin"}
    },
    ["viewer-user"] = {
        experiments = {"2", "7"},
        permissions = {"read"}
    }
}

local function get_user_experiments(user_id)
    local user_access = experiment_access[user_id]
    if not user_access then
        return {}
    end
    return user_access.experiments
end

local function has_experiment_access(user_id, experiment_id)
    local user_experiments = get_user_experiments(user_id)
    for _, exp_id in ipairs(user_experiments) do
        if exp_id == experiment_id then
            return true
        end
    end
    return false
end

local function filter_experiments(user_id, experiments_response)
    local user_experiments = get_user_experiments(user_id)
    local accessible_experiments = {}
    
    if experiments_response.experiments then
        for _, experiment in ipairs(experiments_response.experiments) do
            local exp_id = tostring(experiment.experiment_id)
            for _, allowed_id in ipairs(user_experiments) do
                if exp_id == allowed_id then
                    table.insert(accessible_experiments, experiment)
                    break
                end
            end
        end
    end
    
    experiments_response.experiments = accessible_experiments
    return experiments_response
end

ngx.ctx.get_user_experiments = get_user_experiments
ngx.ctx.has_experiment_access = has_experiment_access
ngx.ctx.filter_experiments = filter_experiments
