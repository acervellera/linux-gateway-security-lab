# Analisi Python dei log

Questa directory contiene gli strumenti sviluppati nella fase 9 del laboratorio. Usano soltanto la libreria standard Python e leggono i log JSON una riga alla volta, senza caricare file grandi interamente in memoria.

Ogni programma commenta le librerie importate, i dati ricevuti, le funzioni principali, gli errori gestiti e i test disponibili.

## Requisiti

```text
Python 3.11 o successivo
Bash
```

Non sono richieste librerie Python esterne.

## Comando unico

`analyze-lab` coordina automaticamente i tre analizzatori.

Per la prima esecuzione, dalla directory `python/`:

```bash
chmod +x analyze-lab
./analyze-lab
```

In alternativa può essere eseguito senza cambiare i permessi:

```bash
bash analyze-lab
```

Per impostazione predefinita il comando:

1. cerca il `conn.log` Zeek più recente sotto `/opt/zeek/logs`;
2. legge `/var/log/suricata/eve.json`;
3. crea copie temporanee private con permessi limitati;
4. esegue l'analisi Zeek;
5. esegue l'analisi Suricata;
6. prova la correlazione con una finestra di 5 secondi;
7. salva i report nella directory privata `../reports/`;
8. elimina le copie temporanee anche in caso di errore.

I report ricevono un prefisso con data e ora. Questi collegamenti puntano sempre all'ultima esecuzione:

```text
../reports/zeek-latest.json
../reports/suricata-latest.json
../reports/correlation-latest.json
```

Aiuto e opzioni:

```bash
./analyze-lab --help
```

Esempio con file specifici:

```bash
./analyze-lab \
    --zeek-log /percorso/conn.log.gz \
    --suricata-log /percorso/eve.json \
    --window-seconds 5
```

Il comando usa `sudo` soltanto quando il log scelto non è leggibile dall'utente. I programmi Python continuano a essere eseguiti senza privilegi amministrativi.

Se la correlazione restituisce zero eventi, l'analisi separata resta valida: normalmente significa che i due log non coprono lo stesso intervallo temporale.

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

Le copie temporanee create da `analyze-lab` vengono rimosse automaticamente. L'opzione `--keep-temp` deve essere usata soltanto per il debug e lascia nel terminale il percorso della directory privata.

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

bash -n analyze-lab
```
