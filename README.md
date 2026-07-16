# Ubuntu Security Gateway Lab

Laboratorio didattico per costruire un gateway di sicurezza su Ubuntu e imparare, passo dopo passo:

- networking Linux;
- hotspot Wi-Fi;
- DHCP, routing e NAT;
- firewall con `nftables`;
- cattura del traffico con `tcpdump`;
- rilevamento con Suricata;
- analisi dei log con Zeek;
- programmazione Python applicata alla sicurezza;
- database e dashboard con Docker.

> Usare il progetto esclusivamente su reti, sistemi e dispositivi propri o esplicitamente autorizzati.

## Architettura principale

Il percorso operativo principale è il gateway fisico Ubuntu:

```text
Telefono / portatile / dispositivo autorizzato
                    |
                    v
        Realtek USB usata come hotspot
                    |
                    v
              Ubuntu gateway
              |-- hotspot e DHCP iniziale
              |-- routing IPv4 e NAT
              |-- nftables
              |-- tcpdump
              |-- Suricata
              |-- Zeek
              |-- Python
              `-- Docker per servizi applicativi
                    |
                    v
        MediaTek interna usata come uplink
                    |
                    v
                 Internet
```

Le prime tre fasi sono state completate: hardware inventariato, piano IP definito e hotspot reale verificato con client, navigazione, rollback e comportamento dopo riavvio.

## Laboratorio virtuale secondario

Il repository conserva anche un laboratorio KVM/libvirt:

```text
Parrot VM
    -> Kali VM gateway
    -> rete libvirt default
    -> Ubuntu host
    -> Internet
```

Kali rappresenta il gateway e Parrot il client. Questo ambiente serve per esperimenti isolati e snapshot, ma non sostituisce la roadmap principale del gateway fisico.

## Metodo di lavoro

Il progetto viene costruito una fase alla volta. Ogni fase deve contenere:

1. obiettivo;
2. teoria necessaria;
3. prerequisiti;
4. comandi commentati;
5. spiegazione di ogni opzione;
6. risultati realmente osservati;
7. test di verifica;
8. problemi incontrati;
9. procedura di rollback;
10. stato finale della fase.

Un passaggio viene segnato come completato soltanto dopo una verifica reale.

## Da dove iniziare

1. Leggere [obiettivi e architettura](docs/OBIETTIVI_E_PROGETTO.md).
2. Controllare lo [stato attuale](docs/02-STATO-ATTUALE.md).
3. Leggere la [roadmap completa](docs/00-ROADMAP.md).
4. Seguire i documenti nella cartella [`docs/steps`](docs/steps).

## Struttura del repository

```text
.
|-- README.md
|-- SECURITY.md
|-- CONTRIBUTING.md
|-- docs/
|   |-- README.md
|   |-- OBIETTIVI_E_PROGETTO.md
|   |-- LAVORO_SVOLTO_E_PROSSIMI_PASSI.md
|   |-- 00-ROADMAP.md
|   |-- 01-METODO-DI-LAVORO.md
|   |-- 02-STATO-ATTUALE.md
|   |-- TEMPLATE-FASE.md
|   `-- steps/
|       |-- 01-inventario-hardware-rete.md
|       |-- 02-topologia-e-indirizzamento.md
|       |-- 03-hotspot-realtek.md
|       |-- 04-dhcp-routing-nat.md
|       |-- 05-firewall-nftables.md
|       |-- 06-cattura-tcpdump.md
|       |-- 07-suricata.md
|       |-- 08-zeek.md
|       |-- 09-python-log-analysis.md
|       |-- 10-database-dashboard-docker.md
|       `-- 11-test-hardening-backup.md
|-- configs/      configurazioni verificate
|-- scripts/      script Bash di supporto
|-- python/       programmi Python commentati
|-- docker/       compose, database e dashboard
|-- samples/      esempi pubblici anonimizzati: report, output e log revisionati
`-- reports/      report privati locali ignorati da Git
```

Le directory tecniche vengono riempite soltanto quando la relativa fase è stata eseguita e verificata.

### Differenza tra `samples/` e `reports/`

`samples/` contiene materiale sicuro da pubblicare e utile come esempio riproducibile:

- report pubblici anonimizzati delle fasi completate;
- output brevi con dati sensibili rimossi;
- in futuro, estratti di log revisionati e dati di esempio per gli script Python.

`reports/` contiene invece materiale privato locale:

- output completi;
- screenshot originali;
- nomi reali delle interfacce;
- indirizzi MAC e altri dati locali;
- report personali non destinati al repository.

La cartella `reports/` è esclusa tramite `.gitignore`.

## Stati usati

- **DA FARE**: attività pianificata ma non iniziata;
- **IN CORSO**: attività iniziata ma non completamente verificata;
- **COMPLETATO**: attività eseguita, testata e documentata.

Non inserire configurazioni presentandole come funzionanti prima di averle provate sul gateway.

## Privacy

Non pubblicare:

- password Wi-Fi;
- SSID domestici reali;
- token o chiavi private;
- file `.env` reali;
- nomi completi `wlx...` quando incorporano MAC;
- indirizzi MAC non necessari;
- catture `.pcap` non revisionate;
- log contenenti dati personali;
- traffico appartenente a terzi.

I report completi restano nella cartella locale `reports/`, esclusa tramite `.gitignore`.

## Licenza

Il progetto è distribuito con licenza MIT.
