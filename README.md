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

Le prime nove fasi sono completate:

1. hardware e rete inventariati;
2. piano IP definito;
3. hotspot reale verificato;
4. DHCP, routing e NAT verificati;
5. firewall `nftables` stateful reso persistente;
6. catture tcpdump con DNS, ICMP, handshake TCP, NAT e PCAP controllato verificate;
7. Suricata IDS passivo con alert controllato, avvio on demand e rotazione log verificato;
8. Zeek 8.0.9 configurato come sensore standalone con log JSON DNS, TLS e QUIC verificati;
9. analizzatori Python per Zeek e Suricata, report JSON, correlazione e test automatici verificati.

La fase 10, database e dashboard Docker, è la prossima attività.

| Fase | Stato |
|---:|---|
| 1. Inventario hardware e rete | COMPLETATA |
| 2. Topologia e indirizzamento | COMPLETATA |
| 3. Hotspot Realtek | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | COMPLETATA |
| 6. tcpdump | COMPLETATA |
| 7. Suricata | COMPLETATA |
| 8. Zeek | COMPLETATA |
| 9. Python | COMPLETATA |
| 10. Docker dashboard | PROSSIMA |
| 11. Test e hardening | DA FARE |

## Risultati della fase 8

Sono stati verificati:

- Zeek 8.0.9 e ZeekControl installati sotto `/opt/zeek`;
- plugin di cattura AF_PACKET e Pcap;
- nodo standalone sull'interfaccia hotspot;
- rete locale limitata a `10.42.0.0/24`;
- `digest_salt` personalizzato;
- log JSON abilitati;
- cattura manuale con 12.850 pacchetti e zero drop kernel;
- assenza di gap TCP e byte mancanti nella prova manuale;
- eventi `conn.log`, `dns.log`, `ssl.log` e `quic.log`;
- avvio e arresto tramite ZeekControl;
- archiviazione dei log all'arresto;
- Zeek fermo e Suricata ripristinato al termine del test.

La rotazione oraria è configurata, ma non è stata attesa un'ora completa; è stata verificata l'archiviazione gestita all'arresto.

## Risultati della fase 9

Sono stati realizzati:

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/tests/test_phase9.py
```

Funzionalità verificate:

- lettura streaming di JSON Lines e gzip;
- analisi di `conn.log` Zeek;
- analisi di Suricata `eve.json`;
- report testuali e JSON;
- esclusione di IP grezzi e UID dai report;
- correlazione bidirezionale tramite 5-tupla e timestamp;
- 23 test automatici superati.

Nella sessione con entrambi i sensori attivi, 33 delle 35 connessioni Zeek hanno trovato almeno un evento Suricata compatibile. Il delta temporale medio era 0,027 secondi.

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

- [`docs/steps/07-suricata.md`](docs/steps/07-suricata.md);
- [`docs/steps/08-zeek.md`](docs/steps/08-zeek.md);
- [`docs/steps/09-python-log-analysis.md`](docs/steps/09-python-log-analysis.md).

## Report pubblici

Ogni fase completata possiede un solo report principale nella radice di `samples/`.

```text
samples/05-firewall-nftables-report.md
samples/06-cattura-tcpdump-report.md
samples/07-suricata-report.md
samples/08-zeek-report.md
samples/09-python-log-analysis-report.md
```

Il report della fase 9 documenta analisi Zeek e Suricata, esportazione JSON, correlazione reale e test automatici.

## Report privati

`reports/` contiene materiale locale e sensibile ed è esclusa tramite `.gitignore`.

Report privati recenti:

```text
reports/06-cattura-tcpdump-private.md
reports/07-suricata-private.md
reports/08-zeek-private.md
reports/09-python-log-analysis-private.md
```

Verifica:

```bash
git check-ignore -v reports/09-python-log-analysis-private.md
git status --short
```

I PCAP e i log integrali non vengono pubblicati.

## Componenti verificati

```text
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
/etc/suricata/suricata.yaml
/var/lib/suricata/rules/suricata.rules
/var/lib/suricata/rules/local.rules
/opt/zeek/etc/node.cfg
/opt/zeek/etc/networks.cfg
/opt/zeek/etc/zeekctl.cfg
/opt/zeek/share/zeek/site/local.zeek
```

Il servizio standard `nftables.service` non viene usato perché la configurazione predefinita contiene `flush ruleset`. Il progetto usa un servizio dedicato che gestisce soltanto le proprie tabelle.

Suricata e Zeek vengono usati su richiesta durante le sessioni di laboratorio:

```bash
sudo systemctl start suricata
sudo systemctl stop suricata

sudo /opt/zeek/bin/zeekctl deploy
sudo /opt/zeek/bin/zeekctl stop
```

Durante i test iniziali i due analizzatori sono stati eseguiti separatamente; nella fase 9 è stata inoltre verificata una sessione sovrapposta per la correlazione.

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

Non pubblicare password Wi-Fi, SSID domestici, token, chiavi, MAC, nomi completi `wlx...`, hostname o percorsi personali, IP e porte completi non necessari, query DNS personali, PCAP grezzi, log integrali, file `eve.json` completi, log Zeek integrali, SNI TLS, certificati o traffico appartenente a terzi.

## Licenza

Il progetto è distribuito con licenza MIT.
