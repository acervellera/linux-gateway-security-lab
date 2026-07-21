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

## Guide operative

Ogni guida contiene comandi realmente eseguiti, spiegazione delle opzioni, risultati, problemi, verifiche, privacy e rollback. Una fase viene segnata `COMPLETATA` soltanto dopo una prova reale.

Stato sintetico:

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

Guide delle fasi più recenti:

- [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md);
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
  -> Suricata IDS e Zeek
  -> analisi Python
  -> NAT/masquerading
  -> MediaTek uplink
  -> Internet
```

La fase 6 ha verificato il percorso prima e dopo il NAT. La fase 7 ha verificato eventi IDS, regole, alert controllato, avvio su richiesta e rotazione dei log. La fase 8 ha verificato log JSON di connessione, DNS, TLS e QUIC, cattura senza drop kernel e gestione on demand tramite ZeekControl. La fase 9 ha verificato analisi streaming, esportazione JSON e correlazione reale tra i sensori.

## Configurazioni e script verificati

```text
../configs/nftables/security-gateway-input-filter.nft
../configs/nftables/security-gateway-filter.nft
../configs/systemd/security-gateway-firewall.service
../scripts/security-gateway-firewall
../python/read_zeek_json.py
../python/read_suricata_json.py
../python/correlate_logs.py
/etc/suricata/suricata.yaml
/var/lib/suricata/rules/suricata.rules
/var/lib/suricata/rules/local.rules
/opt/zeek/etc/node.cfg
/opt/zeek/etc/networks.cfg
/opt/zeek/etc/zeekctl.cfg
/opt/zeek/share/zeek/site/local.zeek
```

I file sotto `/etc`, `/var/lib` e `/opt` sono configurazioni locali del gateway e non vengono pubblicati integralmente quando contengono valori sensibili.

## Analisi Python

Gli strumenti della fase 9 si trovano sotto [`../python`](../python):

```text
read_zeek_json.py
read_suricata_json.py
correlate_logs.py
tests/test_phase9.py
```

Risultato dei test:

```text
Ran 23 tests

OK
```

## Sample pubblici

La cartella [`../samples`](../samples) contiene un report principale anonimizzato per ogni fase completata.

Report più recenti:

- [`../samples/05-firewall-nftables-report.md`](../samples/05-firewall-nftables-report.md);
- [`../samples/06-cattura-tcpdump-report.md`](../samples/06-cattura-tcpdump-report.md);
- [`../samples/07-suricata-report.md`](../samples/07-suricata-report.md);
- [`../samples/08-zeek-report.md`](../samples/08-zeek-report.md);
- [`../samples/09-python-log-analysis-report.md`](../samples/09-python-log-analysis-report.md).

Output supplementare della fase 4:

- [`../samples/04-dhcp-routing-nat-output.md`](../samples/04-dhcp-routing-nat-output.md).

Non viene usata una sottocartella `samples/reports/`. La struttura e le regole di anonimizzazione sono spiegate in [`../samples/README.md`](../samples/README.md).

## Report privati

La cartella locale:

```text
reports/
```

è ignorata da Git e può contenere output integrali, nomi reali delle interfacce, percorsi locali e report personali.

Report privati recenti:

```text
reports/06-cattura-tcpdump-private.md
reports/07-suricata-private.md
reports/08-zeek-private.md
reports/09-python-log-analysis-private.md
```

Verifica obbligatoria:

```bash
git check-ignore -v reports/09-python-log-analysis-private.md
git status --short
```

Il report privato non deve apparire tra i file da committare. I PCAP grezzi e i log integrali devono restare in aree private.

## Regola di aggiornamento

Dopo ogni sessione aggiornare:

1. il documento della fase corrente;
2. `02-STATO-ATTUALE.md`;
3. configurazioni o script realmente verificati;
4. la roadmap quando cambia lo stato;
5. il report pubblico principale della fase;
6. gli indici del repository;
7. il report privato locale, senza aggiungerlo a Git.
