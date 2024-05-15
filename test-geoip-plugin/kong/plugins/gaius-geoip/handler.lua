local kong = kong
local geo = require 'kong.plugins.gaius-geoip.maxminddb'
local ipmatcher = require "resty.ipmatcher"

local response = kong.response

local MMDB_PATH = "/usr/share/GeoLite2-Country.mmdb"

local GaiusGeoIP = {
  PRIORITY = 2050,
  VERSION  = "0.3.0",
}

function match_bin(list, binary_remote_addr)
    
  local ip, err = ipmatcher.new(list)
  if err then
    return error("failed to create a new ipmatcher instance: " .. err)
  end

  local is_match
  is_match, err = ip:match_bin(binary_remote_addr)
  if err then
    return error("invalid binary ip address: " .. err)
  end

  return is_match
end

function GaiusGeoIP:init_worker()
  kong.log.info("GaiusGeoIP init_worker")
end

---
--- full :{"city":{"geoname_id":1799962,"names":{"en":"Nanjing","ru":"Нанкин","fr":"Nankin","pt-BR":"Nanquim","zh-CN":"南京","es":"Nankín","de":"Nanjing","ja":"南京市"}},"subdivisions":[{"geoname_id":1806260,"names":{"en":"Jiangsu","fr":"Province de Jiangsu","zh-CN":"江苏省"},"iso_code":"32"}],"country":{"geoname_id":1814991,"names":{"en":"China","ru":"Китай","fr":"Chine","pt-BR":"China","zh-CN":"中国","es":"China","de":"China","ja":"中国"},"iso_code":"CN"},"registered_country":{"geoname_id":1814991,"names":{"en":"China","ru":"Китай","fr":"Chine","pt-BR":"China","zh-CN":"中国","es":"China","de":"China","ja":"中国"},"iso_code":"CN"},"location":{"time_zone":"Asia\/Shanghai","longitude":118.7778,"accuracy_radius":50,"latitude":32.0617},"continent":{"geoname_id":6255147,"names":{"en":"Asia","ru":"Азия","fr":"Asie","pt-BR":"Ásia","zh-CN":"亚洲","es":"Asia","de":"Asien","ja":"アジア"},"code":"AS"}}
---

-- LOOPS
function includeOrExcludes(arr, element, initial_value)
  for i,line in ipairs(arr) do
    if line == element then
      return (initial_value + 1)%2
    end 
  end
  return initial_value
end

-- Access Phase
function GaiusGeoIP:access(conf)
  geo.init(MMDB_PATH)

  local binary_remote_addr = ngx.var.binary_remote_addr
  local remote_addr = ngx.var.remote_addr
  if not binary_remote_addr then
    return kong.response.error(403, "Cannot identify the client IP address, unix domain sockets are not supported.")
  end

  -- Global ip restriction allowed
  if kong.ctx.shared.is_trusted and remote_addr == "127.0.0.1" then
    return
  end
  
  local geoinfo = geo.lookup(remote_addr)
  local country = geoinfo.country
  
  if country == nil then
    kong.log.err("Plugin DEBUG message : Country not found : ", remote_addr)
    return
  end

  -- INJECT HEADER 
  if conf.inject_country_header ~= nil then
    kong.response.set_header(conf.inject_country_header, country.iso_code)
  end
  
  -- BLOCK IP IF MATCH RULES
  local block = 1

  -- PRIORTIZING WHITELISTED IPS
  if conf.whitelist_ips and #conf.whitelist_ips > 0 then
    local allowed = match_bin(conf.whitelist_ips, binary_remote_addr)
    if allowed then
      block = 0
    end
  end

  if block == 1 then
    if ( conf.mode == "Blacklist" and conf.blacklist_countries ~= nil ) then
      block = includeOrExcludes(conf.blacklist_countries, country.iso_code, 0)
    elseif ( conf.mode == "Whitelist" and conf.whitelist_countries ~= nil) then
      block = includeOrExcludes(conf.blacklist_countries, country.iso_code, 1)
    end
  end

  
  
  if block == 1 then
    kong.response.set_header("x-geoip", "BLOCKED")
    kong.response.exit(403, "Access not available for your ip: " .. remote_addr .. ", " .. country.iso_code)
  end
end


return GaiusGeoIP

