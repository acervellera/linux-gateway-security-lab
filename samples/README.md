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
```

Il sample della fase 4 include riferimenti a due immagini pubbliche ritagliate:

```text
docs/images/04-wifi-security-before.svg
docs/images/04-wifi-security-after.svg
```

I sample delle fasi successive saranno aggiunti soltanto dopo l'esecuzione, la verifica e l'anonimizzazione dei risultati.
