--[[
    app.lua is the entrypint of the scripts
    When a request is sent to nginx followings happen:

    - if request is /signin then we check for username
        password of the user in mongo, if user exists
        we generate a jwt token for the user with username
        in the payload of the token, otherwise reject the request.
    - if request is not option (and not /signin) 
        we check if jwt is exists in the header
        if not exists reject the request, if exists
        validate if it is valid.
    - if jwt token validated we send the request to the
        correspond address in (middleware service)

    Available endpoints:
        - /signin -> process here in lua + mongo
        - /bucket -> send to middleware service
]]

local auth = require("etc/nginx/lua/auth")
local helper = require("etc/nginx/lua/helper")
local cjson = require("cjson")

-- define all necessary variables
local middleware_service_address = os.getenv("MIDDLEWARE_SERVICE_URL")
local arvan_url = os.getenv("CREATE_BUCKET_BASE_API")

local content_type = "application/json; charset=utf-8"
local bucket_uri = middleware_service_address .. os.getenv("BUCKET_PATH")

-- start reading the body
ngx.req.read_body()

-- save original request necessary variables to use later
local orig_request_method = ngx.var.request_method
local orig_request_header = ngx.req.get_headers()
local orig_request_body = ngx.req.get_body_data()
local orig_req_uri = ngx.var.uri

-- decode the body into table for later use
local decoded_body = orig_request_body ~= nil and cjson.decode(orig_request_body) or {}

-- set nginx header to application/json for all responses
ngx.header.content_type = content_type

--[[
    ***********************************************
    **** request validation and signin handler ****
    ***********************************************
]]

-- if request uri is not /signin or request method is not option 
-- then validate the request for JWT token.
if orig_request_method ~= "OPTIONS" and not string.match(orig_req_uri, "signin") then 
    auth.validate_request() 
end

-- /signin handler
if orig_request_method == "POST" and string.match(orig_req_uri, 'signin') then
    local username = decoded_body['username']
    local password = decoded_body['password']
    local error_table = {}

    if username == nil then error_table["username"] = "username field is required" end
    if password == nil then error_table["password"] = "password field is required" end
    
    if next(error_table) ~= nil then
        helper.say(ngx.HTTP_BAD_REQUEST, cjson.encode(error_table))
    end

    -- validate username and password and generate jwt token
    auth.generate_token(username, password)
end

--[[
    *******************************
    **** handle bucket request ****
    *******************************
]]

-- create http client
local httpc = require("resty.http").new()

-- send request to `bucket_uri` in middleware to check out the bucket name
local res, err = httpc:request_uri(bucket_uri,
    {
        method = "POST", 
        headers={ content_type=content_type },
        body=orig_request_body,
    }
)

-- no response from the previous request
if not res then
    helper.say(ngx.HTTP_BAD_REQUEST, cjson.encode({error="request failed, " .. err}))
end

ngx.log(ngx.INFO, "response returned from validating middleware api ...")

-- middleware accepted the bucket name
-- now send request to arvan api to
-- create the bucket
if res.status == 200 then
    local bucket = decoded_body["bucket"]

    local bucket_url = arvan_url .. "/panel/bucket/" .. bucket .. "?is_public=false"
    -- send request to arvan to create the bucket
    local res, err = httpc:request_uri(bucket_url, {
        ssl_verify=false,
        method = "POST",
        headers={
            content_type=content_type,
            Authorization=os.getenv("CREATE_BUCKET_AUTH_TOKEN")
        },
    })

    -- no response from arvan
    if not res then
        helper.say(ngx.HTTP_BAD_REQUEST, cjson.encode({error="request failed, " .. err}))
    end

    -- send back arvan response to the client
    helper.say(res.status, res.body)
else
    -- do anyting else if response was not a 200
    helper.say(res.status, res.body)
end
