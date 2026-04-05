# postfix-limit
Simple mail limiter for postfix (check_policy_service)

## Installation
### TL;DR
~~~
PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install git+https://github.com/yaroslaff/postfixlimit
wget https://raw.githubusercontent.com/yaroslaff/postfixlimit/refs/heads/master/contrib/postfixlimit.service
wget https://raw.githubusercontent.com/yaroslaff/postfixlimit/refs/heads/master/contrib/postfixlimit.conf

cp postfixlimit.service /etc/systemd/system/
systemctl daemon-reload

cp postfixlimit.conf /etc/
~~~

After this, edit `/etc/postfixlimit.conf`, maybe you want to change `field`, `default_limit` specific limits. Then start daemon: `systemcctl start postfixlimit`.


~~~
# and same for clean uninstall (if you will ever need)
PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx uninstall postfixlimit
~~~

## Systemd unit file
Copy [contrib/postfixlimit.service](contrib/postfixlimit.service) as `/etc/systemd/system/postfixlimit.service`.
Do `systemctl daemon-reload` after this and then: `systemctl start postfixlimit`

## Example config file
Example config file is in [contrib/postfixlimit.conf](contrib/postfixlimit.conf), save it as `/etc/postfixlimit.conf`
~~~
# Main server options
[server]
address = 127.0.0.1
port = 4455

# field is one of sender/sasl_username/client_address
field = sender
default_limit = 5/day
action = DEFER
action_text = Limit ({limit}) exceeded for {field}={key}

# storage: this or memory:// (default) for memory storage
storage = redis://localhost:6379/

dump_period = 60
dump_file = /var/lib/postfixlimit/limits.txt
log_file = /var/log/postfixlimit/postfixlimit.log

# Specific limits
[limits]
aaa@example.com = 100 / day
~~~

## Limits configuration
Postfixlimit uses [limits](https://github.com/alisaifee/limits) package for this. Limits could be configured according to it's [documentation](https://limits.readthedocs.io/en/stable/quickstart.html#rate-limit-string-notation). Format is: `[count] [per|/] [n (optional)] [second|minute|hour|day|month|year]`.

## Integration with postfix
add this to `smtpd_recipient_restrictions` in `main.cf`:
~~~
smtpd_recipient_restrictions = 
        check_policy_service inet:127.0.0.1:4455
~~~

## Protocol specification
https://www.postfix.org/SMTPD_POLICY_README.html
