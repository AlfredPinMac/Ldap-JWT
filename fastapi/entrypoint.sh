#!/bin/bash
set -e

mkdir -p /var/log/ldap-auth /var/run/fail2ban
touch /var/log/ldap-auth/access.log /var/log/ldap-auth/ldap_tls.log /var/log/fail2ban.log
rm -f /var/run/fail2ban/fail2ban.sock /var/run/fail2ban/fail2ban.pid

# Configure port-level protection rule for LDAP TLS (Port 636) and port 389
iptables -N LDAP_TLS_PROTECT 2>/dev/null || true
iptables -F LDAP_TLS_PROTECT 2>/dev/null || true
iptables -A LDAP_TLS_PROTECT -m recent --name LDAP_DOS --update --seconds 10 --hitcount 20 -j DROP
iptables -A LDAP_TLS_PROTECT -m recent --name LDAP_DOS --set -j ACCEPT
iptables -A INPUT -p tcp --dport 636 -j LDAP_TLS_PROTECT 2>/dev/null || true
iptables -A INPUT -p tcp --dport 389 -j LDAP_TLS_PROTECT 2>/dev/null || true

# Start FastAPI/Uvicorn on port 8000 in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 2

# Start Fail2ban service
fail2ban-client -x start

echo "[ldap-auth-api] FastAPI + Fail2Ban + LDAP TLS Port Protection running. Following /var/log/fail2ban.log..."
exec tail -F /var/log/fail2ban.log
