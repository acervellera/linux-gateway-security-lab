# Fase 5 — Report privato finale firewall nftables

**Progetto:** Ubuntu Security Gateway Lab  
**Data verifica finale:** 17 luglio 2026  
**Gateway:** `pc-MS-7E26`  
**Stato:** **COMPLETATA E VERIFICATA, CON LIMITI DI TEST DICHIARATI**

> Documento privato. Contiene nomi reali delle interfacce e indirizzi della rete di laboratorio. Non pubblicarlo senza anonimizzazione.

## 1. Sintesi del risultato

Sul gateway Ubuntu fisico è stato realizzato un firewall stateful con `nftables` che:

- protegge i servizi locali di Ubuntu raggiungibili dall'hotspot;
- permette DHCP e DNS necessari ai client;
- permette connessioni valide dal laboratorio verso Internet;
- permette verso i client soltanto risposte `established,related`;
- blocca l'accesso dall'hotspot alle reti private laterali;
- registra i blocchi con rate limit;
- coesiste con NetworkManager, Docker e libvirt;
- può essere caricato, ricaricato e rimosso senza `flush ruleset`;
- viene caricato automaticamente tramite systemd;
- è stato verificato dopo un riavvio reale.

Il client autorizzato ha continuato a collegarsi, ricevere un indirizzo `10.42.0.x`, usare il DNS `10.42.0.1` e raggiungere Internet tramite `wlp13s0`.

## 2. Valori reali della sessione

```text
AP_IF=wlx00c0cab4ed2d
UPLINK_IF=wlp13s0
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
CLIENT_IP=10.42.0.162
HOTSPOT_PROFILE=security-gateway-ap
UPLINK_HOST_IP=192.168.10.115/24
UPLINK_ROUTER=192.168.10.1
LIBVIRT_TEST_NET=192.168.122.0/24
LIBVIRT_TEST_IP=192.168.122.254
```

Il nome completo della Realtek incorpora dati riconducibili al MAC. Nei file pubblici è sostituito da `wlx<REDACTED>` o `wlx<REPLACE_ME>`.

## 3. Situazione iniziale

```text
nftables.service standard: disabled / inactive
UFW:                       inactive
firewalld:                 inactive
iptables backend:          nf_tables
net.ipv4.ip_forward:       1
```

Il ruleset conteneva chain dinamiche di NetworkManager, Docker, libvirt e `iptables-nft`.

`/etc/nftables.conf` conteneva `flush ruleset` e l'unità standard usava anche:

```text
ExecStop=/usr/sbin/nft flush ruleset
```

Il servizio standard non è stato abilitato per evitare di eliminare regole appartenenti ad altri componenti.

## 4. Metodo di lavoro

```text
backup
→ osservazione con counter
→ filtro FORWARD
→ rollback/reload FORWARD
→ inventario porte
→ filtro INPUT
→ rollback/reload INPUT
→ logging limitato
→ test attivi
→ script amministrativo
→ servizio systemd
→ enable
→ reboot reale
→ verifica post-reboot
```

Non è mai stato usato:

```bash
sudo nft flush ruleset
```

## 5. Inventario dei servizi locali

Il comando `sudo ss -lntup` ha mostrato:

```text
10.42.0.1:53 TCP/UDP       dnsmasq, DNS hotspot
0.0.0.0:67 UDP             dnsmasq, DHCP hotspot
127.0.0.1:631 TCP          CUPS solo loopback
0.0.0.0:5353 UDP           Avahi/mDNS
UDP 3702                   wsdd/WS-Discovery
```

Il processo Python sulla porta 3702 è stato identificato come:

```text
python3 /usr/bin/wsdd --no-host --discovery --listen /run/user/1000/gvfsd/wsdd
```

Non è stato rimosso globalmente. Il firewall blocca soltanto UDP 3702 proveniente dall'hotspot.

## 6. Filtro INPUT

### Struttura

```text
table inet security_gateway_input_filter
chain input_filter
hook input
priority -20
policy accept
```

### Regole reali

```nft
iifname "wlx00c0cab4ed2d" udp sport 68 udp dport 67 counter accept
iifname "wlx00c0cab4ed2d" ct state invalid counter drop
iifname "wlx00c0cab4ed2d" ct state established,related counter accept

iifname "wlx00c0cab4ed2d" ip saddr 10.42.0.0/24     ip daddr 10.42.0.1 udp dport 53 counter accept

iifname "wlx00c0cab4ed2d" ip saddr 10.42.0.0/24     ip daddr 10.42.0.1 tcp dport 53 counter accept

iifname "wlx00c0cab4ed2d" ip saddr 10.42.0.0/24     ip daddr 10.42.0.1 ip protocol icmp counter accept

iifname "wlx00c0cab4ed2d" udp dport 3702 counter drop
iifname "wlx00c0cab4ed2d" udp dport 5353 counter drop

iifname "wlx00c0cab4ed2d"     limit rate 5/minute burst 10 packets     counter log prefix "SGW_INPUT_DROP " level info

iifname "wlx00c0cab4ed2d" counter drop
```

### Spiegazione

- **DHCP:** UDP 68→67; non viene imposto `ip daddr 10.42.0.1` perché la prima richiesta può essere broadcast.
- **invalid:** pacchetti non associabili a un flusso valido vengono scartati.
- **established,related:** consente risposte legittime già note a conntrack.
- **DNS:** il client può interrogare soltanto `10.42.0.1:53` TCP/UDP.
- **ICMP:** consente ping e diagnostica IPv4 verso il gateway.
- **3702 e 5353:** WS-Discovery e mDNS vengono bloccati dall'hotspot.
- **log finale:** registra senza produrre un verdetto.
- **drop finale:** blocca qualsiasi altro pacchetto diretto a Ubuntu e proveniente dall'AP.

## 7. Test INPUT reale

Dal telefono è stato aperto:

```text
http://10.42.0.1:631
```

Il kernel ha registrato:

```text
SGW_INPUT_DROP
IN=wlx00c0cab4ed2d
SRC=10.42.0.162
DST=10.42.0.1
PROTO=TCP
SPT=49885
DPT=631
SYN
```

Le righe ripetute avevano la stessa porta sorgente: erano ritrasmissioni dello stesso `SYN`.

Risultato:

```text
pagina CUPS:          non aperta
pacchetti test:       registrati e bloccati
DHCP:                 funzionante
DNS:                  funzionante
Internet:             funzionante
```

Contatori della prima prova:

```text
SGW_INPUT_DROP: 10 pacchetti / 640 byte
drop finale:    10 pacchetti / 640 byte
```

## 8. Filtro FORWARD

### Struttura

```text
table inet security_gateway_filter
chain forward_filter
hook forward
priority -20
policy accept
```

### Politica

```text
hotspot → uplink, connessioni valide       ACCEPT
uplink → hotspot, risposte esistenti       ACCEPT
uplink → hotspot, nuove connessioni        LOG + DROP
invalid sul percorso hotspot/uplink        DROP
hotspot → altre interfacce                 LOG + DROP
altre interfacce → hotspot                 LOG + DROP
traffico estraneo all'hotspot              invariato
```

### Regole reali principali

```nft
iifname "wlx00c0cab4ed2d" oifname "wlp13s0"     ct state invalid counter drop

iifname "wlp13s0" oifname "wlx00c0cab4ed2d"     ct state invalid counter drop

iifname "wlx00c0cab4ed2d" oifname "wlp13s0"     ip saddr 10.42.0.0/24     ct state new,established,related counter accept

iifname "wlp13s0" oifname "wlx00c0cab4ed2d"     ip daddr 10.42.0.0/24     ct state established,related counter accept

iifname "wlp13s0" oifname "wlx00c0cab4ed2d"     ct state new limit rate 5/minute burst 10 packets     counter log prefix "SGW_FWD_TO_AP_DROP " level info

iifname "wlp13s0" oifname "wlx00c0cab4ed2d"     ct state new counter drop

iifname "wlx00c0cab4ed2d"     limit rate 5/minute burst 10 packets     counter log prefix "SGW_FWD_FROM_AP_DROP " level info

iifname "wlx00c0cab4ed2d" counter drop

oifname "wlx00c0cab4ed2d"     limit rate 5/minute burst 10 packets     counter log prefix "SGW_FWD_TO_AP_DROP " level info

oifname "wlx00c0cab4ed2d" counter drop
```

## 9. Test FORWARD verso libvirt

La route verso `192.168.122.254` indicava `virbr0`.

Dal telefono è stato aperto:

```text
http://192.168.122.254/
```

Log osservato:

```text
SGW_FWD_FROM_AP_DROP
IN=wlx00c0cab4ed2d
OUT=virbr0
SRC=10.42.0.162
DST=192.168.122.254
PROTO=TCP
SPT=49991
DPT=80
SYN
TTL=63
```

Risultato:

```text
hotspot → Internet:             consentito
hotspot → rete privata libvirt: registrato e bloccato
```

Contatori:

```text
SGW_FWD_FROM_AP_DROP: 10 pacchetti / 640 byte
drop da AP:            10 pacchetti / 640 byte
```

## 10. Logging con rate limit

```nft
limit rate 5/minute burst 10 packets
```

Il limite protegge il journal. Non limita il numero di pacchetti bloccati: quelli oltre la soglia non vengono registrati, ma raggiungono comunque il drop finale.

Prefissi:

```text
SGW_INPUT_DROP
SGW_FWD_FROM_AP_DROP
SGW_FWD_TO_AP_DROP
```

Monitoraggio:

```bash
sudo journalctl -k -f |
grep --line-buffered -E 'SGW_INPUT_DROP|SGW_FWD_FROM_AP_DROP|SGW_FWD_TO_AP_DROP'
```

## 11. Controlli, rollback e reload

Controlli sintattici:

```bash
sudo nft --check --file reports/phase-05/security-gateway-input-filter.nft
sudo nft --check --file reports/phase-05/security-gateway-filter.nft
```

Risultati:

```text
INPUT check:   0
FORWARD check: 0
```

Rollback preciso:

```bash
sudo nft delete table inet security_gateway_input_filter
sudo nft delete table inet security_gateway_filter
```

Le tabelle sono state eliminate e ricaricate senza interrompere NetworkManager, Docker o libvirt.

## 12. Script amministrativo

Percorso:

```text
/usr/local/sbin/security-gateway-firewall
```

Azioni:

```text
load
reload
unload
```

Funzionamento:

1. richiede root;
2. usa `/usr/sbin/nft`;
3. crea un batch protetto in `/run`;
4. elimina soltanto le tabelle del progetto se esistono;
5. aggiunge INPUT e FORWARD;
6. controlla con `nft --check`;
7. applica il batch;
8. verifica che le due tabelle siano presenti;
9. elimina il file temporaneo con `trap`.

Test senza sudo:

```text
ERRORE: lo script deve essere eseguito come root.
```

Test con sudo:

```text
Filtri security gateway caricati correttamente.
```

Dopo il caricamento erano ancora presenti:

```text
nm-sh-in-wlx00c0cab4ed2d
nm-sh-fw-wlx00c0cab4ed2d
DOCKER-USER
DOCKER-FORWARD
```

## 13. Servizio systemd

Percorso:

```text
/etc/systemd/system/security-gateway-firewall.service
```

Direttive:

```ini
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/sbin/security-gateway-firewall load
ExecReload=/usr/local/sbin/security-gateway-firewall reload
ExecStop=/usr/local/sbin/security-gateway-firewall unload
WantedBy=multi-user.target
```

`active (exited)` è corretto: lo script termina dopo aver caricato le regole, mentre le regole restano nel kernel.

Verifica unità:

```text
systemd-analyze verify: 0
ExecStart: status=0/SUCCESS
ExecReload: status=0/SUCCESS
```

## 14. Persistenza dopo reboot

Il servizio è stato abilitato con:

```bash
sudo systemctl enable security-gateway-firewall.service
```

Dopo un riavvio reale:

```text
Loaded: enabled
Active: active (exited)
ExecStart: status=0/SUCCESS
INPUT: presente
FORWARD: presente
nftables.service standard: disabled/inactive
```

Journal:

```text
Starting security-gateway-firewall.service
Filtri security gateway caricati correttamente.
Finished security-gateway-firewall.service
```

L'hotspot non parte automaticamente perché `connection.autoconnect=no`. È stato avviato manualmente con:

```bash
sudo nmcli connection up "security-gateway-ap"
```

## 15. Evidenza post-reboot

### INPUT

```text
DHCP UDP 68 → 67:                    2 pacchetti / 656 byte ACCEPT
DNS UDP:                            10 pacchetti / 642 byte ACCEPT
mDNS UDP 5353:                      17 pacchetti / 1539 byte DROP
SGW_INPUT_DROP:                      1 pacchetto / 32 byte LOG
drop finale:                         1 pacchetto / 32 byte DROP
```

### FORWARD

```text
invalid AP → uplink:                  2 pacchetti / 1275 byte DROP
AP → uplink valido:                2244 pacchetti / 461190 byte ACCEPT
uplink → AP established/related:   4494 pacchetti / 4736404 byte ACCEPT
```

La crescita dei contatori dimostra che le regole caricate automaticamente hanno elaborato traffico reale.

## 16. Problemi e lezioni apprese

### Hotspot non riconnettibile

I log mostravano `reason: user-requested`. Il profilo è stato disattivato e riattivato. Non era un blocco nftables.

### Browser e cronologia Google

Il problema è scomparso riaprendo il browser. I contatori non mostravano un blocco corrispondente; era compatibile con una vecchia sessione TCP/QUIC.

### Script Python e formattazione

Uno script cercava una regola multilinea, mentre il file reale la conteneva su una riga. Lo script ha terminato senza modificare il file. La ricerca è stata resa più robusta.

### `AP_IF` vuota

Dopo la chiusura della shell la variabile non esisteva più. Lo script ha rifiutato la modifica. La variabile è stata ricostruita da NetworkManager.

### `awk` e handle 6

L'handle esisteva, ma l'estrazione con `awk` spezzata su più righe è fallita. La ricerca è stata corretta e ha prodotto:

```text
NEW_TO_AP_HANDLE=6
FROM_AP_HANDLE=7
TO_AP_HANDLE=8
```

### Falso allarme `flush ruleset`

`grep` ha trovato le parole in un commento. Non era presente alcun comando globale di flush.

## 17. Limiti dichiarati

Non sono stati generati attivamente:

1. una nuova connessione da un secondo host dell'uplink verso un client hotspot;
2. un pacchetto `ct state invalid` costruito appositamente.

Le relative regole sono presenti. Pochi pacchetti reali `invalid` sono stati osservati e bloccati. Questi due test potranno essere ripresi nella fase 11.

## 18. Checklist finale

```text
[x] backup iniziale
[x] osservazione con counter
[x] filtro FORWARD
[x] filtro INPUT
[x] DHCP
[x] DNS UDP
[x] DNS TCP previsto
[x] ICMP previsto
[x] mDNS bloccato
[x] WS-Discovery bloccato
[x] test TCP 631
[x] test hotspot → libvirt
[x] logging INPUT
[x] logging FORWARD
[x] rate limit
[x] rollback INPUT
[x] rollback FORWARD
[x] load e reload
[x] NetworkManager conservato
[x] Docker conservato
[x] libvirt conservato
[x] script amministrativo
[x] servizio systemd
[x] enable
[x] reboot reale
[x] DHCP/DNS/Internet dopo reboot
[ ] test attivo da secondo host uplink
[ ] generazione controllata invalid
```

## 19. Rollback completo

```bash
sudo systemctl disable --now security-gateway-firewall.service

sudo nft delete table inet security_gateway_input_filter
sudo nft delete table inet security_gateway_filter

sudo rm -f /etc/systemd/system/security-gateway-firewall.service
sudo rm -f /usr/local/sbin/security-gateway-firewall
sudo rm -rf /etc/security-gateway-firewall
sudo systemctl daemon-reload
```

Il profilo NetworkManager `security-gateway-ap` non viene eliminato.

## 20. File repository aggiornati

Branch:

```text
agent/reorganize-ubuntu-security-gateway-lab
```

File collegati:

```text
README.md
docs/README.md
docs/00-ROADMAP.md
docs/02-STATO-ATTUALE.md
docs/LAVORO_SVOLTO_E_PROSSIMI_PASSI.md
docs/steps/05-firewall-nftables.md
samples/README.md
samples/reports/phase-05-forward-filter-checkpoint.md
samples/reports/phase-05-firewall-nftables-final.md
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
```

## 21. Conclusione

La fase 5 ha prodotto un firewall reale, testato, persistente e documentato. Il gateway consente i servizi necessari e Internet, blocca accessi non previsti a Ubuntu e alle reti laterali, registra i blocchi senza saturare il journal e non sostituisce le regole dinamiche degli altri servizi.

La fase successiva è la fase 6: `tcpdump`, filtri BPF, catture limitate, PCAP, confronto tra interfacce e anonimizzazione.
