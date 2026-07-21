# Sample pubblici anonimizzati

La cartella `samples/` contiene report pubblici derivati da attività realmente eseguite e verificati prima della pubblicazione.

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

## Fasi 4–6

- [`04-dhcp-routing-nat-report.md`](04-dhcp-routing-nat-report.md): DHCP, DNS, forwarding, NAT e sicurezza Wi-Fi;
- [`05-firewall-nftables-report.md`](05-firewall-nftables-report.md): filtri, logging, rollback e persistenza;
- [`06-cattura-tcpdump-report.md`](06-cattura-tcpdump-report.md): DNS, ICMP, TCP, NAT e PCAP controllato.

Il PCAP grezzo non è pubblicato.

## Fase 7 — Suricata

[`07-suricata-report.md`](07-suricata-report.md) documenta installazione, AF_PACKET, `HOME_NET`, regole, eventi, alert controllato, avvio su richiesta e rotazione di `eve.json`.

Il file completo `eve.json` non è pubblicato.

## Fase 8 — Zeek

[`08-zeek-report.md`](08-zeek-report.md) documenta installazione, plugin di cattura, log JSON `conn`, `dns`, `ssl` e `quic`, assenza di drop kernel nella prova manuale, configurazione standalone, ZeekControl e archiviazione.

Log integrali, IP, DNS e SNI non sono pubblicati.

## Fase 9 — Python

[`09-python-log-analysis-report.md`](09-python-log-analysis-report.md) documenta:

- analizzatori Python per Zeek e Suricata;
- lettura streaming di JSON Lines e gzip;
- statistiche su connessioni, flow e alert;
- report testuali e JSON;
- correlazione bidirezionale tramite 5-tupla e timestamp;
- protezione di IP e UID nei report;
- sessione reale con 33 connessioni Zeek abbinate su 35;
- 23 test automatici superati.

I campioni tecnici usati dai test si trovano sotto `python/samples/`, sono sintetici e usano indirizzi riservati alla documentazione.

## Contenuti ammessi

- report pubblici anonimizzati;
- output brevi e revisionati;
- configurazioni prive di segreti;
- estratti sintetici o anonimizzati;
- dati sintetici chiaramente dichiarati;
- screenshot ricostruiti o revisionati.

## Contenuti non ammessi

- password o PSK Wi-Fi;
- SSID domestici;
- MAC reali;
- nome completo di interfacce che incorpora un MAC;
- hostname e percorsi personali;
- IP completi non necessari;
- porte effimere associate a sessioni reali;
- query DNS personali;
- SNI TLS e certificati;
- valore di `digest_salt`;
- log integrali;
- PCAP grezzi;
- traffico appartenente a terzi.

Questi elementi devono restare nella cartella locale `reports/`, ignorata da Git, oppure in una directory privata esterna al repository.

## Regola per le fasi future

1. creare un solo report principale `NN-nome-fase-report.md`;
2. aggiungere output separati soltanto quando utili e non duplicati;
3. anonimizzare ogni valore locale o remoto non necessario;
4. collegare il report dagli indici e dallo stato attuale;
5. dichiarare chiaramente ciò che non è stato provato attivamente.
