# Output pubblico revisionato — Fase 4

## Interfacce e forwarding

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
wlx<REDACTED>  UP  10.42.0.1/24
1.1.1.1 via 192.168.10.1 dev wlp13s0 src 192.168.10.x
net.ipv4.ip_forward = 1
```

## Profilo

```text
connection.id:             security-gateway-ap
connection.interface-name: wlx<REDACTED>
ipv4.method:               shared
ipv4.addresses:            10.42.0.1/24
ipv4.gateway:              --
ipv4.dns:                  --
```

## Servizi

```text
10.42.0.1:53/udp  dnsmasq
10.42.0.1:53/tcp  dnsmasq
0.0.0.0:67/udp    dnsmasq
```

## DHCP

```text
DHCPDISCOVER(wlx<REDACTED>) <CLIENT_MAC>
DHCPOFFER(wlx<REDACTED>) 10.42.0.x <CLIENT_MAC>
DHCPREQUEST(wlx<REDACTED>) 10.42.0.x <CLIENT_MAC>
DHCPACK(wlx<REDACTED>) 10.42.0.x <CLIENT_MAC>
```

## NAT

```text
ip saddr 10.42.0.0/24
ip daddr != 10.42.0.0/24
masquerade
```

## Prima del NAT

```text
10.42.0.x:PORTA_CLIENT > 17.253.x.x:443
17.253.x.x:443 > 10.42.0.x:PORTA_CLIENT
```

## Dopo il NAT

```text
192.168.10.x:PORTA_ESTERNA > 17.253.x.x:443
17.253.x.x:443 > 192.168.10.x:PORTA_ESTERNA
```

## DNS

```text
10.42.0.x:PORTA > 10.42.0.1:53
A? time.apple.com.

10.42.0.1:53 > 10.42.0.x:PORTA
CNAME time.g.aaplimg.com.
A 17.253.x.x
```

## Sicurezza finale

```text
key-mgmt: wpa-psk
proto:    rsn
pairwise: ccmp
group:    ccmp
```
