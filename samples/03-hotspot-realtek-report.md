# Report pubblico anonimizzato — Fase 3

Data verifica: 15–16 luglio 2026  
Fase: hotspot Wi-Fi con Realtek USB  
Esito: completata e verificata

## Scopo

Creare un hotspot di laboratorio stabile sulla scheda Realtek USB senza interrompere la connessione Internet della MediaTek.

## Valori pubblicabili

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
GATEWAY_IP=10.42.0.1/24
IPV4_METHOD=shared
IPV6_MODE=disabled
AUTOCONNECT=no
```

La password WPA, gli indirizzi MAC e il nome completo dell'interfaccia Realtek non sono inclusi.

## Configurazione applicata

```bash
sudo nmcli connection add \
    type wifi \
    ifname <AP_IF> \
    con-name security-gateway-ap \
    ssid SecurityGatewayLab

sudo nmcli connection modify security-gateway-ap \
    connection.autoconnect no \
    802-11-wireless.mode ap \
    802-11-wireless.band bg \
    802-11-wireless.channel 6 \
    802-11-wireless-security.key-mgmt wpa-psk \
    ipv4.method shared \
    ipv4.addresses 10.42.0.1/24 \
    ipv4.never-default yes \
    ipv6.method disabled

sudo nmcli --ask connection up \
    security-gateway-ap \
    ifname <AP_IF>
```

## Dominio regolamentare

È stato richiesto temporaneamente:

```bash
sudo iw reg set IT
```

Il kernel ha mostrato:

```text
country 98: DFS-ETSI
```

Il canale 6 a 2,4 GHz è risultato disponibile con potenza indicata di 20 dBm.

## Risultati radio

```text
ssid SecurityGatewayLab
type AP
channel 6 (2437 MHz), width: 20 MHz
txpower 20.00 dBm
```

La Realtek è passata dalla modalità `managed` alla modalità `AP`.

## Indirizzamento

```text
Gateway hotspot: 10.42.0.1/24
Client osservato: 10.42.0.x
Route Internet host: via 192.168.10.1 dev wlp13s0
```

Almeno un client risultava:

```text
authorized: yes
authenticated: yes
associated: yes
```

## Test client → gateway

È stato avviato un server HTTP temporaneo sul gateway:

```bash
python3 -m http.server 8000 \
    --bind 10.42.0.1 \
    --directory /tmp/hotspot-gateway-test
```

Il client ha ricevuto una risposta HTTP `200` da `10.42.0.1`, confermando la raggiungibilità del gateway attraverso l'hotspot.

## Navigazione Internet

La navigazione del client è stata osservata attraverso Ubuntu.

Il profilo usa:

```text
ipv4.method=shared
```

NetworkManager ha quindi predisposto la condivisione IPv4 necessaria per permettere al client di usare l'uplink predefinito `wlp13s0`.

Il comportamento dettagliato di DHCP, DNS, forwarding e NAT viene studiato nella fase 4.

## Backup locale

Lo stato completo dei profili NetworkManager è stato salvato fuori dal repository pubblico. I segreti risultavano nascosti come:

```text
802-11-wireless-security.psk: <hidden>
```

## Rollback verificato

Spegnimento ed eliminazione:

```bash
sudo nmcli connection down security-gateway-ap
sudo nmcli connection delete security-gateway-ap
```

Dopo l'eliminazione sono stati verificati:

```text
profilo non presente
Realtek disconnessa
nessun IPv4 sulla Realtek
MediaTek ancora collegata
route Internet ancora tramite wlp13s0
```

Il profilo è stato poi ricreato e riattivato con successo usando gli stessi parametri.

## Test dopo riavvio

Dopo un riavvio completo:

```text
security-gateway-ap: presente ma inattivo
connection.autoconnect: no
Realtek: disconnessa
IPv4 sulla Realtek: assente
MediaTek: collegata
route Internet: ancora tramite wlp13s0
```

Il comportamento è quello previsto: il profilo resta salvato ma l'hotspot non parte automaticamente.

## Privacy applicata

Sono stati rimossi o mascherati:

- SSID domestico;
- password WPA;
- indirizzi MAC della Realtek e dei client;
- nome completo `wlx...`;
- indirizzo IPv4 completo dell'host;
- hostname e percorsi locali.

## Esito

- [x] profilo hotspot creato;
- [x] SSID e WPA-PSK configurati;
- [x] banda 2,4 GHz e canale 6 verificati;
- [x] hotspot attivo soltanto sulla Realtek;
- [x] uplink MediaTek rimasto collegato;
- [x] client autorizzati associati;
- [x] indirizzo IPv4 assegnato;
- [x] gateway raggiunto dal client;
- [x] navigazione Internet osservata;
- [x] backup locale creato con segreti nascosti;
- [x] arresto e riattivazione verificati;
- [x] eliminazione e ricreazione del profilo verificate;
- [x] comportamento dopo riavvio verificato.

## Conclusione

La Realtek RTL8812AU funziona come access point stabile sulla banda 2,4 GHz, canale 6. I client possono collegarsi alla rete `SecurityGatewayLab`, raggiungere il gateway Ubuntu e usare l'uplink MediaTek. Il rollback e il comportamento dopo riavvio sono stati verificati.
