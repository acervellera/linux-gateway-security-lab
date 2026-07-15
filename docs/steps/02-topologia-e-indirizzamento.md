# Fase 2 — Topologia e piano di indirizzamento

## Stato

```text
COMPLETATA E VERIFICATA
```

Verifica eseguita il 15 luglio 2026 con comandi di osservazione. In questa fase non sono state applicate modifiche alla rete.

## Obiettivo

Definire prima delle modifiche:

- ruolo delle interfacce;
- subnet IPv4 del laboratorio;
- indirizzo del gateway;
- intervallo e durata DHCP;
- DNS distribuito ai client;
- profilo e SSID dell'hotspot;
- banda e canale iniziali;
- comportamento IPv6;
- percorso previsto dei pacchetti;
- convivenza con Docker, libvirt e rete locale.

## Metodo usato

Sono stati eseguiti soltanto comandi di lettura:

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

Nessuno di questi comandi ha creato un hotspot, modificato indirizzi, attivato il forwarding o applicato regole firewall.

## Interfacce verificate

### Uplink verso Internet

```text
UPLINK_IF=wlp13s0
UPLINK_NETWORK=192.168.10.0/24
UPLINK_HOST_IP=192.168.10.x/24
UPLINK_GATEWAY=192.168.10.1
```

La route predefinita usa `wlp13s0`, quindi questa interfaccia rimane l'uscita Internet del gateway.

### Interfaccia destinata all'hotspot

Il nome locale completo incorpora l'indirizzo MAC e non viene pubblicato nel repository.

```text
AP_IF=wlx<REDACTED>
AP_STATE=disconnected
AP_MODE_CURRENT=managed
AP_MODE_SUPPORTED=yes
```

La Realtek USB dichiara supporto alle modalità:

- `managed`;
- `AP`;
- `AP/VLAN`;
- `monitor`.

L'identificatore `phy` osservato può cambiare dopo riavvii o scollegamenti USB e non deve essere usato come nome persistente in una configurazione.

## Reti già presenti

Sono state verificate le seguenti subnet:

| Subnet | Utilizzo |
|---|---|
| `192.168.10.0/24` | rete locale dell'uplink |
| `192.168.122.0/24` | rete libvirt `default` |
| `10.10.10.0/24` | rete libvirt isolata `lab-lan` |
| `172.17.0.0/16` | bridge Docker predefinito |
| `172.18.0.0/16` | bridge Docker del laboratorio Python |

Le reti Docker `host` e `none` non assegnano una normale subnet bridge separata.

## Controllo dei conflitti

La subnet proposta per l'hotspot:

```text
10.42.0.0/24
```

non compare tra:

- rotte IPv4 attive o registrate dal kernel;
- indirizzi assegnati alle interfacce;
- profili NetworkManager;
- reti libvirt;
- reti Docker.

Il controllo non può garantire che una rete esterna futura non usi la stessa subnet, ma conferma che non esiste un conflitto nell'ambiente osservato durante la fase 2.

## Piano di indirizzamento approvato

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

### Significato degli indirizzi

```text
10.42.0.0      indirizzo della rete
10.42.0.1      gateway Ubuntu e DNS locale previsto
10.42.0.2-49   spazio riservato per eventuali indirizzi statici
10.42.0.50     primo indirizzo assegnabile via DHCP
10.42.0.200    ultimo indirizzo assegnabile via DHCP
10.42.0.201-254 spazio libero per usi futuri
10.42.0.255    indirizzo broadcast
```

## Scelta della durata DHCP

Il lease iniziale è impostato a un'ora:

```text
3600 secondi
```

È adatto a un laboratorio perché gli indirizzi vengono riciclati in tempi brevi e i dispositivi di prova non conservano a lungo configurazioni non più necessarie.

## DNS previsto

I client useranno inizialmente:

```text
10.42.0.1
```

Ubuntu agirà da punto DNS locale per i client e inoltrerà le richieste secondo la configurazione effettiva dell'uplink. Il comportamento reale dovrà essere collaudato nelle fasi 3 e 4.

## Banda e canale iniziali

La scansione locale ha rilevato reti forti sui canali 1 e 10 della banda 2,4 GHz e reti anche nella banda 5 GHz.

Per il primo test è stato scelto:

```text
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
```

Motivazioni:

- maggiore compatibilità con dispositivi di prova;
- nessuna rete osservata esattamente sul canale 6;
- il canale 1 era già occupato da un segnale forte;
- il canale 11 sarebbe troppo vicino alle reti osservate sul canale 10;
- l'uplink usa già la banda 5 GHz;
- nella prima prova vengono evitati i canali DFS.

Il canale 6 è una scelta iniziale, non una garanzia di assenza di interferenze. La qualità reale verrà verificata con un client collegato.

## Dominio regolamentare

Durante la raccolta il kernel riportava:

```text
REGDOMAIN_CURRENT=GB
REGDOMAIN_REQUIRED=IT
```

Il dominio regolamentare deve essere corretto a `IT` prima dell'attivazione dell'hotspot, perché determina canali e potenze consentiti. La correzione non è stata applicata nella fase 2.

## Gestione IPv6 iniziale

Per ridurre le variabili durante i primi test:

```text
IPV6_MODE=disabled-on-hotspot-initially
```

La scelta riguarda il profilo hotspot e non richiede di disabilitare IPv6 globalmente sull'uplink. IPv6 potrà essere introdotto e verificato in una fase successiva.

## Isolamento dei client

La politica desiderata è isolare i client tra loro quando il supporto di NetworkManager, driver e modalità AP lo consente.

Se l'isolamento non è disponibile nel primo test, verrà collegato un solo dispositivo autorizzato alla volta fino all'introduzione di regole firewall specifiche.

## Topologia approvata

```text
Client di test autorizzato
        |
        | Wi-Fi: SecurityGatewayLab
        | rete: 10.42.0.0/24
        v
Realtek USB — AP_IF=wlx<REDACTED>
        |
        v
Ubuntu gateway — 10.42.0.1
        |
        | routing / firewall / NAT nelle fasi successive
        v
MediaTek — UPLINK_IF=wlp13s0
        |
        v
Router locale — 192.168.10.1
        |
        v
Internet
```

## Percorso previsto dei pacchetti

```text
client 10.42.0.x
  -> interfaccia hotspot Realtek
  -> decisione firewall nella chain forward
  -> routing IPv4 del kernel
  -> NAT/masquerading
  -> wlp13s0
  -> router 192.168.10.1
  -> Internet
```

La risposta dovrà tornare attraverso la connessione già tracciata dal kernel:

```text
Internet
  -> wlp13s0
  -> conntrack e traduzione NAT inversa
  -> decisione firewall
  -> interfaccia hotspot
  -> client 10.42.0.x
```

Il percorso è stato progettato ma non ancora collaudato end-to-end, perché hotspot, forwarding, NAT e firewall appartengono alle fasi successive.

## Tabella completata

| Elemento | Valore verificato o deciso |
|---|---|
| Interfaccia uplink | `wlp13s0` |
| Interfaccia hotspot | `wlx<REDACTED>` |
| Subnet laboratorio | `10.42.0.0/24` |
| Gateway | `10.42.0.1` |
| Range DHCP | `10.42.0.50-10.42.0.200` |
| Durata lease | `3600` secondi |
| DNS | `10.42.0.1` |
| Profilo hotspot | `security-gateway-ap` |
| SSID anonimizzato | `SecurityGatewayLab` |
| Banda | `2.4 GHz` |
| Canale iniziale | `6` |
| Gestione IPv6 | disabilitato inizialmente sul solo hotspot |
| Isolamento client | richiesto se supportato; altrimenti un client alla volta |
| Dominio regolamentare | correggere da `GB` a `IT` prima dell'attivazione |

## Privacy della documentazione

Nel repository pubblico non sono stati inseriti:

- SSID domestici reali;
- indirizzi MAC completi;
- nome completo dell'interfaccia `wlx...` che incorpora il MAC;
- indirizzo IPv4 completo dell'host;
- password o altri segreti.

I valori completi appartengono esclusivamente al report locale ignorato da Git.

## Test di completamento

- [x] nomi e ruoli delle interfacce verificati;
- [x] capacità `AP` dichiarata dalla Realtek;
- [x] reti NetworkManager inventariate;
- [x] reti libvirt inventariate;
- [x] subnet Docker verificate con `docker network inspect`;
- [x] nessun conflitto locale per `10.42.0.0/24`;
- [x] gateway e intervallo DHCP definiti;
- [x] durata DHCP definita;
- [x] DNS iniziale definito;
- [x] profilo e SSID di laboratorio definiti;
- [x] banda e canale iniziali scelti;
- [x] comportamento IPv6 iniziale definito;
- [x] politica di isolamento client definita;
- [x] percorso dei pacchetti disegnato;
- [x] dati pubblici anonimizzati;
- [x] rollback del futuro profilo hotspot documentato.

## Modifiche effettuate

Nessuna configurazione di rete è stata modificata.

In particolare non sono stati:

- creati o attivati profili hotspot;
- modificati indirizzi IP;
- modificati DNS;
- attivati forwarding o NAT;
- applicate regole firewall;
- modificato il dominio regolamentare.

## Rollback

Non è necessario un rollback per la fase 2, perché sono stati usati soltanto comandi di osservazione.

Il rollback da usare nella fase 3, qualora venga creato il profilo previsto, sarà:

```bash
sudo nmcli connection down security-gateway-ap
sudo nmcli connection delete security-gateway-ap
```

Il primo comando disattiva il profilo se è attivo. Il secondo elimina la configurazione persistente da NetworkManager.

## Prossimo passo

Passare alla fase 3:

1. correggere e verificare il dominio regolamentare italiano;
2. creare il profilo `security-gateway-ap` sulla Realtek USB;
3. configurare `SecurityGatewayLab` sulla banda 2,4 GHz e canale 6;
4. collegare un solo client autorizzato;
5. verificare associazione Wi-Fi, indirizzo IP e rollback del profilo.
