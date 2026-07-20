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
Fase 8  Zeek                            PROSSIMA
```

Guide delle fasi più recenti:

- [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md);
- [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md);
- [`steps/07-suricata.md`](steps/07-suricata.md).

## Architettura sintetica

```text
Client autorizzato
  -> Realtek USB AP
  -> Ubuntu gateway
  -> nftables INPUT/FORWARD
  -> Suricata AF_PACKET in modalità IDS passiva
  -> NAT/masquerading
  -> MediaTek uplink
  -> Internet
```

La fase 6 ha verificato il percorso prima e dopo il NAT. La fase 7 ha verificato eventi IDS, regole, alert controllato, avvio su richiesta e rotazione dei log.

## Configurazioni e script verificati

```text
../configs/nftables/security-gateway-input-filter.nft
../configs/nftables/security-gateway-filter.nft
../configs/systemd/security-gateway-firewall.service
../scripts/security-gateway-firewall
/etc/suricata/suricata.yaml
/var/lib/suricata/rules/suricata.rules
/var/lib/suricata/rules/local.rules
```

I file sotto `/etc` e `/var/lib` sono configurazioni locali del gateway e non vengono pubblicati integralmente quando contengono valori sensibili.

## Sample pubblici

La cartella [`../samples`](../samples) contiene un report principale anonimizzato per ogni fase completata.

Report più recenti:

- [`../samples/05-firewall-nftables-report.md`](../samples/05-firewall-nftables-report.md);
- [`../samples/06-cattura-tcpdump-report.md`](../samples/06-cattura-tcpdump-report.md);
- [`../samples/07-suricata-report.md`](../samples/07-suricata-report.md).

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
```

Verifica obbligatoria:

```bash
git check-ignore -v reports/07-suricata-private.md
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
