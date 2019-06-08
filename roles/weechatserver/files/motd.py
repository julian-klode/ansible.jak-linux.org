# Managed by Ansible.
# Copyright (C) 2019 Julian Andres Klode <jak@jak-linux.org>
"""Script to display the current motd on an Ubuntu system"""
import weechat
import os

weechat.register("motd", "jak@jak-linux.org", "0.1.0",
                 "Apache-2.0", "Display the current motd", "", "")

buffer = weechat.buffer_new("motd", "", "", "", "")
weechat.buffer_set(buffer, "motd", "Message of the day")
weechat.buffer_set(buffer, "localvar_set_no_log", "1")


previous_mtime = 0


def timer_cb(data, remaining_calls):
    global previous_mtime
    try:
        mtime = os.stat("/run/motd.dynamic").st_mtime
    except OSError:
        return  # Try again later
    if mtime == previous_mtime:
        return weechat.WEECHAT_RC_OK

    previous_mtime = mtime
    weechat.buffer_clear(buffer)
    with open("/run/motd.dynamic") as motd:
        for line in motd:
            weechat.prnt(buffer, line)

    return weechat.WEECHAT_RC_OK


timer_cb(None, None)
weechat.hook_timer(5 * 60 * 1000, 0, 0, "timer_cb", "")
