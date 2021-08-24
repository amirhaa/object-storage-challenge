--[[
    auth.lua is responsible for validate request 
    and also generate jwt token
]]

local jwt = require("resty.jwt")
local mongo = require("etc/nginx/lua/mongo")
local helper = require("etc/nginx/lua/helper")
local cjson = require("cjson")

local auth = {}

local jwt_secret = 'some_secret_key'

-- validate jwt token
function auth.validate_request()
    local function fail_jwt_validation_request()
        local error_table = {error="forbidden"}

        helper.say(ngx.HTTP_UNAUTHORIZED, cjson.encode(error_table))
    end

    local token = ngx.req.get_headers()["Authorization"]
    
    if token == nil then fail_jwt_validation_request() end

    local jwt_token = token:gsub("JWT ", "")

    local jwt_obj = jwt:verify(jwt_secret, jwt_token)

    if not jwt_obj["verified"] then fail_jwt_validation_request() end
end

-- check username and password in mongo
-- and generate jwt token with username
-- in the payload of the jwt token
function auth.generate_token(username, password)
    if not mongo.user_exists(username, password) then
        local error_table = {error="wrong username or password"}

        helper.say(ngx.HTTP_NOT_FOUND, cjson.encode(error_table))
    end

    local jwt_token = jwt:sign(jwt_secret,
        {
            header={typ="JWT", alg="HS256"},
            payload={username=username}
        }
    )
    local result_table = {token=jwt_token}

    helper.say(ngx.HTTP_CREATED, cjson.encode(result_table))
end

return auth