#!/bin/sh
HOST_IP=$(ip route | awk 'NR==1 {print $3}')
if [ -z "$HOST_IP" ]; then
  echo "Error: Unable to determine host IP address. Exiting."
  exit 1
fi

echo "dynamic_chain
proxy_dns
[ProxyList]
socks5 $HOST_IP 9090
" > /etc/proxychains4.conf

