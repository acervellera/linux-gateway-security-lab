# Sample pubblici anonimizzati

La cartella `samples/` contiene materiale destinato al repository pubblico.

## Contenuti ammessi

Possono essere inseriti:

- report pubblici anonimizzati delle fasi completate;
- output brevi e revisionati;
- esempi di configurazione senza segreti;
- estratti di log anonimizzati;
- file JSON o CSV di esempio per gli script Python;
- dati sintetici utili per test e documentazione;
- screenshot ricostruiti o ritagliati, revisionati per rimuovere dati locali.

Ogni file deve derivare da una fase realmente eseguita oppure essere chiaramente indicato come dato sintetico.

## Contenuti non ammessi

Non devono essere inseriti:

- password o PSK Wi-Fi;
- SSID domestici;
- indirizzi MAC reali non necessari;
- nome completo di interfacce `wlx...` che incorpora un MAC;
- hostname o percorsi personali;
- IP pubblici o dati personali;
- output integrali non revisionati;
- catture PCAP grezze;
- screenshot originali non revisionati contenenti dati locali.

Questi elementi devono restare nella cartella locale `reports/`, ignorata da Git.

## Sample disponibili

```text
01-inventario-hardware-rete-report.md
02-topologia-e-indirizzamento-report.md
03-hotspot-realtek-report.md
04-dhcp-routing-nat-report.md
04-dhcp-routing-nat-output.md
reports/phase-05-forward-filter-checkpoint.md
reports/phase-05-firewall-nftables-final.md
```

Il checkpoint `phase-05-forward-filter-checkpoint.md` è conservato per mostrare lo stato intermedio della fase. Il riferimento aggiornato è `phase-05-firewall-nftables-final.md`.

Il report finale della fase 5 documenta in forma anonimizzata:

- filtro `INPUT`;
- filtro `FORWARD`;
- test TCP 631 verso il gateway;
- test verso la rete privata libvirt;
- logging con rate limit;
- rollback e reload;
- coesistenza con NetworkManager, Docker e libvirt;
- servizio systemd dedicato;
- persistenza verificata dopo reboot.

Le configurazioni revisionate e lo script collegato sono pubblicati fuori da `samples/`:

```text
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
```

## Immagini pubbliche

Il sample della fase 4 include riferimenti a due immagini pubbliche ritagliate:

```text
docs/images/04-wifi-security-before.svg
docs/images/04-wifi-security-after.svg
```

Le immagini e gli screenshot delle fasi successive vengono aggiunti soltanto dopo revisione e rimozione dei dati locali.