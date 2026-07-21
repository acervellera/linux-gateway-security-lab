# Lavoro svolto e prossimi passi

## Funzione del documento

Questo file riassume l'evoluzione reale del gateway fisico Ubuntu. Per lo stato più aggiornato usare [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md); per comandi e rollback usare le guide in [`steps`](steps).

## Gateway fisico

```text
Telefono / dispositivo autorizzato
  -> SecurityGatewayLab
  -> Realtek USB AP
  -> Ubuntu gateway
  -> nftables INPUT e FORWARD
  -> Suricata IDS e Zeek standalone
  -> analisi Python
  -> NAT/masquerading
  -> MediaTek wlp13s0
  -> router
  -> Internet
```

## Fase 1 completata — Inventario

Verificati Ubuntu, kernel, schede MediaTek e Realtek, driver, supporto AP, route predefinita, rfkill e reti Docker.

## Fase 2 completata — Topologia

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
```

## Fase 3 completata — Hotspot

Realtek in modalità AP, client reali associati, indirizzi `10.42.0.x`, gateway raggiunto, Internet tramite MediaTek e rollback del profilo verificato.

## Fase 4 completata — DHCP, routing e NAT

Completata il 16 luglio 2026.

Verificati `dnsmasq`, sequenza DHCP, forwarding IPv4, masquerading, traffico sui lati Realtek e MediaTek, DNS classico, TCP/443, UDP/443 e WPA2-RSN con CCMP/AES.

```text
10.42.0.x:porta -> NAT -> 192.168.10.x:porta -> server:443
```

## Fase 5 completata — Firewall nftables

Completata il 17 luglio 2026.

### INPUT

Consentiti DHCP, DNS e ICMP necessari. Bloccati mDNS, WS-Discovery e accessi non previsti al gateway. Testato il blocco TCP 631.

### FORWARD

```text
hotspot -> uplink, new/established/related  ACCEPT
uplink -> hotspot, established/related      ACCEPT
uplink -> hotspot, new                      LOG + DROP
hotspot -> altre interfacce                 LOG + DROP
altre interfacce -> hotspot                 LOG + DROP
invalid sul percorso controllato            DROP
```

Testato il blocco hotspot→rete libvirt. Internet è rimasto funzionante.

### Persistenza

Installati script, configurazioni e servizio `security-gateway-firewall.service`. Persistenza verificata dopo riavvio reale. Il servizio standard `nftables.service` resta disabilitato.

## Fase 6 completata — tcpdump

Completata e verificata il 18 luglio 2026.

Sono stati verificati filtri BPF, DNS, ICMP, handshake TCP, flag principali, traffico cifrato, NAT sui due lati, decremento TTL, PCAP privato limitato, formato Linux cooked v2, permessi `600` e compatibilità con AppArmor.

```text
Report pubblico: samples/06-cattura-tcpdump-report.md
Report privato:  reports/06-cattura-tcpdump-private.md
```

## Fase 7 completata — Suricata IDS

Completata e verificata il 20 luglio 2026.

### Installazione e build

```text
Suricata:         8.0.3 RELEASE
suricata-update:  1.3.7
jq:               1.8.1
AF_PACKET:        yes
Hyperscan:        yes
systemd:          yes
```

Suricata è installato sull'host Ubuntu, non in Docker.

### Configurazione e regole

La configurazione predefinita usava `eth0`, interfaccia inesistente. `HOME_NET` è stato limitato a `10.42.0.0/24` e sono state caricate oltre 52.000 regole senza errori.

### Eventi e alert

Osservati eventi flow, QUIC, mDNS, DNS, TLS, HTTP, fileinfo, DHCP, stats e alert. Una regola ICMP locale innocua ha prodotto l'alert previsto con azione `allowed`.

### Modalità operativa e rotazione

Suricata resta disabilitato al boot ed è avviato soltanto durante il laboratorio. La rotazione reale ha creato `eve.json.1.gz`.

```text
Report pubblico: samples/07-suricata-report.md
Report privato:  reports/07-suricata-private.md
```

## Fase 8 completata — Zeek e log di rete

Completata e verificata il 21 luglio 2026.

### Installazione

I repository Ubuntu configurati non offrivano Zeek. È stato aggiunto il repository ufficiale per Ubuntu 26.04 con chiave dedicata tramite `signed-by`.

```text
Zeek:         8.0.9
ZeekControl:  2.6.0-31
Prefisso:     /opt/zeek
```

Verificati plugin AF_PACKET, Pcap e gli analizzatori DNS, HTTP, TLS, QUIC e X.509.

### Cattura manuale

Zeek è stato avviato direttamente sull'interfaccia hotspot con rete locale `10.42.0.0/24` e log JSON.

```text
pacchetti ricevuti:       12850
pacchetti kernel persi:   0
pacchetti non elaborati:  4 (0,03%)
gap TCP stimati:          0
perdita TCP stimata:      0,0%
byte mancanti:            0
```

Eventi principali:

```text
conn.log    56
dns.log     67
ssl.log     32
quic.log    20
```

### Configurazione standalone

```ini
[zeek]
type=standalone
host=localhost
interface=wlx<REDACTED>
```

```text
10.42.0.0/24    Rete laboratorio autorizzata
```

```ini
PrivateAddressSpaceIsLocal = 0
```

In `local.zeek` il `digest_salt` è stato personalizzato e il logging JSON è stato abilitato:

```zeek
@load policy/tuning/json-logs
```

### ZeekControl

Controllo:

```text
zeek scripts are ok.
```

La prova gestita ha prodotto:

```text
conn.log    19 eventi
dns.log     85 eventi
ssl.log     13 eventi
quic.log    13 eventi
```

Tutti i file erano JSON validi.

### Modalità operativa

```text
normalmente:             Zeek spento
sessione di laboratorio: zeekctl deploy
fine laboratorio:        zeekctl stop
avvio al boot:            non configurato
```

Al termine Zeek risultava `stopped` e Suricata `active`. Hotspot, routing, NAT e accesso Internet sono rimasti funzionanti.

La rotazione è configurata ogni ora. Non è stata attesa un'ora completa; è stata verificata l'archiviazione dei log all'arresto e la lettura degli archivi gzip.

```text
Guida:           docs/steps/08-zeek.md
Report pubblico: samples/08-zeek-report.md
Report privato:  reports/08-zeek-private.md
```

## Fase 9 completata — Analisi Python dei log

Completata e verificata il 21 luglio 2026.

### Codice

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/tests/test_phase9.py
```

### Metodo

- libreria standard Python;
- JSON Lines letto una riga alla volta;
- supporto gzip e standard input;
- indice in memoria soltanto per il piccolo log Zeek;
- Suricata letto in streaming;
- report aggregati senza IP grezzi e UID.

### Analisi Zeek

Verificati conteggi di protocolli, servizi, porte, byte, durata media e stati di connessione su un campione reale da 19 eventi.

### Analisi Suricata

Verificati tipi di evento, protocolli, flow, alert, anomalie, traffico e distribuzione oraria su oltre 7000 eventi EVE validi.

### Correlazione reale

È stata eseguita una sessione con entrambi i sensori attivi:

```text
Connessioni Zeek:                       35
Connessioni Zeek abbinate:              33
Eventi Suricata:                       318
Eventi Suricata correlati:             101
Copertura connessioni Zeek:          94,29%
Copertura eventi correlabili:        51,27%
Delta temporale medio:                0,027 s
Delta temporale massimo:              0,330 s
```

### Test

```text
Ran 23 tests

OK
```

```text
Guida:           docs/steps/09-python-log-analysis.md
Report pubblico: samples/09-python-log-analysis-report.md
Report privato:  reports/09-python-log-analysis-private.md
```

## Stato corrente

| Fase | Stato |
|---:|---|
| 1. Inventario | COMPLETATA |
| 2. Topologia | COMPLETATA |
| 3. Hotspot | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | COMPLETATA |
| 6. tcpdump | COMPLETATA |
| 7. Suricata | COMPLETATA |
| 8. Zeek | COMPLETATA |
| 9. Python | COMPLETATA |
| 10. Docker | PROSSIMA |
| 11. Test e hardening | DA FARE |

## Prossimi passi immediati

1. salvare il report privato come `reports/09-python-log-analysis-private.md`;
2. applicare permessi `600`;
3. verificare `git check-ignore` e `git status --short`;
4. sincronizzare il branch locale con gli aggiornamenti remoti;
5. passare a [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md);
6. definire schema, importazione idempotente e volumi persistenti;
7. montare log e report in sola lettura quando possibile.

## Report pubblici e privati

Nel repository pubblico:

- guide revisionate;
- configurazioni parametrizzate;
- script commentati;
- report principali anonimizzati;
- campioni sintetici;
- output brevi e revisionati.

Nella cartella locale `reports/`:

- output integrali;
- nomi reali delle interfacce;
- IP e porte effimere;
- query DNS osservate;
- log operativi;
- report personali.

Non pubblicare password, token, MAC, PCAP grezzi, log integrali, query DNS personali, SNI TLS, certificati, valore di `digest_salt` o traffico di terzi.
