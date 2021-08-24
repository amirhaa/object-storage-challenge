--[[
    mongo.lua is responsible for queries on mongo
]]

local mongodb = require("mongo")

local MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
local MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME")
local MONGO_USER_COLLECTION = os.getenv("MONGO_USER_COLLECTION")

-- create mongodb client
local client = mongodb.Client(MONGO_CONNECTION_STRING)

-- get `user` collection
local collection = client:getCollection(MONGO_DATABASE_NAME, MONGO_USER_COLLECTION)

local mongo = {}

-- check if any user with this username and password
-- exists in database or not
function mongo.user_exists(username, passowrd)
    local query = mongodb.BSON(string.format('{"username":"%s", "password":"%s"}', username, passowrd))

    local result = collection:findOne(query)
    
    if result == nil then return false end
    return true
end

return mongo