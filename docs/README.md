# Indice della documentazione

## Punto di ingresso

1. leggere [`OBIETTIVI_E_PROGETTO.md`](OBIETTIVI_E_PROGETTO.md);
2. controllare [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md);
3. consultare [`00-ROADMAP.md`](00-ROADMAP.md);
4. seguire le guide operative in [`steps`](steps).

## Documenti principali

- [`OBIETTIVI_E_PROGETTO.md`](OBIETTIVI_E_PROGETTO.md): obiettivi e architettura fisica;
- [`00-ROADMAP.md`](00-ROADMAP.md): fasi e criteri di completamento;
- [`01-METODO-DI-LAVORO.md`](01-METODO-DI-LAVORO.md): comandi, verifiche, privacy e rollback;
- [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md): stato operativo verificato;
- [`LAVORO_SVOLTO_E_PROSSIMI_PASSI.md`](LAVORO_SVOLTO_E_PROSSIMI_PASSI.md): riepilogo e prossime attività;
- [`TEMPLATE-FASE.md`](TEMPLATE-FASE.md): modello per nuove fasi.

## Stato sintetico

```text
Fase 1  inventario hardware e rete      COMPLETATA
Fase 2  topologia e indirizzamento      COMPLETATA
Fase 3  hotspot Realtek                 COMPLETATA
Fase 4  DHCP, routing e NAT             COMPLETATA
Fase 5  firewall nftables               COMPLETATA
Fase 6  cattura tcpdump                 COMPLETATA
Fase 7  Suricata IDS                    COMPLETATA
Fase 8  Zeek                            COMPLETATA
Fase 9  analisi Python                  COMPLETATA
Fase 10 database e dashboard Docker     PROSSIMA
```

## Guide recenti

- [`steps/07-suricata.md`](steps/07-suricata.md);
- [`steps/08-zeek.md`](steps/08-zeek.md);
- [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md);
- [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md).

## Architettura sintetica

```text
Client autorizzato
  -> Realtek USB AP
  -> Ubuntu gateway
  -> nftables INPUT/FORWARD
  -> Suricata e Zeek
  -> analisi Python
  -> NAT/masquerading
  -> MediaTek uplink
  -> Internet
```

Le fasi 6–9 hanno verificato cattura prima e dopo il NAT, eventi IDS, log JSON di connessione e protocollo, analisi streaming, report JSON e correlazione temporale tra i due sensori.

## Codice Python verificato

```text
../python/read_zeek_json.py
../python/read_suricata_json.py
../python/correlate_logs.py
../python/tests/test_phase9.py
```

Test:

```text
Ran 23 tests

OK
```

## Sample pubblici

La cartella [`../samples`](../samples) contiene un report principale anonimizzato per ogni fase completata.

Report recenti:

- [`../samples/07-suricata-report.md`](../samples/07-suricata-report.md);
- [`../samples/08-zeek-report.md`](../samples/08-zeek-report.md);
- [`../samples/09-python-log-analysis-report.md`](../samples/09-python-log-analysis-report.md).

## Report privati

La cartella locale `reports/` è ignorata da Git e può contenere output integrali, percorsi locali e report personali.

```text
reports/07-suricata-private.md
reports/08-zeek-private.md
reports/09-python-log-analysis-private.md
```

Verifica obbligatoria:

```bash
git check-ignore -v reports/09-python-log-analysis-private.md
git status --short
```

I report privati, PCAP e log integrali non devono essere committati.

## Regola di aggiornamento

Dopo ogni sessione aggiornare:

1. il documento della fase corrente;
2. `02-STATO-ATTUALE.md`;
3. configurazioni o script realmente verificati;
4. la roadmap quando cambia lo stato;
5. il report pubblico principale;
6. gli indici del repository;
7. il report privato locale, senza aggiungerlo a Git.
