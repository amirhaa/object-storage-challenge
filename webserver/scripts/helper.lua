--[[
    helper is a module that enclosed
    bunch of helper function to use 
    in the scripts
]]

local helper = {}

-- status nginx status
-- and return the result to client
-- then exit nginx
function helper.say(status, encoded_response)
    ngx.status = status
    ngx.say(encoded_response)
    ngx.exit(ngx.status)
end

return helper