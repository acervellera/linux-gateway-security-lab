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
```

Non viene usata una sottocartella `samples/reports/`. Gli output supplementari sono ammessi soltanto quando aggiungono materiale utile senza duplicare il report principale.

## Fase 4

[`04-dhcp-routing-nat-report.md`](04-dhcp-routing-nat-report.md) documenta DHCP, DNS locale, forwarding IPv4, NAT, traffico prima e dopo la traduzione e sicurezza WPA2-RSN/CCMP.

[`04-dhcp-routing-nat-output.md`](04-dhcp-routing-nat-output.md) contiene output brevi e revisionati collegati alla fase.

## Fase 5

[`05-firewall-nftables-report.md`](05-firewall-nftables-report.md) documenta filtri `INPUT` e `FORWARD`, test attivi dei blocchi, logging con rate limit, rollback, coesistenza con NetworkManager/Docker/libvirt, script amministrativo, servizio systemd e persistenza dopo riavvio.

## Fase 6

[`06-cattura-tcpdump-report.md`](06-cattura-tcpdump-report.md) è l’unico report pubblico principale della fase e riunisce:

- filtri BPF e interpretazione di IP, porte e direzioni;
- traffico UDP 443 compatibile con QUIC/HTTP/3;
- consultazione WHOIS e limiti di attribuzione;
- DNS tradizionale e record `A`, `AAAA`, `CNAME`, `HTTPS`;
- richieste ICMP senza risposta del client;
- handshake TCP completo e principali flag TCP;
- confronto riga per riga prima e dopo il NAT;
- traduzione inversa e decremento TTL;
- PCAP limitato, snapshot di 128 byte e permessi privati;
- lettura compatibile con il profilo AppArmor attivo;
- privacy e conservazione dei dati.

I precedenti estratti separati della fase 6 sono stati incorporati nel report principale e rimossi. Il PCAP grezzo non è pubblicato.

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