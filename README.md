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

Le prime sei fasi sono completate:

1. hardware e rete inventariati;
2. piano IP definito;
3. hotspot reale verificato;
4. DHCP, routing e NAT verificati;
5. firewall `nftables` stateful reso persistente;
6. catture tcpdump con DNS, ICMP, handshake TCP, NAT e PCAP controllato verificate.

La fase 7, Suricata, è la prossima attività.

| Fase | Stato |
|---:|---|
| 1. Inventario hardware e rete | COMPLETATA |
| 2. Topologia e indirizzamento | COMPLETATA |
| 3. Hotspot Realtek | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | COMPLETATA |
| 6. tcpdump | COMPLETATA |
| 7. Suricata | PROSSIMA |
| 8. Zeek | DA FARE |
| 9. Python | DA FARE |
| 10. Docker dashboard | DA FARE |
| 11. Test e hardening | DA FARE |

## Risultati della fase 6

Sono stati osservati e documentati:

- traffico del client autorizzato;
- DNS tradizionale e record `A`, `AAAA`, `CNAME`, `HTTPS`;
- richieste ICMP;
- handshake TCP SYN, SYN-ACK e ACK;
- flag ACK, PSH, FIN e RST;
- traffico TCP/443 e UDP/443 cifrato;
- stesso flusso sui lati hotspot e uplink;
- sostituzione dell’IP tramite NAT;
- traduzione inversa delle risposte;
- decremento TTL durante il forwarding;
- PCAP privato limitato a 20 record e 128 byte per record;
- lettura del PCAP con AppArmor mantenuto attivo.

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

- [`docs/steps/04-dhcp-routing-nat.md`](docs/steps/04-dhcp-routing-nat.md);
- [`docs/steps/05-firewall-nftables.md`](docs/steps/05-firewall-nftables.md);
- [`docs/steps/06-cattura-tcpdump.md`](docs/steps/06-cattura-tcpdump.md).

## Report pubblici

Ogni fase completata possiede un solo report principale nella radice di `samples/`.

```text
samples/04-dhcp-routing-nat-report.md
samples/05-firewall-nftables-report.md
samples/06-cattura-tcpdump-report.md
```

Il report della fase 6 consolida DNS, ICMP, handshake TCP, NAT, PCAP e AppArmor. I frammenti duplicati sono stati rimossi.

## Report privati

`reports/` contiene materiale locale e sensibile ed è esclusa tramite `.gitignore`.

Report privato previsto per la fase 6:

```text
reports/06-cattura-tcpdump-private.md
```

Verifica:

```bash
git check-ignore -v reports/06-cattura-tcpdump-private.md
```

Il PCAP grezzo resta in una directory privata esterna al repository e non viene pubblicato.

## Componenti verificati del firewall

```text
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
```

Il servizio standard `nftables.service` non viene usato perché la configurazione predefinita contiene `flush ruleset`. Il progetto usa un servizio dedicato che gestisce soltanto le proprie tabelle.

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

Non pubblicare password Wi-Fi, SSID domestici, token, chiavi, MAC, nomi completi `wlx...`, hostname o percorsi personali, IP e porte completi non necessari, query DNS personali, PCAP grezzi, log integrali o traffico appartenente a terzi.

## Licenza

Il progetto è distribuito con licenza MIT.