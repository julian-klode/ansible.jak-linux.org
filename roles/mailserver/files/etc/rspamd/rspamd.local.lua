-- Ansible managed

local logger = require "rspamd_logger"
local tcp = require "rspamd_tcp"
local rspamd_regexp = require "rspamd_regexp"

local ok = rspamd_regexp.create_cached('^200 (.*)')

-- SRS rewriting for incoming messages.
--
-- Rewrites the envelope sender when returning the message to postfix
-- via the milter interface.
rspamd_config:register_symbol('SRS', 1.0,
  function(task)

    from = task:get_from('smtp')[1]['addr']

    if from == nil then
      return true
    end

    local function cb(err, data)
      result = tostring(data)
      logger.infox('query result for %1: err: %2, %3', from, err, tostring(data))

      result = tostring(data)
      match = ok:search(result, false, true)
      logger.infox('match: %1 is %2', match)
      if match ~= nil then
        logger.infox('rewriting %1 to "%2"', from, match[1][2])
        task:set_milter_reply{
          change_from = match[1][2]
        }
      end
    end

    tcp.request({
      task = task,
      host = "localhost",
      port = 10001,
      data = {"get " .. from .. "\r\n"},
      callback = cb})

    return true
  end)

