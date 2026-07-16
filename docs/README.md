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
- [`LAVORO_SVOLTO_E_PROSSIMI_PASSI.md`](LAVORO_SVOLTO_E_PROSSIMI_PASSI.md): riassume il lavoro verificato e le prossime fasi del gateway fisico.
- [`TEMPLATE-FASE.md`](TEMPLATE-FASE.md): modello per aggiungere o aggiornare una fase.

## Guide operative

Le guide nella cartella [`steps`](steps) devono essere seguite in ordine numerico.

Ogni guida:

- parte come `DA FARE` o `IN CORSO`;
- contiene comandi realmente eseguiti;
- spiega opzioni e modifiche prodotte;
- include verifiche e rollback;
- viene segnata `COMPLETATA` solo dopo una prova reale.

Stato sintetico corrente:

```text
Fase 1  inventario hardware e rete      COMPLETATA
Fase 2  topologia e indirizzamento      COMPLETATA
Fase 3  hotspot Realtek                 COMPLETATA
Fase 4  DHCP, routing e NAT             COMPLETATA
Fase 5  firewall nftables               PROSSIMA
```

## Architettura sintetica

```text
Client autorizzato
  -> Realtek USB AP
  -> Ubuntu gateway
  -> MediaTek uplink
  -> Internet
```

È il percorso seguito da tutte le guide numerate.

## Sample pubblici

La cartella [`../samples`](../samples) contiene materiale pubblico anonimizzato:

- report sintetici delle fasi completate;
- output brevi revisionati;
- screenshot revisionati;
- futuri estratti di log, JSON o CSV per gli script Python.

Per la fase 4 sono disponibili:

- [`../samples/04-dhcp-routing-nat-report.md`](../samples/04-dhcp-routing-nat-report.md);
- [`../samples/04-dhcp-routing-nat-output.md`](../samples/04-dhcp-routing-nat-output.md).

Le regole dettagliate sono in [`../samples/README.md`](../samples/README.md).

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
5. `OBIETTIVI_E_PROGETTO.md` soltanto quando cambia l'architettura generale.
