# Fase 5 — Report pubblico firewall nftables

**Data della verifica finale:** 17 luglio 2026  
**Stato:** **COMPLETATA E VERIFICATA**

Questo report documenta il firewall realmente costruito e provato sul gateway Ubuntu fisico. Nomi completi delle interfacce, indirizzi MAC, IP locali completi dell'host, screenshot originali e log integrali sono stati rimossi.

## 1. Obiettivo della fase

Proteggere Ubuntu e i dispositivi collegati all'hotspot consentendo soltanto il traffico necessario:

- DHCP per ottenere la configurazione di rete;
- DNS verso il gateway;
- ICMP per diagnostica controllata;
- connessioni valide dal laboratorio verso Internet;
- risposte appartenenti a connessioni già esistenti.

Il firewall deve invece bloccare:

- accessi non autorizzati ai servizi locali di Ubuntu;
- discovery locale non necessario proveniente dall'hotspot;
- inoltro dall'hotspot verso reti private Docker, libvirt o altre interfacce;
- nuove connessioni inoltrate dall'uplink verso i client;
- pacchetti classificati `invalid` sul percorso controllato.

## 2. Architettura verificata

```text
Client autorizzato 10.42.0.x
        |
        v
Realtek USB in modalità AP
        |
        v
Ubuntu gateway 10.42.0.1
        |-- filtro INPUT
        |-- filtro FORWARD
        |-- logging limitato
        |-- NAT NetworkManager
        v
MediaTek wlp13s0
        |
        v
Internet
```

Valori pubblicabili:

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
CLIENT_IP=10.42.0.x
HOTSPOT_PROFILE=security-gateway-ap
```

## 3. Ambiente e coesistenza

Componenti presenti durante i test:

```text
NetworkManager  hotspot, DHCP, DNS, forwarding e NAT
Docker          chain DOCKER-*
libvirt         bridge e reti virtuali
nftables        tabelle del progetto
systemd         caricamento automatico del firewall
```

Stato finale:

```text
nftables.service standard:         disabled / inactive
security-gateway-firewall.service: enabled / active (exited)
UFW:                               inactive
firewalld:                         inactive
IPv4 forwarding:                   1
hotspot NetworkManager:            avvio manuale
```

Il servizio standard `nftables.service` non è stato usato perché la configurazione predefinita conteneva `flush ruleset`. Un flush globale avrebbe potuto eliminare regole dinamiche appartenenti a NetworkManager, Docker e libvirt.

## 4. Metodo di lavoro

La fase è stata costruita in modo incrementale:

```text
backup del ruleset
        ↓
osservazione con soli counter
        ↓
filtro FORWARD
        ↓
rollback e reload FORWARD
        ↓
inventario delle porte locali
        ↓
filtro INPUT
        ↓
rollback e reload INPUT
        ↓
logging con rate limit
        ↓
test attivi dei blocchi
        ↓
script amministrativo
        ↓
servizio systemd
        ↓
riavvio reale
```

Non è mai stato usato:

```bash
sudo nft flush ruleset
```

## 5. Tabelle del progetto

Sono state usate due tabelle separate:

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

- studiare separatamente traffico locale e traffico inoltrato;
- eseguire rollback precisi;
- evitare modifiche alle chain gestite da altri programmi;
- ricaricare soltanto le tabelle del laboratorio.

La policy delle base chain resta `accept` per non cambiare traffico estraneo all'hotspot. Le regole finali applicano il blocco esplicitamente all'interfaccia AP.

## 6. Inventario dei servizi locali

Prima del filtro `INPUT` è stato eseguito:

```bash
sudo ss -lntup
```

Servizi importanti osservati:

```text
10.42.0.1:53/tcp e udp   dnsmasq, DNS hotspot
0.0.0.0:67/udp           dnsmasq, DHCP hotspot
127.0.0.1:631/tcp        CUPS solo loopback
0.0.0.0:5353/udp         Avahi/mDNS
UDP 3702                 wsdd/WS-Discovery
```

Il processo Python associato a UDP 3702 è stato identificato come `/usr/bin/wsdd`, integrato con GVFS. Non è stato terminato globalmente: il firewall limita soltanto le richieste provenienti dall'hotspot.

## 7. Filtro INPUT

### Politica

```text
DHCP client UDP 68 → server UDP 67          ACCEPT
DNS UDP/TCP verso 10.42.0.1:53              ACCEPT
ICMP dal laboratorio verso il gateway       ACCEPT
established,related proveniente dall'AP      ACCEPT
invalid proveniente dall'AP                  DROP
WS-Discovery UDP 3702                        DROP
mDNS UDP 5353                                DROP
altro traffico dall'AP verso Ubuntu          LOG + DROP
```

### Regole pubbliche equivalenti

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

### Perché DHCP non vincola la destinazione IP

La prima richiesta DHCP può essere inviata in broadcast prima che il client possieda un indirizzo. Una regola che imponesse subito `ip daddr 10.42.0.1` potrebbe bloccare il bootstrap.

### DNS UDP e TCP

UDP è il percorso comune. TCP è mantenuto per risposte grandi, fallback o altre condizioni previste dal protocollo.

### Logging e blocco finale

La regola `log` non contiene `accept` o `drop`. Registra il pacchetto e lo lascia proseguire verso la regola successiva, che lo blocca.

## 8. Test attivo INPUT

Dal telefono è stato aperto:

```text
http://10.42.0.1:631
```

Il kernel ha prodotto eventi equivalenti a:

```text
SGW_INPUT_DROP
IN=wlx<REDACTED>
SRC=10.42.0.x
DST=10.42.0.1
PROTO=TCP
DPT=631
SYN
```

La stessa porta sorgente è comparsa più volte perché TCP ha ritrasmesso il medesimo `SYN` in assenza di risposta.

Risultato:

```text
pagina CUPS:                    non aperta
pacchetti:                      registrati e bloccati
DHCP:                           funzionante
DNS:                            funzionante
navigazione Internet:           funzionante
```

Durante una prova i contatori mostravano:

```text
SGW_INPUT_DROP: 10 pacchetti / 640 byte
blocco finale:  10 pacchetti / 640 byte
```

I valori uguali dimostrano che i pacchetti registrati sono poi arrivati al `drop` finale.

## 9. Filtro FORWARD

### Politica

```text
hotspot → uplink, new/established/related  ACCEPT
uplink → hotspot, established/related      ACCEPT
uplink → hotspot, new                      LOG + DROP
invalid sul percorso hotspot/uplink        DROP
hotspot → altre interfacce                 LOG + DROP
altre interfacce → hotspot                 LOG + DROP
traffico non collegato all'hotspot         invariato
```

### Regole pubbliche equivalenti

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

## 10. Test attivo verso la rete libvirt

Il comando:

```bash
ip route get 192.168.122.254
```

ha indicato:

```text
virbr0
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

Il test non era diretto a Internet. `192.168.122.0/24` è una rete privata libvirt collegata a `virbr0`.

Risultato:

```text
hotspot → Internet:             consentito
hotspot → rete privata libvirt: registrato e bloccato
```

Contatori osservati:

```text
SGW_FWD_FROM_AP_DROP: 10 pacchetti / 640 byte
blocco da AP:          10 pacchetti / 640 byte
```

## 11. Logging con rate limit

Prefissi configurati:

```text
SGW_INPUT_DROP
SGW_FWD_FROM_AP_DROP
SGW_FWD_TO_AP_DROP
```

Limite:

```nft
limit rate 5/minute burst 10 packets
```

Il `burst` permette una piccola raffica iniziale. Successivamente il journal riceve un numero limitato di messaggi.

Il rate limit riguarda i log, non il blocco: i pacchetti che superano il limite possono non essere registrati, ma la regola finale continua a scartarli.

Monitoraggio:

```bash
sudo journalctl -k -f |
grep --line-buffered -E \
'SGW_INPUT_DROP|SGW_FWD_FROM_AP_DROP|SGW_FWD_TO_AP_DROP'
```

## 12. Controllo sintattico

Prima di ogni caricamento sono stati eseguiti controlli equivalenti a:

```bash
sudo nft --check --file security-gateway-input-filter.nft
sudo nft --check --file security-gateway-filter.nft
```

Risultato:

```text
INPUT check:   0
FORWARD check: 0
```

`0` è il codice di uscita che indica il completamento corretto del controllo.

## 13. Rollback verificato

Rimozione del solo filtro INPUT:

```bash
sudo nft delete table inet security_gateway_input_filter
```

Rimozione del solo filtro FORWARD:

```bash
sudo nft delete table inet security_gateway_filter
```

Dopo il rollback:

- le tabelle del progetto risultavano assenti;
- DHCP e DNS NetworkManager restavano operativi;
- le chain Docker restavano presenti;
- le reti libvirt restavano presenti;
- i file sono stati ricontrollati e ricaricati;
- i contatori sono ripartiti da zero.

## 14. Script amministrativo

Percorso installato sul gateway:

```text
/usr/local/sbin/security-gateway-firewall
```

Azioni:

```text
load      carica o sostituisce le tabelle
reload    ricarica le tabelle
unload    elimina soltanto le tabelle del progetto
```

Lo script:

1. richiede privilegi root;
2. verifica il comando `nft`;
3. crea un batch temporaneo protetto sotto `/run`;
4. inserisce `delete table` soltanto per le tabelle del progetto già esistenti;
5. aggiunge le configurazioni INPUT e FORWARD;
6. controlla tutto con `nft --check`;
7. applica il batch;
8. verifica la presenza delle tabelle;
9. elimina il file temporaneo tramite `trap`.

Test senza `sudo`:

```text
ERRORE: lo script deve essere eseguito come root.
```

Test con `sudo`:

```text
Filtri security gateway caricati correttamente.
```

## 15. Servizio systemd

Unità installata:

```text
/etc/systemd/system/security-gateway-firewall.service
```

Direttive principali:

```ini
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/sbin/security-gateway-firewall load
ExecReload=/usr/local/sbin/security-gateway-firewall reload
ExecStop=/usr/local/sbin/security-gateway-firewall unload
WantedBy=multi-user.target
```

Significato:

- `Type=oneshot`: esegue una operazione e termina;
- `RemainAfterExit=yes`: mantiene lo stato `active (exited)` dopo il successo;
- `ExecStart`: carica il firewall;
- `ExecReload`: ricarica il firewall;
- `ExecStop`: rimuove soltanto le due tabelle;
- `WantedBy=multi-user.target`: permette l'avvio automatico.

Il servizio è stato verificato con:

```bash
sudo systemd-analyze verify \
    /etc/systemd/system/security-gateway-firewall.service
```

Risultato:

```text
0
```

## 16. Persistenza dopo un riavvio reale

Il servizio è stato abilitato:

```bash
sudo systemctl enable security-gateway-firewall.service
```

Dopo il riavvio:

```text
security-gateway-firewall.service: enabled
stato:                            active (exited)
ExecStart:                        status=0/SUCCESS
INPUT:                            presente
FORWARD:                          presente
nftables.service standard:        disabled / inactive
```

Il journal del boot mostrava:

```text
Starting security-gateway-firewall.service
Filtri security gateway caricati correttamente.
Finished security-gateway-firewall.service
```

L'hotspot è rimasto ad avvio manuale perché il profilo usa:

```text
connection.autoconnect=no
```

Il firewall era già presente prima dell'attivazione manuale dell'hotspot.

## 17. Contatori post-reboot

Dopo la connessione del telefono sono stati osservati:

```text
INPUT
DHCP UDP 68 → 67                         2 pacchetti ACCEPT
DNS UDP verso il gateway                10 pacchetti ACCEPT
mDNS UDP 5353                           17 pacchetti DROP
altro traffico verso Ubuntu              1 pacchetto LOG + DROP

FORWARD
hotspot → uplink valido               2244 pacchetti ACCEPT
uplink → hotspot established/related  4494 pacchetti ACCEPT
invalid hotspot → uplink                 2 pacchetti DROP
```

I contatori sono una istantanea e cambiano con il traffico. Dimostrano che il ruleset caricato automaticamente ha elaborato pacchetti reali.

## 18. Problemi incontrati

### Hotspot disattivato manualmente

I log NetworkManager indicavano `reason: user-requested`. La causa non era il firewall. Dopo la riattivazione DHCP ha completato nuovamente la sequenza completa.

### Browser temporaneamente bloccato

Una pagina della cronologia non si apriva dopo una riconnessione. Il problema è scomparso riaprendo il browser. I contatori non indicavano un blocco del firewall; il comportamento era compatibile con una vecchia sessione TCP o QUIC.

### Formattazione del file nftables

Uno script Python cercava una regola in un formato multilinea troppo preciso. Ha terminato senza modificare il file. La ricerca è stata resa più robusta e la modifica è stata poi verificata con `diff` e `nft --check`.

### Variabili shell perse

La chiusura del terminale ha eliminato variabili come `AP_IF`, ma non le regole nel kernel. Le variabili sono state ricostruite da NetworkManager e dalla route predefinita.

### Estrazione dell'handle

Una chiamata `awk index()` spezzata su più righe non era accettata dalla versione usata. La regola esisteva; era fallita soltanto l'estrazione automatica dell'handle.

### Falso allarme sul flush

Un `grep` ha trovato la frase `flush ruleset` dentro un commento che spiegava di non usarlo. L'unità non conteneva un comando globale di flush.

## 19. Limiti dichiarati

Non sono stati generati attivamente:

- una nuova connessione proveniente da un secondo host dell'uplink verso un client hotspot;
- un pacchetto `ct state invalid` costruito appositamente.

Le regole corrispondenti sono presenti. Pochi pacchetti `invalid` reali sono stati osservati e bloccati, ma non vengono presentati come test controllato.

## 20. Checklist finale

- [x] backup iniziale;
- [x] osservazione con counter;
- [x] filtro INPUT;
- [x] filtro FORWARD;
- [x] DHCP consentito;
- [x] DNS TCP/UDP consentito;
- [x] ICMP previsto;
- [x] mDNS bloccato;
- [x] WS-Discovery bloccato;
- [x] test TCP 631;
- [x] test verso rete libvirt;
- [x] logging INPUT;
- [x] logging FORWARD;
- [x] rate limit;
- [x] rollback INPUT;
- [x] rollback FORWARD;
- [x] reload;
- [x] coesistenza NetworkManager;
- [x] coesistenza Docker;
- [x] coesistenza libvirt;
- [x] script amministrativo;
- [x] servizio systemd;
- [x] avvio automatico;
- [x] riavvio reale;
- [x] DHCP, DNS e Internet dopo reboot;
- [ ] test attivo da un secondo host sull'uplink;
- [ ] traffico `invalid` costruito appositamente.

## 21. Rollback completo

```bash
sudo systemctl disable --now security-gateway-firewall.service

sudo nft delete table inet security_gateway_input_filter
sudo nft delete table inet security_gateway_filter

sudo rm -f /etc/systemd/system/security-gateway-firewall.service
sudo rm -f /usr/local/sbin/security-gateway-firewall
sudo rm -rf /etc/security-gateway-firewall

sudo systemctl daemon-reload
```

Non usare:

```bash
sudo nft flush ruleset
```

## 22. File collegati

```text
docs/steps/05-firewall-nftables.md
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
```

## 23. Privacy

Sono stati rimossi o generalizzati:

- nome completo dell'interfaccia Realtek;
- indirizzi MAC;
- indirizzo completo del gateway sull'uplink;
- password e segreti Wi-Fi;
- hostname e percorsi personali;
- log integrali;
- screenshot originali;
- output completi del ruleset.

## 24. Risultato finale

Il gateway applica un firewall stateful persistente senza sostituire il ruleset globale.

```text
client autorizzato
    → riceve DHCP
    → usa il DNS del gateway
    → raggiunge Internet tramite l'uplink consentito
    → riceve risposte established,related

traffico non autorizzato
    → viene contato
    → viene registrato con rate limit
    → viene bloccato
```

NetworkManager, Docker e libvirt continuano a gestire le proprie regole. Il firewall del laboratorio viene caricato automaticamente da un servizio systemd dedicato ed è stato verificato dopo un riavvio reale.