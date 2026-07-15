# Fase 3 — Hotspot Wi-Fi con Realtek USB

## Stato

```text
IN CORSO — hotspot attivo e client reali associati
```

Verifica eseguita il 15 luglio 2026 su Ubuntu 26.04 LTS con kernel `7.0.0-27-generic`.

## Obiettivo

Creare un hotspot di laboratorio stabile sulla scheda Realtek USB senza interrompere la connessione Internet della MediaTek.

## Prerequisiti

- fase 1 completata;
- fase 2 completata;
- `AP_IF` e `UPLINK_IF` verificati;
- supporto `AP` dichiarato dalla radio Realtek;
- console locale disponibile;
- password di laboratorio non pubblicata nel repository.

## Valori usati

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
GATEWAY_IP=10.42.0.1/24
IPV6_MODE=disabled
AUTOCONNECT=no
```

Il nome completo dell'interfaccia Realtek e gli indirizzi MAC rimangono esclusivamente nei dati locali.

## Approccio iniziale

La prima prova usa NetworkManager, perché consente di creare rapidamente un profilo hotspot e verificare radio, DHCP e associazione dei client. In seguito le funzioni potranno essere separate per studiare `hostapd`, DHCP, routing e firewall in modo indipendente.

## Attività

- [ ] salvare in un file locale lo stato completo dei profili NetworkManager;
- [x] creare un profilo hotspot con nome riconoscibile;
- [x] impostare SSID e sicurezza WPA-PSK;
- [x] scegliere banda 2,4 GHz e canale 6;
- [x] attivare il profilo sulla sola Realtek;
- [x] verificare che la MediaTek resti collegata;
- [x] collegare dispositivi autorizzati;
- [x] verificare associazione e indirizzo assegnato;
- [x] fermare e riattivare l'hotspot;
- [ ] verificare esplicitamente la raggiungibilità del gateway dal client;
- [ ] verificare il rollback eliminando e ricreando il profilo;
- [ ] verificare il comportamento dopo riavvio solo quando richiesto.

## Dominio regolamentare osservato

È stato richiesto temporaneamente il dominio italiano:

```bash
sudo iw reg set IT
```

Il valore effettivamente mostrato dal kernel dopo il comando è stato:

```text
country 98: DFS-ETSI
```

Il driver o il firmware non ha quindi mostrato letteralmente `IT`, ma ha applicato un dominio ETSI che consente il canale 6 a 2,4 GHz con potenza indicata di 20 dBm. Il comportamento è stato annotato senza tentare forzature aggiuntive.

## Comandi realmente eseguiti

I comandi seguenti sono riportati con il nome dell'interfaccia anonimizzato.

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

sudo nmcli --ask connection up security-gateway-ap ifname <AP_IF>
```

Il segreto WPA non viene riportato nella documentazione pubblica.

## Verifiche eseguite

```bash
nmcli device status
nmcli connection show --active
iw dev <AP_IF> info
ip -4 address show dev <AP_IF>
ip -4 route get 1.1.1.1
ip neigh show dev <AP_IF>
sudo iw dev <AP_IF> station dump
```

## Risultati osservati

La Realtek è passata correttamente dalla modalità `managed` alla modalità `AP`:

```text
ssid SecurityGatewayLab
type AP
channel 6 (2437 MHz), width: 20 MHz
txpower 20.00 dBm
```

Il gateway è stato assegnato correttamente all'interfaccia hotspot:

```text
10.42.0.1/24
```

La route predefinita dell'host è rimasta sull'uplink MediaTek:

```text
1.1.1.1 via 192.168.10.1 dev wlp13s0 src 192.168.10.x
```

Durante il test sono risultate due stazioni Wi-Fi associate. Per entrambe `iw` ha mostrato:

```text
authorized: yes
authenticated: yes
associated: yes
```

Un client è comparso nella tabella dei vicini IPv4 come `REACHABLE` con indirizzo `10.42.0.143`. Una seconda voce IPv4 risultava `FAILED`, mentre `iw station dump` mostrava comunque una seconda stazione associata a livello Wi-Fi. Questo indica che l'associazione radio è riuscita, ma la risoluzione IPv4 della seconda voce non era confermata in quel momento.

## Prova grafica anonimizzata

![Verifica anonimizzata dei client associati all'hotspot](../images/03-hotspot-client-association.svg)

La figura è stata ricostruita dallo screenshot reale eliminando:

- indirizzi MAC dei client;
- nome completo dell'interfaccia `wlx...`;
- hostname e percorso del terminale;
- qualsiasi password.

## Significato tecnico del risultato

Il test conferma già che:

1. la Realtek può trasmettere come access point;
2. i client possono autenticarsi con la protezione configurata;
3. NetworkManager assegna la rete `10.42.0.0/24` all'hotspot;
4. almeno un client ha ricevuto un indirizzo IPv4 valido;
5. più stazioni possono associarsi contemporaneamente;
6. l'uplink dell'host continua a usare `wlp13s0`.

Non sono ancora considerati verificati:

- isolamento tra i client;
- accesso controllato alla rete domestica;
- navigazione Internet end-to-end;
- regole firewall definitive;
- persistenza dopo riavvio;
- rollback completo con eliminazione e ricreazione del profilo.

## Condizione di completamento

L'hotspot deve restare attivo, almeno un client deve collegarsi e raggiungere il gateway `10.42.0.1`, mentre l'uplink MediaTek continua a funzionare.

La navigazione Internet non è il criterio principale di questa fase: verrà verificata e documentata nella fase 4 insieme a DHCP, routing IPv4 e NAT.

## Rollback previsto

```bash
sudo nmcli connection down security-gateway-ap
sudo nmcli connection delete security-gateway-ap
```

Il primo comando disattiva l'hotspot. Il secondo elimina il profilo persistente da NetworkManager. Prima del test di rollback devono essere conservati localmente i parametri necessari per ricrearlo senza pubblicare il segreto WPA.

## Prossimo passo

1. verificare dal client la raggiungibilità di `10.42.0.1`;
2. verificare gateway e DNS ricevuti dal client;
3. verificare con cautela l'eventuale navigazione Internet;
4. documentare DHCP, routing IPv4 e NAT nella fase 4;
5. introdurre il firewall prima di considerare sicuro l'accesso verso altre reti.
