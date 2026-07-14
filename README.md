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

## Nome del progetto

Il nome scelto per il progetto è **Ubuntu Security Gateway Lab**.

Slug GitHub consigliato:

```text
ubuntu-security-gateway-lab
```

Il repository può conservare temporaneamente il vecchio slug `linux-gateway-security-lab` senza compromettere la struttura dei file.

## Risultato finale

```text
Telefono / VM / dispositivo di test
                |
                v
       Realtek USB usata come hotspot
                |
                v
          Ubuntu gateway
          |-- NetworkManager / hostapd: hotspot
          |-- DHCP e DNS locale
          |-- routing IPv4 e NAT
          |-- nftables: firewall
          |-- tcpdump: cattura pacchetti
          |-- Suricata: rilevamento eventi
          |-- Zeek: log di rete
          |-- Python: analisi e report
          `-- Docker: database e dashboard
                |
                v
       MediaTek interna usata come uplink
                |
                v
             Internet
```

## Metodo di lavoro

Il progetto viene costruito una fase alla volta.

Ogni fase deve contenere:

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

1. Leggere la [roadmap completa](docs/00-ROADMAP.md).
2. Controllare lo [stato attuale](docs/02-STATO-ATTUALE.md).
3. Seguire i documenti nella cartella [`docs/steps`](docs/steps).
4. Aggiornare il documento della fase dopo ogni attività realmente eseguita.

## Struttura del repository

```text
.
|-- README.md
|-- SECURITY.md
|-- CONTRIBUTING.md
|-- docs/
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
|-- samples/      esempi di log anonimizzati
`-- reports/      report locali, normalmente ignorati da Git
```

Le directory tecniche verranno riempite solo quando la relativa fase sarà stata eseguita e verificata.

## Regola fondamentale

Nel repository distinguiamo sempre tre stati:

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
- indirizzi MAC non necessari;
- catture `.pcap` non revisionate;
- log contenenti dati personali;
- traffico appartenente a terzi.

## Licenza

Il progetto è distribuito con licenza MIT.