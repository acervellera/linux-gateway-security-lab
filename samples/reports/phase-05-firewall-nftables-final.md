# Fase 5 — Report finale firewall nftables

Data verifica finale: 17 luglio 2026.

## Stato

```text
COMPLETATA E VERIFICATA
```

Questo report pubblico documenta i test effettivamente eseguiti sul gateway Ubuntu fisico. Nomi completi delle interfacce, indirizzi MAC, IP locali completi dell'host, screenshot originali e log integrali sono stati esclusi.

## Ambiente anonimizzato

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
CLIENT_IP=10.42.0.x
HOTSPOT_PROFILE=security-gateway-ap
```

Componenti del sistema:

```text
NetworkManager: gestisce hotspot, DHCP, DNS, forwarding e NAT
Docker:         conserva le proprie chain DOCKER-*
libvirt:        conserva bridge e regole delle reti virtuali
nftables:       ospita le due tabelle del progetto
systemd:        carica automaticamente il firewall dedicato
```

## Tabelle del progetto

```text
table inet security_gateway_input_filter
    hook input
    priority -20
    policy accept

table inet security_gateway_filter
    hook forward
    priority -20
    policy accept
```

Le chain hanno policy `accept` per non interferire con traffico non collegato all'hotspot. I blocchi finali si applicano esplicitamente ai pacchetti che entrano o escono dall'interfaccia AP.

## Politica INPUT verificata

```text
DHCP client UDP 68 -> server UDP 67            ACCEPT
DNS UDP/TCP dal laboratorio a 10.42.0.1:53    ACCEPT
ICMP dal laboratorio al gateway                ACCEPT
established,related dall'AP                    ACCEPT
invalid dall'AP                                DROP
WS-Discovery UDP 3702 dall'AP                  DROP
mDNS UDP 5353 dall'AP                          DROP
altro traffico dall'AP verso Ubuntu            LOG + DROP
```

### Test attivo INPUT

Dal client è stata richiesta la porta CUPS del gateway:

```text
http://10.42.0.1:631
```

Il kernel ha registrato pacchetti equivalenti a:

```text
SGW_INPUT_DROP
IN=wlx<REDACTED>
SRC=10.42.0.x
DST=10.42.0.1
PROTO=TCP
DPT=631
SYN
```

Il browser ha ritrasmesso lo stesso tentativo TCP perché non riceveva risposta. La pagina non si è aperta.

Durante lo stesso periodo:

- DHCP ha continuato a funzionare;
- DNS ha continuato a funzionare;
- la navigazione Internet ha continuato a funzionare;
- i pacchetti mDNS sono stati contati e bloccati.

## Politica FORWARD verificata

```text
hotspot -> uplink, new/established/related  ACCEPT
uplink -> hotspot, established/related      ACCEPT
uplink -> hotspot, new                      LOG + DROP
invalid hotspot/uplink                      DROP
hotspot -> altre interfacce                 LOG + DROP
altre interfacce -> hotspot                 LOG + DROP
traffico non collegato all'hotspot          invariato
```

### Test attivo verso rete libvirt

È stata verificata la route:

```text
192.168.122.254 -> virbr0
```

Dal client è stato aperto:

```text
http://192.168.122.254/
```

Il kernel ha registrato un evento equivalente a:

```text
SGW_FWD_FROM_AP_DROP
IN=wlx<REDACTED>
OUT=virbr0
SRC=10.42.0.x
DST=192.168.122.254
PROTO=TCP
DPT=80
SYN
```

La pagina non si è aperta. Un normale sito Internet ha continuato a funzionare tramite l'uplink autorizzato.

## Logging con rate limit

Prefissi:

```text
SGW_INPUT_DROP
SGW_FWD_FROM_AP_DROP
SGW_FWD_TO_AP_DROP
```

Limite applicato:

```text
limit rate 5/minute burst 10 packets
```

La regola di log non contiene un verdetto. Il pacchetto prosegue verso la successiva regola `drop`. Il rate limit riduce i messaggi del kernel, ma tutti i pacchetti che raggiungono il blocco finale vengono comunque scartati.

## Rollback e reload

Sono stati provati:

```text
eliminazione della sola tabella INPUT
eliminazione della sola tabella FORWARD
ricontrollo sintattico dei file
ricaricamento delle tabelle
reload tramite servizio systemd
```

Dopo rollback e reload sono rimasti presenti:

```text
nm-sh-in-<AP_IF>
nm-sh-fw-<AP_IF>
DOCKER-USER
DOCKER-FORWARD
altre chain Docker
bridge e reti libvirt
NAT/masquerading NetworkManager
```

Non è stato usato `nft flush ruleset`.

## Persistenza

Il servizio standard `nftables.service` è rimasto:

```text
disabled
inactive
```

È stato creato un servizio dedicato:

```text
security-gateway-firewall.service
```

Stato verificato:

```text
enabled
active (exited)
ExecStart status=0/SUCCESS
ExecReload status=0/SUCCESS
```

Il servizio esegue uno script che:

- accetta `load`, `reload` e `unload`;
- richiede privilegi root;
- crea un batch temporaneo protetto;
- elimina soltanto le due tabelle del progetto se esistono;
- controlla il batch con `nft --check`;
- applica il batch soltanto dopo il controllo riuscito;
- verifica che INPUT e FORWARD siano presenti dopo il caricamento.

## Test dopo riavvio reale

Dopo il riavvio sono stati verificati:

```text
servizio dedicato enabled
servizio dedicato active (exited)
tabella INPUT presente
tabella FORWARD presente
quattro regole di logging presenti
servizio nftables standard ancora disabled/inactive
```

L'hotspot è stato avviato manualmente, come previsto da `connection.autoconnect=no`.

Contatori osservati dopo traffico reale:

```text
INPUT
DHCP UDP 68 -> 67                         2 pacchetti ACCEPT
DNS UDP verso il gateway                 10 pacchetti ACCEPT
mDNS UDP 5353                            17 pacchetti DROP
altro traffico diretto al gateway         1 pacchetto LOG + DROP

FORWARD
hotspot -> uplink valido               2244 pacchetti ACCEPT
uplink -> hotspot established/related  4494 pacchetti ACCEPT
invalid hotspot -> uplink                 2 pacchetti DROP
```

I contatori sono un'istantanea e cambiano con il traffico. Dimostrano che le regole caricate automaticamente dopo il reboot hanno realmente elaborato pacchetti.

## Problemi incontrati

### Hotspot disattivato manualmente

I log NetworkManager mostravano `reason: user-requested`. La causa non era il firewall. Riattivando il profilo, DHCP ha completato nuovamente la sequenza completa.

### Browser temporaneamente bloccato dopo riconnessione

Il problema è scomparso riaprendo il browser. I contatori non indicavano blocchi del firewall; il comportamento era compatibile con una sessione TCP/QUIC precedente.

### Formattazione del file nftables

Uno script Python non ha trovato una regola perché cercava una formattazione multilinea precisa. Ha terminato senza modificare il file. La ricerca è stata resa più robusta e la modifica è stata poi verificata con `diff` e `nft --check`.

### Variabili shell perse

La chiusura dei terminali ha eliminato variabili come `AP_IF`, ma non le regole nel kernel. Le variabili sono state ricostruite da NetworkManager e dalla route predefinita.

## Risultati verificati

- [x] client verso gateway limitato ai servizi previsti;
- [x] DHCP consentito;
- [x] DNS consentito;
- [x] navigazione Internet consentita;
- [x] risposte Internet consentite tramite connessione esistente;
- [x] accesso TCP 631 al gateway bloccato;
- [x] accesso dall'hotspot alla rete libvirt bloccato;
- [x] logging INPUT verificato;
- [x] logging FORWARD verificato;
- [x] rate limit configurato;
- [x] rollback INPUT verificato;
- [x] rollback FORWARD verificato;
- [x] reload verificato;
- [x] coesistenza con NetworkManager verificata;
- [x] coesistenza con Docker verificata;
- [x] coesistenza con libvirt verificata;
- [x] servizio systemd dedicato verificato;
- [x] persistenza dopo reboot verificata;
- [ ] nuova connessione da un secondo host dell'uplink verso il client non generata attivamente;
- [ ] traffico `invalid` costruito appositamente non generato attivamente.

## File pubblici collegati

```text
docs/steps/05-firewall-nftables.md
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
```

## Risultato finale

Il gateway applica un firewall stateful persistente senza sostituire il ruleset globale. Il client autorizzato può ottenere configurazione di rete e raggiungere Internet, mentre gli accessi non previsti al gateway e alle reti private laterali vengono bloccati e registrati con un limite controllato.