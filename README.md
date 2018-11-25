# jak-linux.org configuration

This repository contains the ansible configuration for deploying
the machines in the jak-linux.org domain, and some related machines.


# Variables

## Websites

For each host, the array `domains` configures the domains configured
on that host to be served by `nginx`. It also configures TLS
certificates, either using dummy ones or letsencrypt.

Let's consider the following example:

```yaml
domains:
  - cname: example.com
    alias:
      - www.example.com
    nginx_add_locations:
      # This is added to the server configuration
      location ~ /iamfancy/ {
        fastcgi_pass    unix:/run/path/to/socket;
        include         fastcgi_params;
      }
letsencrypt_email: jak@jak-linux.org
```

This configures a domain with the canonical domain `example.com`,
and redirects from `wwww.example.com`. It also sets up `/iamfancy`
to passthrough to a fastcgi socket. Content will be served from the
directory `/var/www/example.com`, and one certificate will be generated
with `example.com` and `wwww.example.com` as subject alternative names.

Configured websites are TLS-only. They are configured with letsencrypt
certificates or dummy certificates, depending on whether they have the
role `letsencrypt` or `snake-oil-letsencrypt`. The latter is useful
for testing purposes.

*Confinement*: The nginx server is confined using AppArmor to only
read the SSL keys, webdata, and other stuff it needs to operate.

## Weechat

The `weechatserver` role configures a user called `weechat` and a
system `weechat` service that runs weechat inside of tmux. It also
installs `mosh` so you can connect to the running `weechat`.

Furthermore, it also configures a weechat relay to listen on port
9000 on localhost. This can then be made available through nginx using
websockets, for example, including a rate limiting to 5 requests per
minute:

```yaml
nginx_conf:
  weechat:
    # Rate limit weechat
    limit_req_zone $binary_remote_addr zone=weechat:10m rate=5r/m;

domains:
  - cname: example.com
    alias:
      - www.example.com
    nginx_add_locations: |
      location /weechat {
          proxy_pass http://localhost:9000/weechat; # Change the port to your relay's
          proxy_http_version 1.1;
          proxy_set_header Upgrade $http_upgrade;   # These two lines ensure that the
          proxy_set_header Connection "Upgrade";    # a WebSocket is used
          proxy_read_timeout 604800;                # Prevent idle disconnects
          proxy_set_header X-Real-IP $remote_addr;  # Let WeeChat see the client's IP
          limit_req zone=weechat burst=1 nodelay;   # Brute force prevention
      }
```

It is not exposed by default however.

*Confinement*: The weechat binary is confined to mostly ~/.weechat using
AppArmor, reducing the attack surface considerably.
