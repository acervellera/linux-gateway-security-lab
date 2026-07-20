# Ubuntu Security Gateway Lab

Laboratorio didattico per costruire un gateway di sicurezza su Ubuntu e imparare, passo dopo passo:

- networking Linux;
- hotspot Wi-Fi;
- DHCP, routing e NAT;
- firewall con `nftables`;
- servizi e persistenza con systemd;
- cattura del traffico con `tcpdump`;
- rilevamento con Suricata;
- analisi dei log con Zeek;
- programmazione Python applicata alla sicurezza;
- database e dashboard con Docker.

> Usare il progetto esclusivamente su reti, sistemi e dispositivi propri o esplicitamente autorizzati.

## Architettura principale

```text
Telefono / dispositivo autorizzato
                    |
                    v
        Realtek USB usata come hotspot
                    |
                    v
              Ubuntu gateway
              |-- DHCP e DNS locale
              |-- routing IPv4 e NAT
              |-- nftables INPUT/FORWARD
              |-- servizio systemd dedicato
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

## Stato verificato

Le prime sette fasi sono completate:

1. hardware e rete inventariati;
2. piano IP definito;
3. hotspot reale verificato;
4. DHCP, routing e NAT verificati;
5. firewall `nftables` stateful reso persistente;
6. catture tcpdump con DNS, ICMP, handshake TCP, NAT e PCAP controllato verificate;
7. Suricata IDS passivo con alert controllato, avvio on demand e rotazione log verificato.

La fase 8, Zeek, è la prossima attività.

| Fase | Stato |
|---:|---|
| 1. Inventario hardware e rete | COMPLETATA |
| 2. Topologia e indirizzamento | COMPLETATA |
| 3. Hotspot Realtek | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | COMPLETATA |
| 6. tcpdump | COMPLETATA |
| 7. Suricata | COMPLETATA |
| 8. Zeek | PROSSIMA |
| 9. Python | DA FARE |
| 10. Docker dashboard | DA FARE |
| 11. Test e hardening | DA FARE |

## Risultati della fase 7

Sono stati verificati:

- installazione di Suricata 8.0.3 sull’host Ubuntu, non in Docker;
- supporto AF_PACKET e Hyperscan;
- correzione dell’interfaccia predefinita `eth0` inesistente;
- `HOME_NET` limitato a `10.42.0.0/24`;
- oltre 52.000 regole caricate senza errori;
- eventi DNS, TLS, QUIC, HTTP, DHCP, mDNS e flow;
- avvio e arresto su richiesta tramite systemd;
- servizio `disabled` al boot;
- regola ICMP locale innocua e alert ripetibile;
- azione `allowed`, coerente con IDS passivo;
- statistiche AF_PACKET e drop finali dello `0,25%`;
- rotazione reale di `eve.json` in archivio compresso;
- conservazione prevista di 14 rotazioni.

## Metodo di lavoro

Ogni fase contiene:

1. obiettivo;
2. teoria necessaria;
3. prerequisiti;
4. comandi commentati;
5. spiegazione delle opzioni;
6. risultati realmente osservati;
7. test di verifica;
8. problemi incontrati;
9. rollback;
10. stato finale.

Una fase viene segnata come completata soltanto dopo una verifica reale. Gli aspetti non testati attivamente vengono dichiarati.

## Da dove iniziare

1. [Obiettivi e architettura](docs/OBIETTIVI_E_PROGETTO.md)
2. [Stato attuale](docs/02-STATO-ATTUALE.md)
3. [Roadmap completa](docs/00-ROADMAP.md)
4. [Indice della documentazione](docs/README.md)
5. [Guide operative](docs/steps)

Guide più recenti:

- [`docs/steps/05-firewall-nftables.md`](docs/steps/05-firewall-nftables.md);
- [`docs/steps/06-cattura-tcpdump.md`](docs/steps/06-cattura-tcpdump.md);
- [`docs/steps/07-suricata.md`](docs/steps/07-suricata.md).

## Report pubblici

Ogni fase completata possiede un solo report principale nella radice di `samples/`.

```text
samples/05-firewall-nftables-report.md
samples/06-cattura-tcpdump-report.md
samples/07-suricata-report.md
```

Il report della fase 7 documenta installazione, AF_PACKET, configurazione, regole, alert, systemd on demand, statistiche e rotazione log.

## Report privati

`reports/` contiene materiale locale e sensibile ed è esclusa tramite `.gitignore`.

Report privati recenti:

```text
reports/06-cattura-tcpdump-private.md
reports/07-suricata-private.md
```

Verifica:

```bash
git check-ignore -v reports/07-suricata-private.md
```

I PCAP e i log integrali non vengono pubblicati.

## Componenti verificati

```text
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
/etc/suricata/suricata.yaml
/var/lib/suricata/rules/suricata.rules
/var/lib/suricata/rules/local.rules
```

Il servizio standard `nftables.service` non viene usato perché la configurazione predefinita contiene `flush ruleset`. Il progetto usa un servizio dedicato che gestisce soltanto le proprie tabelle.

Suricata resta disabilitato al boot e viene avviato soltanto quando serve:

```bash
sudo systemctl start suricata
sudo systemctl stop suricata
```

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
|   |-- images/
|   `-- steps/
|-- configs/
|-- scripts/
|-- python/
|-- docker/
|-- samples/
`-- reports/      privato e ignorato da Git
```

## Privacy

Non pubblicare password Wi-Fi, SSID domestici, token, chiavi, MAC, nomi completi `wlx...`, hostname o percorsi personali, IP e porte completi non necessari, query DNS personali, PCAP grezzi, log integrali, file `eve.json` completi o traffico appartenente a terzi.

## Licenza

Il progetto è distribuito con licenza MIT.
