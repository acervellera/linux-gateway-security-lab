# Sample pubblici anonimizzati

La cartella `samples/` contiene esempi pubblici derivati da attività realmente eseguite e verificati prima della pubblicazione.

## Organizzazione

Ogni fase completata possiede un solo report pubblico principale nella radice di `samples/`:

```text
01-inventario-hardware-rete-report.md
02-topologia-e-indirizzamento-report.md
03-hotspot-realtek-report.md
04-dhcp-routing-nat-report.md
05-firewall-nftables-report.md
06-cattura-tcpdump-report.md
07-suricata-report.md
08-zeek-report.md
09-python-log-analysis-report.md
```

Non viene usata una sottocartella `samples/reports/`. Gli output supplementari sono ammessi soltanto quando aggiungono materiale utile senza duplicare il report principale.

## Fase 4

[`04-dhcp-routing-nat-report.md`](04-dhcp-routing-nat-report.md) documenta DHCP, DNS locale, forwarding IPv4, NAT, traffico prima e dopo la traduzione e sicurezza WPA2-RSN/CCMP.

[`04-dhcp-routing-nat-output.md`](04-dhcp-routing-nat-output.md) contiene output brevi e revisionati collegati alla fase.

## Fase 5

[`05-firewall-nftables-report.md`](05-firewall-nftables-report.md) documenta filtri `INPUT` e `FORWARD`, test attivi dei blocchi, logging con rate limit, rollback, coesistenza con NetworkManager/Docker/libvirt, script amministrativo, servizio systemd e persistenza dopo riavvio.

## Fase 6

[`06-cattura-tcpdump-report.md`](06-cattura-tcpdump-report.md) riunisce:

- filtri BPF e interpretazione di IP, porte e direzioni;
- traffico UDP 443 compatibile con QUIC/HTTP/3;
- DNS tradizionale e record `A`, `AAAA`, `CNAME`, `HTTPS`;
- richieste ICMP senza risposta del client;
- handshake TCP completo e principali flag TCP;
- confronto prima e dopo il NAT;
- PCAP limitato, snapshot di 128 byte e permessi privati;
- lettura compatibile con AppArmor attivo;
- privacy e conservazione dei dati.

Il PCAP grezzo non è pubblicato.

## Fase 7

[`07-suricata-report.md`](07-suricata-report.md) documenta:

- installazione di Suricata sull'host Ubuntu;
- cattura AF_PACKET sull'interfaccia hotspot;
- correzione dell'interfaccia predefinita `eth0`;
- `HOME_NET` limitato a `10.42.0.0/24`;
- caricamento delle regole senza errori;
- eventi DNS, TLS, QUIC, HTTP, DHCP, mDNS e flow;
- avvio e arresto su richiesta;
- regola ICMP locale e alert ripetibile;
- statistiche di cattura e drop;
- rotazione reale di `eve.json`.

Il file completo `eve.json`, i log integrali e i valori locali sensibili non sono pubblicati.

## Fase 8

[`08-zeek-report.md`](08-zeek-report.md) documenta:

- installazione di Zeek 8.0.9 sull'host Ubuntu;
- plugin di cattura AF_PACKET e Pcap;
- cattura manuale sull'interfaccia hotspot;
- rete locale `10.42.0.0/24`;
- log JSON `conn`, `dns`, `ssl` e `quic`;
- assenza di drop kernel, gap TCP e byte mancanti nella prova manuale;
- configurazione standalone tramite ZeekControl;
- `digest_salt` personalizzato senza pubblicarne il valore;
- avvio e arresto on demand;
- archiviazione dei log all'arresto;
- ripristino finale di Suricata.

Il nome reale dell'interfaccia, gli IP client, le query DNS, gli SNI TLS, i certificati e i log integrali non sono pubblicati.

## Fase 9

[`09-python-log-analysis-report.md`](09-python-log-analysis-report.md) documenta:

- analizzatori Python per Zeek e Suricata;
- lettura streaming di JSON Lines e gzip;
- statistiche su connessioni, servizi, flow, alert e anomalie;
- esportazione testuale e JSON;
- esclusione di indirizzi IP e UID dai report;
- correlazione bidirezionale tramite 5-tupla e timestamp;
- sessione reale con 33 connessioni Zeek abbinate su 35;
- 23 test automatici superati.

I campioni tecnici usati dai test sono sotto `python/samples/`, sono sintetici e usano indirizzi riservati alla documentazione.

## Contenuti ammessi

- report pubblici anonimizzati;
- output brevi e revisionati;
- configurazioni prive di segreti;
- estratti di log anonimizzati;
- dati sintetici chiaramente dichiarati;
- screenshot ricostruiti o revisionati.

## Contenuti non ammessi

- password o PSK Wi-Fi;
- SSID domestici;
- MAC reali;
- nome completo di interfacce `wlx...` che incorpora un MAC;
- hostname e percorsi personali;
- IP completi non necessari;
- porte temporanee associate a sessioni reali;
- query DNS personali;
- SNI TLS e certificati non necessari;
- valore di `digest_salt`;
- log integrali;
- PCAP grezzi;
- traffico appartenente a terzi.

Questi elementi devono restare nella cartella locale `reports/`, ignorata da Git, oppure in una directory privata esterna al repository.

## Immagini pubbliche della fase 4

```text
docs/images/04-wifi-security-before.svg
docs/images/04-wifi-security-after.svg
```

Le immagini sono ricostruzioni anonimizzate.

## Regola per le fasi future

1. creare un solo report principale `NN-nome-fase-report.md`;
2. aggiungere output separati soltanto quando utili e non duplicati;
3. anonimizzare ogni valore locale o remoto non necessario;
4. collegare il report dagli indici e dallo stato attuale;
5. dichiarare chiaramente ciò che non è stato provato attivamente.
