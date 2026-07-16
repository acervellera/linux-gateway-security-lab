# Fase 5 — Firewall con nftables

## Stato

```text
IN CORSO — FILTRO FORWARD IMPLEMENTATO E VERIFICATO
```

Fase avviata il 16 luglio 2026 sul gateway Ubuntu fisico.

Il filtro del traffico inoltrato tra hotspot e uplink è stato caricato, verificato con traffico reale, rimosso tramite rollback e ricaricato correttamente. Il filtro del traffico diretto al gateway, il logging, la persistenza e il test controllato delle singole regole di blocco restano da completare.

## Obiettivo

Creare un firewall stateful che protegga Ubuntu e permetta soltanto il traffico necessario dal laboratorio verso Internet, senza interrompere le regole dinamiche di NetworkManager, Docker e libvirt.

## Valori pubblicabili

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
CLIENT_IP=10.42.0.x
```

Il nome completo dell'interfaccia USB, gli indirizzi MAC e gli output completi restano nei report privati locali.

## Ambiente osservato

```text
nftables:          installato e funzionante
iptables backend: nf_tables
nftables.service: inactive / disabled
UFW:               inactive
firewalld:         inactive
IPv4 forwarding:   1
```

Il servizio `nftables.service` non è ancora stato abilitato. Le regole esistenti vengono create dinamicamente da NetworkManager, Docker e libvirt.

Sono presenti tabelle gestite tramite `iptables-nft`:

```text
table ip filter
table ip nat
table ip mangle
table ip6 filter
table ip6 nat
table ip6 mangle
```

Non è stato usato `nft flush ruleset`, perché eliminerebbe anche regole appartenenti ad altri componenti.

## Backup eseguito

Prima delle modifiche sono state salvate copie private del ruleset:

```bash
sudo nft list ruleset > reports/phase-05/nftables-before-lab.nft
sudo nft -a list ruleset > reports/phase-05/nftables-before-lab-handles.txt
sudo nft -j list ruleset > reports/phase-05/nftables-before-lab.json
```

I file completi non vengono pubblicati senza revisione e anonimizzazione.

## Concetti verificati

- una `table` contiene chain e regole;
- una base chain è collegata a un hook del percorso dei pacchetti;
- la priorità stabilisce l'ordine delle base chain sullo stesso hook;
- `counter` osserva il traffico senza produrre un verdetto;
- `accept` termina la chain corrente, ma non impedisce ad altre base chain successive di esaminare il pacchetto;
- `drop` termina l'elaborazione e scarta il pacchetto;
- conntrack classifica i pacchetti come `new`, `established`, `related` o `invalid`;
- filtro e NAT sono funzioni distinte;
- le regole dinamiche non devono essere modificate direttamente.

## Regole dinamiche osservate

NetworkManager ha creato chain dedicate al profilo condiviso:

```text
nm-sh-in-<AP_IF>
nm-sh-fw-<AP_IF>
```

Le regole osservate permettono:

- DHCP sulle porte necessarie;
- DNS locale su TCP e UDP;
- traffico dalla subnet `10.42.0.0/24` proveniente dall'hotspot;
- traffico di ritorno `established,related` verso il client;
- NAT/masquerading limitato alla subnet del laboratorio.

Docker conserva le chain `DOCKER-*`; libvirt conserva le chain `LIBVIRT_*`. La loro presenza è stata ricontrollata dopo il caricamento e dopo il rollback del filtro del progetto.

## Strategia adottata

Per ridurre il rischio sono state usate due tabelle temporanee separate:

```text
table inet security_gateway
    osservazione con soli contatori
    hook input e forward
    priority -10
    policy accept

table inet security_gateway_filter
    filtro reale del solo forwarding hotspot/uplink
    hook forward
    priority -20
    policy accept
```

La policy della chain del progetto resta `accept` per non modificare traffico non collegato all'hotspot. Le regole finali bloccano invece gli inoltri non previsti che coinvolgono l'interfaccia hotspot.

## Fase osservativa

La prima tabella conteneva esclusivamente regole `counter`. Non erano presenti `drop`, `reject`, SNAT, DNAT o masquerading.

Sono stati osservati con traffico reale:

- richieste DNS UDP dal client verso `10.42.0.1`;
- nuove connessioni dal laboratorio verso l'uplink;
- pacchetti inoltrati dal laboratorio verso Internet;
- risposte `established,related` dall'uplink verso il client;
- nessuna nuova connessione osservata dall'uplink verso il laboratorio;
- nessun pacchetto `invalid` durante la prova.

Il rollback della tabella osservativa è stato eseguito con successo:

```bash
sudo nft delete table inet security_gateway
```

Le regole di NetworkManager, Docker e libvirt sono rimaste presenti. La tabella osservativa è stata successivamente ricaricata per continuare a raccogliere contatori.

## Filtro FORWARD implementato

La politica attiva è equivalente alla seguente:

```nft
chain forward_filter {
    type filter hook forward priority -20; policy accept;

    iifname "<AP_IF>" oifname "<UPLINK_IF>" \
        ct state invalid counter drop

    iifname "<UPLINK_IF>" oifname "<AP_IF>" \
        ct state invalid counter drop

    iifname "<AP_IF>" oifname "<UPLINK_IF>" \
        ip saddr 10.42.0.0/24 \
        ct state new,established,related \
        counter accept

    iifname "<UPLINK_IF>" oifname "<AP_IF>" \
        ip daddr 10.42.0.0/24 \
        ct state established,related \
        counter accept

    iifname "<UPLINK_IF>" oifname "<AP_IF>" \
        ct state new counter drop

    iifname "<AP_IF>" counter drop
    oifname "<AP_IF>" counter drop
}
```

Significato:

```text
hotspot -> uplink, connessioni valide       ACCEPT
uplink -> hotspot, risposte esistenti       ACCEPT
uplink -> hotspot, nuove connessioni        DROP
pacchetti invalidi sul percorso laboratorio DROP
hotspot -> altre interfacce                 DROP
altre interfacce -> hotspot                 DROP
traffico non collegato all'hotspot          invariato
```

## Controllo sintattico e caricamento

Il file è stato controllato prima del caricamento:

```bash
sudo nft --check --file "$FILTER_FILE"
echo "$?"
```

Risultato:

```text
0
```

Il filtro è stato quindi caricato e ispezionato:

```bash
sudo nft --file "$FILTER_FILE"
sudo nft -a list table inet security_gateway_filter
```

## Risultati reali del filtro

Durante la navigazione del client sono aumentati i contatori delle regole consentite:

```text
laboratorio -> uplink, new/established/related: pacchetti osservati, ACCEPT
uplink -> laboratorio, established/related:     pacchetti osservati, ACCEPT
```

Durante la stessa prova sono rimasti a zero:

```text
invalid laboratorio -> uplink
invalid uplink -> laboratorio
new uplink -> laboratorio
altri inoltri dall'hotspot
altri inoltri verso l'hotspot
```

Il valore zero dimostra che tali regole non hanno incontrato traffico corrispondente durante il test; non costituisce ancora una prova attiva di ogni singolo blocco.

## Coesistenza verificata

Dopo il caricamento del filtro sono state ricontrollate:

```bash
sudo nft list chain ip filter "nm-sh-fw-$AP_IF"
sudo nft list chain ip filter DOCKER-FORWARD
sudo nft list chain ip filter LIBVIRT_FWI
```

Risultato:

- i contatori NetworkManager hanno continuato ad aumentare;
- la chain `DOCKER-FORWARD` è rimasta presente;
- la chain `LIBVIRT_FWI` è rimasta presente;
- la navigazione del client è proseguita;
- DHCP e DNS dell'hotspot non sono stati modificati.

## Rollback e ricaricamento del filtro reale

Il filtro reale è stato rimosso esclusivamente con:

```bash
sudo nft delete table inet security_gateway_filter
```

La successiva interrogazione della tabella ha restituito `No such file or directory`, confermandone la rimozione. Le chain dinamiche di NetworkManager, Docker e libvirt sono rimaste presenti e la connettività dell'hotspot ha continuato a dipendere dalle regole dinamiche originali.

Il file è stato poi ricontrollato e ricaricato:

```bash
sudo nft --check --file "$FILTER_FILE"
sudo nft --file "$FILTER_FILE"
```

Dopo la ricarica i contatori sono ripartiti da zero e hanno ricominciato ad aumentare con traffico reale in entrambe le direzioni consentite. Questo verifica sia il rollback sia la possibilità di ripristinare il filtro senza riavviare NetworkManager, Docker o libvirt.

## Problema incontrato

Durante la prova l'hotspot è stato disattivato manualmente con una richiesta utente. Il log mostrava:

```text
activated -> deactivating
reason: user-requested
dnsmasq: uscita
```

La causa non era il filtro nftables. Dopo la riattivazione del profilo, NetworkManager ha riportato il dispositivo nello stato `activated` e il client ha completato nuovamente:

```text
DHCPDISCOVER
DHCPOFFER
DHCPREQUEST
DHCPACK
```

Questo episodio ha confermato l'importanza di distinguere un problema del firewall da un arresto del servizio hotspot.

## Test richiesti

- [ ] client -> gateway consentito solo per i servizi previsti;
- [x] client -> Internet consentito;
- [x] risposta Internet -> client consentita tramite connessione esistente;
- [ ] nuova connessione uplink -> client testata attivamente e bloccata;
- [ ] traffico `invalid` generato in modo controllato e bloccato;
- [x] contatori incrementano;
- [x] rollback della tabella osservativa verificato;
- [x] rollback e ricaricamento del filtro reale verificati;
- [x] coesistenza con NetworkManager verificata;
- [x] presenza delle chain Docker e libvirt verificata;
- [ ] logging con rate limit verificato;
- [ ] persistenza verificata dopo riavvio.

## Rollback

Rollback della sola tabella di filtro:

```bash
sudo nft delete table inet security_gateway_filter
```

Rollback della sola tabella osservativa:

```bash
sudo nft delete table inet security_gateway
```

Non usare:

```bash
sudo nft flush ruleset
```

Il forwarding IPv4 non deve essere impostato automaticamente a `0`, perché NetworkManager, Docker e libvirt possono dipendere dal valore globale.

## Persistenza

Il filtro non è ancora persistente. `nftables.service` resta disabilitato e le tabelle del progetto scompariranno al riavvio.

La persistenza verrà configurata soltanto dopo:

1. inventario dei servizi raggiungibili sul gateway;
2. filtro `INPUT` verificato;
3. test controllati dei blocchi;
4. logging con rate limit;
5. prova di riavvio.

## File previsto

```text
configs/nftables/security-gateway.nft
```

Il file definitivo non viene ancora pubblicato perché la fase non è completa.

## Prossimo passo

Inventariare le porte in ascolto e le connessioni amministrative prima di applicare il filtro `INPUT` al traffico diretto verso Ubuntu.
