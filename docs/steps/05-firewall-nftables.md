# Fase 5 — Firewall con nftables

## Stato

```text
COMPLETATA E VERIFICATA — 17 luglio 2026
```

La fase è stata eseguita sul gateway Ubuntu fisico e verificata con un client reale collegato all'hotspot. Sono stati implementati:

- filtro stateful `FORWARD`;
- filtro `INPUT` limitato all'interfaccia hotspot;
- logging dei blocchi con rate limit;
- rollback delle sole tabelle del laboratorio;
- caricamento e reload tramite uno script amministrativo;
- servizio systemd dedicato;
- persistenza verificata con riavvio reale;
- coesistenza con NetworkManager, Docker e libvirt.

Due casi restano dichiarati come **non generati attivamente** durante questa fase:

- una nuova connessione proveniente da un secondo dispositivo dell'uplink verso un client dell'hotspot;
- traffico `ct state invalid` costruito appositamente.

Le relative regole sono presenti. Pacchetti `invalid` reali, in quantità molto bassa, sono stati osservati e bloccati durante riconnessioni e traffico normale. Il limite di prova attiva è documentato e non viene nascosto.

## Obiettivo

Proteggere Ubuntu e i dispositivi collegati all'hotspot consentendo soltanto:

- DHCP e DNS necessari al client;
- diagnostica ICMP verso il gateway;
- connessioni valide dal laboratorio verso Internet;
- risposte appartenenti a connessioni già esistenti;

bloccando invece:

- accessi non autorizzati ai servizi locali di Ubuntu;
- discovery locale non necessario sull'hotspot;
- inoltro dall'hotspot verso reti private Docker/libvirt o altre interfacce;
- nuove connessioni inoltrate dall'uplink verso i client;
- pacchetti classificati `invalid` sul percorso controllato.

## Valori pubblicabili

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
CLIENT_IP=10.42.0.x
HOTSPOT_PROFILE=security-gateway-ap
```

Il nome completo dell'interfaccia USB, gli indirizzi MAC, l'IP completo dell'host sull'uplink e i log integrali restano nei report privati locali.

## Ambiente verificato

```text
nftables:                     installato e funzionante
iptables backend:             nf_tables
nftables.service standard:    disabled / inactive
security-gateway-firewall:    enabled / active (exited)
UFW:                          inactive
firewalld:                    inactive
IPv4 forwarding:              1
hotspot NetworkManager:       avvio manuale
```

Il servizio standard `nftables.service` non viene usato perché `/etc/nftables.conf` contiene `flush ruleset` e l'unità standard usa anche `nft flush ruleset` durante lo stop. Questo potrebbe eliminare regole dinamiche appartenenti a NetworkManager, Docker e libvirt.

Il progetto usa invece un servizio dedicato che elimina e ricrea esclusivamente le proprie due tabelle.

## Componenti finali

```text
/etc/security-gateway-firewall/
├── security-gateway-input-filter.nft
└── security-gateway-filter.nft

/usr/local/sbin/security-gateway-firewall

/etc/systemd/system/security-gateway-firewall.service
```

Nel repository sono pubblicate versioni revisionate e parametrizzate:

```text
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
```

Prima dell'uso, il placeholder dell'interfaccia hotspot nei file pubblici deve essere sostituito con il nome reale ottenuto sul proprio sistema.

## Perché sono state usate tabelle separate

Le due tabelle del progetto sono:

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

La separazione permette di:

- verificare e rimuovere `INPUT` e `FORWARD` indipendentemente;
- evitare modifiche alle chain gestite da altri programmi;
- eseguire rollback precisi;
- mantenere leggibile il percorso dei pacchetti.

La policy delle base chain resta `accept` perché il progetto vuole controllare soltanto il traffico che coinvolge l'interfaccia hotspot. Le regole finali specifiche per tale interfaccia applicano il blocco effettivo.

## Concetti verificati

- una `table` contiene chain e regole;
- `hook input` vede pacchetti destinati direttamente a Ubuntu;
- `hook forward` vede pacchetti che Ubuntu deve inoltrare;
- una priorità più bassa viene eseguita prima;
- `counter` conta pacchetti e byte;
- `accept` termina la chain corrente, ma non elimina il controllo di altre base chain;
- `drop` scarta definitivamente il pacchetto;
- conntrack classifica i pacchetti come `new`, `established`, `related` o `invalid`;
- `log` registra senza accettare o bloccare da solo;
- `limit rate` protegge il journal da quantità eccessive di log;
- filtro e NAT sono funzioni distinte;
- un servizio systemd `oneshot` può caricare regole e terminare, mentre le regole restano nel kernel;
- `start` avvia un servizio nella sessione corrente, mentre `enable` lo collega all'avvio automatico.

## Inventario dei servizi locali

Prima del filtro `INPUT` è stato eseguito:

```bash
sudo ss -lntup
```

Servizi importanti osservati:

```text
10.42.0.1:53 TCP/UDP       dnsmasq, DNS hotspot
0.0.0.0:67 UDP             dnsmasq, DHCP hotspot
127.0.0.1:631 TCP          CUPS solo loopback
0.0.0.0:5353 UDP           Avahi/mDNS
UDP 3702                   wsdd/WS-Discovery
```

Il processo Python che usava UDP 3702 è stato identificato come `/usr/bin/wsdd`, integrato con GVFS per la discovery. Non è stato terminato o rimosso globalmente: il firewall blocca soltanto le richieste provenienti dall'interfaccia hotspot.

## Filtro INPUT implementato

Politica pubblica equivalente:

```nft
chain input_filter {
    type filter hook input priority -20; policy accept;

    iifname "<AP_IF>" udp sport 68 udp dport 67 counter accept
    iifname "<AP_IF>" ct state invalid counter drop
    iifname "<AP_IF>" ct state established,related counter accept

    iifname "<AP_IF>" ip saddr 10.42.0.0/24 \
        ip daddr 10.42.0.1 udp dport 53 counter accept

    iifname "<AP_IF>" ip saddr 10.42.0.0/24 \
        ip daddr 10.42.0.1 tcp dport 53 counter accept

    iifname "<AP_IF>" ip saddr 10.42.0.0/24 \
        ip daddr 10.42.0.1 ip protocol icmp counter accept

    iifname "<AP_IF>" udp dport 3702 counter drop
    iifname "<AP_IF>" udp dport 5353 counter drop

    iifname "<AP_IF>" \
        limit rate 5/minute burst 10 packets \
        counter log prefix "SGW_INPUT_DROP " level info

    iifname "<AP_IF>" counter drop
}
```

### Spiegazione delle regole INPUT

#### DHCP

```text
client UDP 68 -> server UDP 67
```

La destinazione IP non viene vincolata a `10.42.0.1` perché la prima richiesta DHCP può essere inviata in broadcast prima che il client possieda un indirizzo.

#### `invalid`

Pacchetti che conntrack non riesce ad associare a un flusso valido vengono scartati.

#### `established,related`

Permette risposte legittime a comunicazioni eventualmente iniziate dal gateway verso un dispositivo dell'hotspot.

#### DNS UDP e TCP

Il client può interrogare esclusivamente il DNS del gateway `10.42.0.1:53`. UDP è il caso normale; TCP è mantenuto per risposte grandi e fallback.

#### ICMP

Consente ping e diagnostica IPv4 dal laboratorio verso il gateway.

#### WS-Discovery e mDNS

UDP 3702 e UDP 5353 vengono bloccate sull'hotspot. Non sono necessarie per DHCP, DNS tradizionale o navigazione Internet.

#### Logging e blocco finale

La regola `log` non contiene un verdetto. Registra un numero limitato di pacchetti e li lascia proseguire verso la regola successiva, che esegue il `drop`.

## Test attivo INPUT

Dal client è stato aperto:

```text
http://10.42.0.1:631
```

La richiesta ha prodotto log equivalenti a:

```text
SGW_INPUT_DROP
IN=<AP_IF>
SRC=10.42.0.x
DST=10.42.0.1
PROTO=TCP
DPT=631
SYN
```

Il browser ha ritrasmesso lo stesso `SYN` perché non riceveva risposta. La porta sorgente è rimasta uguale, confermando che si trattava della stessa connessione e non di tentativi differenti.

Risultato:

```text
TCP 631 dal client verso Ubuntu: LOG + DROP
pagina CUPS:                     non raggiungibile
DHCP, DNS e Internet:            funzionanti
```

## Filtro FORWARD implementato

Politica pubblica equivalente:

```nft
chain forward_filter {
    type filter hook forward priority -20; policy accept;

    iifname "<AP_IF>" oifname "<UPLINK_IF>" \
        ct state invalid counter drop

    iifname "<UPLINK_IF>" oifname "<AP_IF>" \
        ct state invalid counter drop

    iifname "<AP_IF>" oifname "<UPLINK_IF>" \
        ip saddr 10.42.0.0/24 \
        ct state new,established,related counter accept

    iifname "<UPLINK_IF>" oifname "<AP_IF>" \
        ip daddr 10.42.0.0/24 \
        ct state established,related counter accept

    iifname "<UPLINK_IF>" oifname "<AP_IF>" ct state new \
        limit rate 5/minute burst 10 packets \
        counter log prefix "SGW_FWD_TO_AP_DROP " level info

    iifname "<UPLINK_IF>" oifname "<AP_IF>" \
        ct state new counter drop

    iifname "<AP_IF>" \
        limit rate 5/minute burst 10 packets \
        counter log prefix "SGW_FWD_FROM_AP_DROP " level info

    iifname "<AP_IF>" counter drop

    oifname "<AP_IF>" \
        limit rate 5/minute burst 10 packets \
        counter log prefix "SGW_FWD_TO_AP_DROP " level info

    oifname "<AP_IF>" counter drop
}
```

### Politica risultante

```text
hotspot -> uplink, connessioni valide       ACCEPT
uplink -> hotspot, risposte esistenti       ACCEPT
uplink -> hotspot, nuove connessioni        LOG + DROP
pacchetti invalidi sul percorso laboratorio DROP
hotspot -> altre interfacce                 LOG + DROP
altre interfacce -> hotspot                 LOG + DROP
traffico non collegato all'hotspot          invariato
```

## Test attivo FORWARD verso una rete privata

È stata verificata la rotta verso la rete libvirt:

```bash
ip route get 192.168.122.254
```

Il kernel ha indicato `virbr0`. Dal client è stato quindi aperto:

```text
http://192.168.122.254/
```

Il log ha mostrato un percorso equivalente a:

```text
SGW_FWD_FROM_AP_DROP
IN=<AP_IF>
OUT=virbr0
SRC=10.42.0.x
DST=192.168.122.254
PROTO=TCP
DPT=80
SYN
```

Risultato:

```text
hotspot -> Internet                 ACCEPT
hotspot -> rete privata libvirt     LOG + DROP
```

Questo test dimostra che il client non può usare il gateway per entrare nella rete privata delle macchine virtuali.

## Logging con rate limit

Le regole usano:

```nft
limit rate 5/minute burst 10 packets
```

Il `burst` consente una piccola raffica iniziale di log. Successivamente il rate limit riduce il numero di messaggi. Il limite riguarda soltanto il logging: la regola finale continua a contare e bloccare tutti i pacchetti corrispondenti.

Prefissi usati:

```text
SGW_INPUT_DROP
SGW_FWD_FROM_AP_DROP
SGW_FWD_TO_AP_DROP
```

Lettura dei log:

```bash
sudo journalctl -k -f |
grep --line-buffered -E \
'SGW_INPUT_DROP|SGW_FWD_FROM_AP_DROP|SGW_FWD_TO_AP_DROP'
```

## Controllo sintattico

Ogni file è stato controllato prima del caricamento:

```bash
sudo nft --check --file security-gateway-input-filter.nft
sudo nft --check --file security-gateway-filter.nft
```

Risultato verificato:

```text
INPUT check:   0
FORWARD check: 0
```

## Rollback verificato

Rollback del solo filtro `INPUT`:

```bash
sudo nft delete table inet security_gateway_input_filter
```

Rollback del solo filtro `FORWARD`:

```bash
sudo nft delete table inet security_gateway_filter
```

Le tabelle sono state eliminate, controllate come assenti e ricaricate. DHCP, DNS, NetworkManager, Docker e libvirt sono rimasti operativi.

Non usare:

```bash
sudo nft flush ruleset
```

## Script amministrativo

Lo script:

```text
/usr/local/sbin/security-gateway-firewall
```

supporta:

```text
load      sostituisce e carica le due tabelle
reload    ricarica le due tabelle
unload    elimina soltanto le due tabelle
```

Caratteristiche verificate:

- richiede privilegi root;
- usa percorsi assoluti;
- crea un batch temporaneo protetto sotto `/run`;
- aggiunge `delete table` soltanto se la tabella esiste;
- controlla il batch con `nft --check`;
- applica il batch soltanto dopo il controllo riuscito;
- non contiene `flush ruleset`;
- verifica la presenza delle due tabelle dopo il caricamento;
- non elimina chain NetworkManager, Docker o libvirt.

Test eseguiti:

```text
esecuzione senza sudo: rifiutata correttamente
load con sudo:         riuscito
reload:                riuscito
INPUT dopo reload:     presente
FORWARD dopo reload:   presente
```

## Servizio systemd dedicato

L'unità:

```text
/etc/systemd/system/security-gateway-firewall.service
```

usa:

```ini
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/sbin/security-gateway-firewall load
ExecReload=/usr/local/sbin/security-gateway-firewall reload
ExecStop=/usr/local/sbin/security-gateway-firewall unload
```

`active (exited)` è lo stato corretto: lo script termina dopo aver caricato le regole, mentre nftables continua a operare nel kernel.

La sezione:

```ini
[Install]
WantedBy=multi-user.target
```

permette l'abilitazione all'avvio con:

```bash
sudo systemctl enable security-gateway-firewall.service
```

## Persistenza verificata dopo riavvio

Dopo un riavvio reale sono stati verificati:

```text
security-gateway-firewall.service enabled
security-gateway-firewall.service active (exited)
ExecStart status=0/SUCCESS
INPUT presente
FORWARD presente
quattro regole di logging presenti
nftables.service standard disabled/inactive
```

Il journal del boot corrente mostrava:

```text
Starting security-gateway-firewall.service
Filtri security gateway caricati correttamente.
Finished security-gateway-firewall.service
```

L'hotspot è rimasto intenzionalmente manuale perché il profilo NetworkManager usa `connection.autoconnect=no`. Dopo l'avvio manuale dell'hotspot, il client ha ricevuto DHCP, ha usato DNS e ha navigato normalmente.

## Evidenza post-riavvio

Contatori osservati dopo l'avvio dell'hotspot e traffico reale:

```text
INPUT
DHCP UDP 68 -> 67                         2 pacchetti ACCEPT
DNS UDP verso 10.42.0.1                  10 pacchetti ACCEPT
mDNS UDP 5353                            17 pacchetti DROP
altro traffico diretto al gateway         1 pacchetto LOG + DROP

FORWARD
hotspot -> uplink valido               2244 pacchetti ACCEPT
uplink -> hotspot established/related  4494 pacchetti ACCEPT
invalid hotspot -> uplink                 2 pacchetti DROP
nuove connessioni uplink -> hotspot       0 pacchetti
altre reti coinvolgenti l'hotspot          0 pacchetti dopo reboot
```

I valori sono un'istantanea e cambiano con il traffico. La loro funzione è dimostrare che, dopo il riavvio, le regole caricate automaticamente hanno realmente elaborato pacchetti.

## Coesistenza verificata

Dopo `load`, `reload` e riavvio sono rimaste presenti:

```text
nm-sh-in-<AP_IF>
nm-sh-fw-<AP_IF>
DOCKER-USER
DOCKER-FORWARD
chain Docker aggiuntive
chain e reti libvirt
NAT/masquerading NetworkManager
```

La navigazione ha continuato a funzionare.

Gli avvisi:

```text
table ip filter is managed by iptables-nft, do not touch!
```

sono informativi: ricordano che quelle tabelle sono gestite da `iptables-nft`. Il progetto non le modifica direttamente.

## Problemi incontrati e lezioni apprese

### Hotspot apparentemente attivo ma client non collegabile

Il problema è stato risolto disattivando e riattivando il profilo NetworkManager. I log mostravano una disattivazione richiesta dall'utente, non un blocco nftables.

### Ricerca browser temporaneamente non funzionante

Il problema è scomparso riaprendo il browser. I contatori `INPUT` non mostravano blocchi corrispondenti. La causa era compatibile con una vecchia sessione TCP o QUIC dopo la riconnessione Wi-Fi.

### Script Python non trovava la regola finale

Il file nftables era stato salvato con una formattazione diversa da quella attesa. Lo script ha rifiutato la modifica senza alterare il file. È stato poi reso più robusto per riconoscere la regola su una o più righe.

### Variabili della shell perse

Chiudendo il terminale sono state perse variabili come `AP_IF`, ma le regole nftables sono rimaste nel kernel. Le variabili sono state ricostruite da NetworkManager e dalla route predefinita.

### Controllo testuale di `flush ruleset`

Un `grep` troppo generico ha trovato le parole dentro un commento dell'unità systemd. Non era presente alcun comando `flush ruleset`. La validazione systemd e il comportamento reale hanno confermato la correttezza dell'unità.

## Checklist finale

- [x] backup iniziale del ruleset;
- [x] osservazione senza blocchi;
- [x] filtro stateful `FORWARD`;
- [x] filtro `INPUT` del gateway;
- [x] DHCP consentito e verificato;
- [x] DNS UDP consentito e verificato;
- [x] DNS TCP previsto;
- [x] ICMP previsto;
- [x] mDNS bloccato e osservato;
- [x] WS-Discovery bloccato;
- [x] accesso TCP 631 al gateway testato e bloccato;
- [x] hotspot verso rete libvirt testato e bloccato;
- [x] Internet dal client consentito;
- [x] risposte Internet consentite tramite conntrack;
- [x] logging limitato verificato;
- [x] rollback `INPUT` verificato;
- [x] rollback `FORWARD` verificato;
- [x] reload verificato;
- [x] coesistenza NetworkManager verificata;
- [x] coesistenza Docker verificata;
- [x] coesistenza libvirt verificata;
- [x] servizio systemd dedicato;
- [x] servizio abilitato all'avvio;
- [x] riavvio reale e persistenza verificati;
- [ ] nuova connessione da un secondo host dell'uplink verso un client, non generata attivamente;
- [ ] pacchetto `invalid` costruito appositamente, non generato attivamente.

## Rollback completo del progetto firewall

Rimuovere le tabelle senza disabilitare il servizio:

```bash
sudo /usr/local/sbin/security-gateway-firewall unload
```

Disabilitare e fermare il servizio:

```bash
sudo systemctl disable --now security-gateway-firewall.service
```

Rimuovere unità, script e configurazioni installate:

```bash
sudo rm -f /etc/systemd/system/security-gateway-firewall.service
sudo rm -f /usr/local/sbin/security-gateway-firewall
sudo rm -rf /etc/security-gateway-firewall
sudo systemctl daemon-reload
```

Il profilo hotspot NetworkManager non viene eliminato da questi comandi.

## Manutenzione futura

Dopo una modifica ai file del progetto:

```bash
sudo nft --check --file configs/nftables/security-gateway-input-filter.nft
sudo nft --check --file configs/nftables/security-gateway-filter.nft
```

Installare le copie revisionate sotto `/etc`, quindi:

```bash
sudo systemctl reload security-gateway-firewall.service
```

Verificare sempre:

```bash
systemctl is-active security-gateway-firewall.service
sudo nft list table inet security_gateway_input_filter
sudo nft list table inet security_gateway_filter
```

## Risultato finale

Il gateway Ubuntu ora applica un firewall stateful persistente e limitato all'hotspot. Il client autorizzato può ottenere DHCP, usare il DNS locale e raggiungere Internet, mentre accessi non previsti al gateway e alle altre reti locali vengono bloccati e registrati con rate limit. Le regole di NetworkManager, Docker e libvirt continuano a coesistere con quelle del progetto.

## Prossimo passo

Passare alla fase 6: approfondire `tcpdump`, filtri BPF, catture limitate, salvataggio controllato, analisi e anonimizzazione.