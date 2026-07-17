# Indice della documentazione

## Punto di ingresso

Per seguire il progetto nell'ordine corretto:

1. leggere [`OBIETTIVI_E_PROGETTO.md`](OBIETTIVI_E_PROGETTO.md) per capire obiettivi e architettura fisica;
2. controllare [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md) per sapere che cosa è realmente verificato;
3. consultare [`00-ROADMAP.md`](00-ROADMAP.md) per l'ordine delle fasi;
4. seguire le guide operative nella cartella [`steps`](steps).

## Documenti principali

- [`OBIETTIVI_E_PROGETTO.md`](OBIETTIVI_E_PROGETTO.md): descrive obiettivi, componenti e architettura del gateway fisico Ubuntu.
- [`00-ROADMAP.md`](00-ROADMAP.md): elenca tutte le fasi e i criteri di completamento.
- [`01-METODO-DI-LAVORO.md`](01-METODO-DI-LAVORO.md): definisce regole per comandi, verifiche, privacy e rollback.
- [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md): contiene lo stato operativo verificato più aggiornato.
- [`LAVORO_SVOLTO_E_PROSSIMI_PASSI.md`](LAVORO_SVOLTO_E_PROSSIMI_PASSI.md): riassume il lavoro verificato e le prossime fasi.
- [`TEMPLATE-FASE.md`](TEMPLATE-FASE.md): modello per aggiungere o aggiornare una fase.

## Guide operative

Le guide nella cartella [`steps`](steps) devono essere seguite in ordine numerico.

Ogni guida:

- parte come `DA FARE` o `IN CORSO`;
- contiene comandi realmente eseguiti;
- spiega opzioni e modifiche prodotte;
- include verifiche e rollback;
- viene segnata `COMPLETATA` solo dopo una prova reale;
- dichiara esplicitamente gli eventuali casi non generati attivamente.

Stato sintetico corrente:

```text
Fase 1  inventario hardware e rete      COMPLETATA
Fase 2  topologia e indirizzamento      COMPLETATA
Fase 3  hotspot Realtek                 COMPLETATA
Fase 4  DHCP, routing e NAT             COMPLETATA
Fase 5  firewall nftables               COMPLETATA
Fase 6  cattura tcpdump                 PROSSIMA
```

Guide delle ultime fasi completate:

- [`steps/04-dhcp-routing-nat.md`](steps/04-dhcp-routing-nat.md);
- [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md).

## Architettura sintetica

```text
Client autorizzato
  -> Realtek USB AP
  -> Ubuntu gateway
  -> nftables INPUT/FORWARD
  -> MediaTek uplink
  -> Internet
```

Il firewall della fase 5 viene caricato automaticamente tramite un servizio systemd dedicato. Il servizio standard `nftables.service` resta disabilitato per non applicare un `flush ruleset` globale alle regole dinamiche di NetworkManager, Docker e libvirt.

## Configurazioni e script verificati

```text
../configs/nftables/security-gateway-input-filter.nft
../configs/nftables/security-gateway-filter.nft
../configs/systemd/security-gateway-firewall.service
../scripts/security-gateway-firewall
```

I file nftables pubblici sono revisionati e contengono un placeholder per il nome dell'interfaccia hotspot. Devono essere adattati e controllati con `nft --check` prima dell'uso.

## Sample pubblici

La cartella [`../samples`](../samples) contiene materiale pubblico anonimizzato.

Ogni fase completata possiede un report principale direttamente nella radice di `samples/`.

Report delle fasi 4 e 5:

- [`../samples/04-dhcp-routing-nat-report.md`](../samples/04-dhcp-routing-nat-report.md);
- [`../samples/05-firewall-nftables-report.md`](../samples/05-firewall-nftables-report.md).

Output supplementare della fase 4:

- [`../samples/04-dhcp-routing-nat-output.md`](../samples/04-dhcp-routing-nat-output.md).

Non viene usata una sottocartella `samples/reports/`. La struttura e le regole di anonimizzazione sono spiegate in [`../samples/README.md`](../samples/README.md).

## Report privati

La cartella locale:

```text
reports/
```

è ignorata da Git. Può contenere output integrali, screenshot originali e report privati con dati locali.

Prima di affidarsi al `.gitignore`, verificare con:

```bash
git check-ignore -v reports/<FILE>
```

## Regola di aggiornamento

Dopo ogni sessione aggiornare almeno:

1. il documento della fase corrente;
2. `02-STATO-ATTUALE.md`;
3. eventuali configurazioni o script realmente verificati;
4. la roadmap se cambia ordine o ambito;
5. il report principale della fase in `samples/` dopo anonimizzazione;
6. `OBIETTIVI_E_PROGETTO.md` soltanto quando cambia l'architettura generale.