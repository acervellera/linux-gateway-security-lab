# Analisi Python dei log

Questa directory contiene gli strumenti sviluppati nella fase 9 del laboratorio. Usano soltanto la libreria standard Python e leggono i log JSON una riga alla volta, senza caricare file grandi interamente in memoria.

Ogni programma commenta le librerie importate, i dati ricevuti, le funzioni principali, gli errori gestiti e i test disponibili.

## Requisiti

```text
Python 3.11 o successivo
```

Non sono richieste librerie esterne.

## Zeek

```bash
python3 read_zeek_json.py samples/zeek_conn_sample.jsonl
```

Esportazione JSON:

```bash
python3 read_zeek_json.py \
    samples/zeek_conn_sample.jsonl \
    --json-output reports/zeek-sample.json
```

Lo script supporta anche file `.gz`.

## Suricata

```bash
python3 read_suricata_json.py samples/suricata_eve_sample.jsonl
```

Lettura sicura del log protetto senza eseguire Python come root:

```bash
sudo cat /var/log/suricata/eve.json \
    | python3 read_suricata_json.py - \
        --json-output reports/suricata-eve.json
```

## Correlazione

```bash
python3 correlate_logs.py \
    samples/zeek_conn_sample.jsonl \
    samples/suricata_correlation_sample.jsonl \
    --window-seconds 2 \
    --json-output reports/correlation-sample.json
```

La correlazione confronta protocollo, coppie IP/porta e timestamp. Gli endpoint sono trattati in entrambe le direzioni.

## Privacy

I report JSON non includono indirizzi IP grezzi, UID Zeek, domini DNS, SNI TLS, URI HTTP o contenuti dei pacchetti. I campioni inclusi sono sintetici e usano indirizzi riservati alla documentazione.

## Test

Dalla directory `python/`:

```bash
python3 -m unittest discover -s tests -v
```

Risultato verificato:

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
```
