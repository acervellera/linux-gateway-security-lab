# Sample pubblici anonimizzati

La cartella `samples/` contiene esempi pubblici derivati da attività realmente eseguite e verificati prima della pubblicazione.

## Organizzazione

I report delle fasi completate sono conservati direttamente nella radice di `samples/` con una numerazione coerente:

```text
01-inventario-hardware-rete-report.md
02-topologia-e-indirizzamento-report.md
03-hotspot-realtek-report.md
04-dhcp-routing-nat-report.md
05-firewall-nftables-report.md
```

Non viene usata una sottocartella `samples/reports/`: ogni fase completata possiede un solo report pubblico principale, facile da trovare e collegare dalla documentazione.

Gli output brevi o gli altri materiali possono invece avere file separati, purché il loro ruolo sia chiaro. Per esempio:

```text
04-dhcp-routing-nat-output.md
```

## Report della fase 4

[`04-dhcp-routing-nat-report.md`](04-dhcp-routing-nat-report.md) spiega in modo dettagliato:

- funzionamento di `ipv4.method=shared`;
- sequenza DHCP completa;
- DNS locale tramite `dnsmasq`;
- forwarding IPv4;
- NAT e masquerading;
- differenza tra cattura prima e dopo il NAT;
- differenza tra DNS leggibile e contenuto HTTPS cifrato;
- traffico TCP 443 e UDP 443;
- configurazione WPA2-RSN con CCMP/AES;
- test di arresto, riattivazione e rollback;
- privacy e dati rimossi.

Il file [`04-dhcp-routing-nat-output.md`](04-dhcp-routing-nat-output.md) contiene output brevi e revisionati collegati alla stessa fase.

## Report della fase 5

[`05-firewall-nftables-report.md`](05-firewall-nftables-report.md) documenta:

- inventario dei servizi locali;
- filtro `INPUT`;
- filtro `FORWARD` stateful;
- DHCP, DNS e ICMP consentiti;
- mDNS e WS-Discovery bloccati;
- test TCP 631 verso il gateway;
- test dall'hotspot verso la rete privata libvirt;
- logging con rate limit;
- rollback e reload;
- coesistenza con NetworkManager, Docker e libvirt;
- script amministrativo;
- servizio systemd dedicato;
- persistenza verificata dopo un riavvio reale;
- limiti delle prove dichiarati esplicitamente.

Le configurazioni e gli script collegati sono pubblicati nelle directory tecniche:

```text
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
```

## Contenuti ammessi

Possono essere inseriti:

- report pubblici anonimizzati delle fasi completate;
- output brevi e revisionati;
- esempi di configurazione senza segreti;
- estratti di log anonimizzati;
- file JSON o CSV di esempio;
- dati sintetici chiaramente dichiarati;
- screenshot ricostruiti o ritagliati e revisionati.

Ogni file deve derivare da una fase realmente eseguita oppure essere indicato esplicitamente come dato sintetico.

## Contenuti non ammessi

Non devono essere pubblicati:

- password o PSK Wi-Fi;
- SSID domestici;
- indirizzi MAC reali non necessari;
- nome completo di interfacce `wlx...` che incorpora un MAC;
- hostname o percorsi personali;
- IP pubblici o dati personali;
- output integrali non revisionati;
- catture PCAP grezze;
- screenshot originali contenenti dati locali;
- traffico appartenente a terzi.

Questi elementi devono restare nella cartella locale `reports/`, ignorata da Git.

## Immagini pubbliche della fase 4

```text
docs/images/04-wifi-security-before.svg
docs/images/04-wifi-security-after.svg
```

Le immagini sono ricostruzioni anonimizzate. Non contengono password, indirizzi MAC, notifiche personali o la barra di stato originale.

## Regola per le fasi future

Quando una fase viene completata:

1. creare un solo report principale `NN-nome-fase-report.md` nella radice di `samples/`;
2. aggiungere output separati soltanto quando utili;
3. anonimizzare ogni valore locale;
4. collegare il report da `docs/README.md` e dallo stato attuale;
5. dichiarare chiaramente ciò che non è stato provato attivamente.