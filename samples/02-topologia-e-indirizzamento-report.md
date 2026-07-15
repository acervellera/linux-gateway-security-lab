# Report pubblico anonimizzato — Fase 2

Data verifica: 15 luglio 2026  
Fase: topologia e piano di indirizzamento  
Esito: completata e verificata

## Scopo

Verificare le reti già presenti e definire il piano IPv4 dell'hotspot senza modificare la configurazione dell'host.

## Dati pubblicabili

```text
UPLINK_IF=wlp13s0
UPLINK_NETWORK=192.168.10.0/24
UPLINK_HOST_IP=192.168.10.x/24
UPLINK_GATEWAY=192.168.10.1

AP_IF=wlx<REDACTED>
AP_STATE=disconnected
AP_MODE_CURRENT=managed
AP_MODE_SUPPORTED=yes
```

Il nome completo della Realtek e gli indirizzi MAC sono stati rimossi perché identificano il dispositivo locale.

## Subnet osservate

```text
192.168.10.0/24    uplink locale
192.168.122.0/24   libvirt default
10.10.10.0/24      libvirt lab-lan
172.17.0.0/16      Docker bridge
172.18.0.0/16      Docker cyber lab
```

## Piano approvato

```text
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
DHCP_START=10.42.0.50
DHCP_END=10.42.0.200
DHCP_LEASE_SECONDS=3600
DNS_SERVER=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
IPV6_MODE=disabled-on-hotspot-initially
CLIENT_ISOLATION=enable-if-supported
```

La subnet `10.42.0.0/24` non risultava presente nelle rotte, negli indirizzi, nei profili NetworkManager, nelle reti libvirt o nelle reti Docker osservate.

## Scelta Wi-Fi

La scansione locale, anonimizzata in questo report, ha mostrato:

- un segnale forte sul canale 1 della banda 2,4 GHz;
- segnali forti sul canale 10 della banda 2,4 GHz;
- reti presenti anche nella banda 5 GHz;
- uplink attivo nella banda 5 GHz.

Il canale 6 a 2,4 GHz è stato scelto come configurazione iniziale di test. La scelta dovrà essere collaudata con un client reale.

## Dominio regolamentare

```text
REGDOMAIN_CURRENT=GB
REGDOMAIN_REQUIRED=IT
```

La correzione a `IT` è stata pianificata per la fase 3 e non è stata applicata durante questa raccolta.

## Percorso progettato

```text
client 10.42.0.x
  -> hotspot Realtek
  -> firewall forward
  -> routing IPv4
  -> NAT/masquerading
  -> wlp13s0
  -> router 192.168.10.1
  -> Internet
```

Il percorso è soltanto progettato: nella fase 2 non sono stati attivati hotspot, forwarding, NAT o firewall.

## Comandi principali usati

```bash
ip -4 route
ip -4 address
nmcli device status
nmcli connection show
virsh net-list --all
sudo docker network ls
sudo docker network inspect <RETE>
iw dev
iw list
iw reg get
sudo nmcli device wifi rescan ifname <AP_IF>
nmcli --fields SSID,CHAN,FREQ,SIGNAL,SECURITY device wifi list ifname <AP_IF>
```

## Privacy applicata

Sono stati rimossi o mascherati:

- SSID domestici reali;
- indirizzi MAC;
- nome completo `wlx...`;
- indirizzo IPv4 completo dell'host;
- eventuali password o segreti.

## Esito

- [x] uplink identificato;
- [x] interfaccia AP identificata e anonimizzata;
- [x] supporto AP dichiarato;
- [x] reti Docker e libvirt verificate;
- [x] subnet senza conflitti locali scelta;
- [x] gateway, DHCP e DNS definiti;
- [x] profilo, SSID, banda e canale definiti;
- [x] percorso dei pacchetti disegnato;
- [x] nessuna modifica di rete applicata;
- [x] report pubblico revisionato.
