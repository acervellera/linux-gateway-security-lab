# Fase 9 — Analisi dei log con Python

## Stato

```text
COMPLETATA E VERIFICATA — 21 luglio 2026
```

## Obiettivo raggiunto

Sono stati sviluppati strumenti Python commentati per leggere, analizzare e correlare i log JSON di Zeek e Suricata senza modificare rete, firewall o sensori.

La soluzione usa soltanto la libreria standard Python e legge i file una riga alla volta, evitando di caricare log grandi interamente in memoria.

## Programmi

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/analyze-lab
```

I primi tre file svolgono l'analisi. `analyze-lab` è un coordinatore Bash: trova i log, prepara copie temporanee private, richiama i programmi Python, salva i report e pulisce i dati temporanei.

Campioni e test:

```text
python/samples/zeek_conn_sample.jsonl
python/samples/suricata_eve_sample.jsonl
python/samples/suricata_correlation_sample.jsonl
python/tests/test_phase9.py
```

## Scelte tecniche

- `pathlib.Path` per i percorsi;
- `json` per JSON Lines e report;
- `gzip` per gli archivi `.gz`;
- `collections.Counter` per i conteggi;
- `dataclasses` per risultati leggibili;
- `argparse` per le interfacce da terminale;
- `unittest` per i test automatici;
- Bash con `set -Eeuo pipefail` per il coordinatore;
- nessuna libreria esterna.

## Uso quotidiano con un solo comando

Dalla directory `python/`, la prima volta:

```bash
chmod +x analyze-lab
```

Successivamente:

```bash
./analyze-lab
```

È sempre possibile eseguirlo anche così:

```bash
bash analyze-lab
```

Il comando predefinito:

1. seleziona il `conn.log` Zeek più recente;
2. legge il file EVE corrente di Suricata;
3. copia i dati in una directory temporanea con `umask 077`;
4. esegue i tre programmi Python come utente normale;
5. usa `sudo` soltanto per leggere file protetti;
6. salva i report in `reports/`, esclusa da Git;
7. aggiorna i collegamenti `zeek-latest.json`, `suricata-latest.json` e `correlation-latest.json`;
8. elimina sempre la directory temporanea tramite `trap`.

Opzioni disponibili:

```bash
./analyze-lab --help
```

Esempio con log scelti manualmente:

```bash
./analyze-lab \
    --zeek-log /percorso/conn.log.gz \
    --suricata-log /percorso/eve.json \
    --window-seconds 5
```

Un risultato di correlazione pari a zero non rende inutili le due analisi separate. Significa normalmente che Zeek e Suricata non hanno osservato lo stesso intervallo temporale.

## Analisi Zeek

`read_zeek_json.py` calcola:

- connessioni totali;
- protocolli e servizi;
- porte di destinazione;
- byte inviati e ricevuti;
- durata media;
- stati delle connessioni;
- righe vuote o malformate.

Il programma separa correttamente servizi multipli come `quic,ssl` e supporta sia file normali sia gzip.

### Risultato reale verificato

```text
Eventi:             19
UDP:                14
TCP:                 4
ICMP:                1
TLS:                17
QUIC:               13
Byte origine:   220132 B
Byte risposta:  321495 B
Durata media:   13,731 s
```

Stati osservati:

| Stato | Eventi | Significato operativo |
|---|---:|---|
| `SF` | 13 | Connessione o scambio terminato normalmente. |
| `S1` | 4 | Connessione stabilita, terminazione non osservata. |
| `OTH` | 1 | Flusso visto senza normale inizio TCP o protocollo non TCP. |
| `S0` | 1 | Tentativo iniziale senza risposta visibile. |

## Analisi Suricata

`read_suricata_json.py` legge `eve.json`, file gzip oppure standard input e calcola:

- tipi di evento;
- protocolli di rete e applicativi;
- porte più frequenti;
- eventi per ora;
- alert per firma, categoria, severità e azione;
- stati e motivi dei flow;
- byte verso server e client;
- anomalie;
- numero di IP unici senza esportare gli indirizzi.

### Risultato reale verificato

```text
Eventi validi: 7074
Righe malformate: 0
Alert: 17
Flow: 1387
QUIC: 2134
DNS: 540
TLS: 294
```

Traffico derivato dai flow:

```text
Verso i server: 31168599 B
Verso i client: 1191333853 B
```

## Correlazione

`correlate_logs.py` indicizza il piccolo `conn.log` Zeek e legge Suricata in streaming. La chiave usa:

```text
protocollo + endpoint A + endpoint B + timestamp
```

Gli endpoint sono ordinati, quindi la correlazione funziona anche quando i sensori registrano direzioni opposte. Per gli eventi flow vengono considerati anche `flow.start` e `flow.end`.

### Sessione sovrapposta verificata

```text
Connessioni Zeek:                       35
Eventi Suricata:                       318
Eventi nella finestra Zeek:            215
Eventi con 5-tupla valida:             197
Eventi Suricata correlati:             101
Connessioni Zeek distinte abbinate:     33
Copertura connessioni Zeek:          94,29%
Copertura eventi correlabili:        51,27%
Delta medio:                          0,027 s
Delta massimo:                        0,330 s
```

Una corrispondenza indica compatibilità di 5-tupla e vicinanza temporale; non dimostra da sola che i record rappresentino esattamente lo stesso pacchetto.

## Esportazione

Tutti i programmi possono produrre report JSON. I report non includono:

- indirizzi IP grezzi;
- UID Zeek;
- query o domini DNS;
- SNI TLS;
- URI HTTP;
- contenuti dei pacchetti.

`analyze-lab` salva i report datati nella directory privata `reports/` e crea tre collegamenti simbolici ai risultati più recenti.

## Test

Comando:

```bash
cd python
python3 -m unittest discover -s tests -v
```

Risultato:

```text
Ran 23 tests

OK
```

Controllo sintattico:

```bash
python3 -m compileall -q \
    read_zeek_json.py \
    read_suricata_json.py \
    correlate_logs.py \
    tests

bash -n analyze-lab
```

Il coordinatore è stato inoltre provato con analizzatori simulati, verificando creazione dei tre report, collegamenti `latest`, lettura delle opzioni e pulizia automatica.

## Test di completamento

- [x] lettura Zeek funzionante;
- [x] lettura Suricata funzionante;
- [x] statistiche verificate manualmente su campioni piccoli;
- [x] file normali e gzip supportati;
- [x] errori gestiti;
- [x] report JSON e testuale prodotti;
- [x] correlazione reale verificata;
- [x] comando unico di coordinamento disponibile;
- [x] copie temporanee private e pulizia automatica;
- [x] codice commentato e spiegato;
- [x] test automatici essenziali superati.

## Report

```text
Report pubblico: samples/09-python-log-analysis-report.md
Report privato:  reports/09-python-log-analysis-private.md
```

Il report privato e i log integrali restano fuori da Git.

## Passo successivo

Fase 10: importare i report in un database e visualizzarli tramite servizi Docker, con volumi in sola lettura e senza container privilegiati non necessari.
