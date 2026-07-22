# Fase 9 — Analisi dei log con Python

## Stato

```text
COMPLETATA E VERIFICATA — 21 luglio 2026
```

## Obiettivo raggiunto

Sono stati sviluppati programmi Python per analizzare i log JSON di Zeek e Suricata, produrre report testuali e JSON e correlare gli eventi osservati dai due sensori.

Il codice usa esclusivamente la libreria standard Python e legge i file una riga alla volta. I log integrali non vengono caricati in memoria e non vengono pubblicati.

## Componenti realizzati

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/analyze-lab
python/tests/test_phase9.py
python/samples/*.jsonl
```

Funzionalità:

- lettura JSON Lines normale e gzip;
- gestione di file mancanti, permessi e righe malformate;
- statistiche Zeek su protocolli, servizi, porte, byte, durata e stati;
- statistiche Suricata su eventi, flow, alert, anomalie e intervalli orari;
- esportazione JSON senza indirizzi IP grezzi o UID Zeek;
- correlazione bidirezionale tramite protocollo, endpoint e timestamp;
- comando Bash unico per trovare i log e coordinare le analisi;
- copie temporanee private e pulizia automatica;
- test automatici con `unittest`.

## Comando unico

Per l'uso quotidiano è disponibile:

```bash
cd python
chmod +x analyze-lab
./analyze-lab
```

Il coordinatore individua il `conn.log` Zeek più recente, legge il file EVE corrente di Suricata, richiama i tre programmi Python e salva i risultati nella directory privata `reports/`.

I collegamenti seguenti puntano sempre ai report più recenti:

```text
reports/zeek-latest.json
reports/suricata-latest.json
reports/correlation-latest.json
```

Il comando usa `sudo` soltanto per la lettura dei log protetti. Python viene eseguito come utente normale. Le copie temporanee sono create con permessi limitati e rimosse tramite `trap` anche in caso di errore.

## Analisi Zeek verificata

Su un campione reale di 19 connessioni:

```text
UDP:   14
TCP:    4
ICMP:   1
TLS:   17
QUIC:  13

Byte origine:      220132 B
Byte risposta:     321495 B
Durata media:      13,731 secondi
```

### Stati delle connessioni

| Stato | Eventi | Significato operativo |
|---|---:|---|
| `SF` | 13 | Connessione o scambio stabilito e terminato normalmente. |
| `S1` | 4 | Connessione stabilita, ma terminazione non osservata. |
| `OTH` | 1 | Flusso osservato senza il normale inizio TCP oppure protocollo non TCP. |
| `S0` | 1 | Tentativo iniziale osservato senza risposta visibile. |

Questi stati devono essere interpretati insieme a protocollo, durata, byte e cronologia dei pacchetti; da soli non dimostrano attività malevola.

## Analisi Suricata verificata

Una fotografia completa di `eve.json` conteneva 7074 eventi validi e nessuna riga malformata.

```text
QUIC:    2134
Stats:   2034
Flow:    1387
mDNS:     644
DNS:      540
TLS:      294
Alert:     17
DHCP:      13
HTTP:       5
Fileinfo:   5
Anomaly:    1
```

Traffico derivato dagli eventi `flow`:

```text
Verso i server: 31168599 B, circa 29,72 MiB
Verso i client: 1191333853 B, circa 1,11 GiB
```

Tutti i 17 alert osservati avevano severità `3` e azione `allowed`. Gli alert decoder o checksum non sono stati interpretati automaticamente come prova di attacco.

## Correlazione Zeek–Suricata

È stata eseguita una sessione con entrambi i sensori attivi.

```text
Connessioni Zeek:                       35
Eventi Suricata:                       318
Eventi nella finestra Zeek:            215
Eventi con 5-tupla valida:             197
Eventi Suricata correlati:             101
Connessioni Zeek distinte abbinate:     33
```

Risultati:

```text
Copertura connessioni Zeek:   94,29%
Copertura eventi correlabili: 51,27%
Delta temporale medio:         0,027 s
Delta temporale massimo:       0,330 s
```

Eventi correlati:

```text
QUIC:   93
TLS:     5
Flow:    2
Alert:   1
```

La correlazione indica compatibilità di 5-tupla e vicinanza temporale; non è da sola una prova che due record rappresentino esattamente lo stesso pacchetto.

## Privacy

I report pubblici e gli output JSON non contengono indirizzi IP grezzi, UID Zeek, query o domini DNS, SNI TLS, URI HTTP, contenuti dei pacchetti o log integrali. I campioni pubblicati sono sintetici e usano indirizzi riservati alla documentazione.

Il comando unico conserva i report nella directory privata ignorata da Git e cancella automaticamente le copie temporanee dei log.

## Test

```text
Ran 23 tests

OK
```

Sono verificati lettura normale e gzip, righe malformate, statistiche note, esportazione JSON, privacy, timestamp, confronto bidirezionale e correlazione positiva e negativa.

Il coordinatore Bash ha superato il controllo `bash -n` ed è stato provato con analizzatori simulati, verificando report, collegamenti `latest`, opzioni e pulizia.

## Valutazione finale

Zeek fornisce una vista compatta delle connessioni; Suricata produce eventi più granulari su protocolli, flussi e alert. Python permette di unire le due viste senza modificare rete, firewall o sensori. `analyze-lab` riduce l'uso quotidiano a un solo comando, mantenendo separati e leggibili i programmi didattici.
