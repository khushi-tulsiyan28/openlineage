-- MLflow Response Filter for Experiment Access Control
local cjson = require "cjson"

-- Mock experiment access control data (same as in experiment_access_control.lua)
local experiment_access = {
    ["test-user"] = {
        experiments = {"0", "1", "5", "8"},
        permissions = {"read", "write"}
    },
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

-- Get user's accessible experiments
local function get_user_experiments(user_id)
    local user_access = experiment_access[user_id]
    if not user_access then
        return {}
    end
    return user_access.experiments
end

-- Check if user has access to specific experiment
local function has_experiment_access(user_id, experiment_id)
    local user_experiments = get_user_experiments(user_id)
    for _, exp_id in ipairs(user_experiments) do
        if exp_id == experiment_id then
            return true
        end
    end
    return false
end

-- Filter experiments list based on user access
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

-- Body filter to process MLflow responses
local user_id = ngx.ctx.user_id
local request_path = ngx.var.request_uri

-- Only filter MLflow responses
if request_path:match("^/mlflow/") and user_id then
    local chunk, eof = ngx.arg[1], ngx.arg[2]
    
    if not ngx.ctx.filtered_response then
        ngx.ctx.filtered_response = ""
    end
    
    if chunk then
        ngx.ctx.filtered_response = ngx.ctx.filtered_response .. chunk
    end
    
    if eof then
        local response_body = ngx.ctx.filtered_response
        local success, response_data = pcall(cjson.decode, response_body)
        
        if success and response_data then
            -- Handle different MLflow endpoints
            if request_path:match("/experiments") and not request_path:match("/experiments/%d+") then
                -- Filter experiments list
                if response_data.experiments then
                    response_data = filter_experiments(user_id, response_data)
                end
            elseif request_path:match("/experiments/(%d+)") then
                -- Check access to specific experiment
                local experiment_id = request_path:match("/experiments/(%d+)")
                if not has_experiment_access(user_id, experiment_id) then
                    response_data = {
                        error = "access_denied",
                        message = "You don't have access to experiment " .. experiment_id
                    }
                end
            elseif request_path:match("/runs") then
                -- Filter runs based on experiment access
                if response_data.runs then
                    local accessible_runs = {}
                    for _, run in ipairs(response_data.runs) do
                        local exp_id = tostring(run.data.experiment_id or run.experiment_id)
                        if has_experiment_access(user_id, exp_id) then
                            table.insert(accessible_runs, run)
                        end
                    end
                    response_data.runs = accessible_runs
                end
            end
            
            ngx.arg[1] = cjson.encode(response_data)
        end
    else
        ngx.arg[1] = nil
    end
end
