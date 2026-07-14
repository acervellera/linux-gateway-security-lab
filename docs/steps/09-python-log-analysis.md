# Fase 9 — Analisi dei log con Python

## Stato

```text
DA FARE
```

## Obiettivo

Imparare Python costruendo programmi che leggono i log di Suricata e Zeek, calcolano statistiche e producono report comprensibili.

## Regola didattica

Ogni programma verrà scritto lentamente. Verranno spiegati:

- librerie importate;
- variabili;
- tipi di dato;
- cicli;
- condizioni;
- funzioni;
- gestione degli errori;
- lettura e scrittura dei file;
- struttura dei log;
- test del risultato.

## Percorso degli esercizi

### Esercizio 1 — Leggere un file

Aprire un file di esempio, leggere le righe e contarle.

Concetti:

- `pathlib.Path`;
- `open` tramite context manager;
- encoding;
- eccezioni di base.

### Esercizio 2 — Contare valori

Estrarre un campo e usare `collections.Counter` per trovare gli elementi più frequenti.

### Esercizio 3 — Suricata JSON

Leggere `eve.json` una riga alla volta con la libreria standard `json`.

Statistiche iniziali:

- tipi di evento;
- alert per firma;
- IP sorgente e destinazione;
- porte;
- eventi per ora.

### Esercizio 4 — Zeek

Leggere un estratto di `conn.log` o una versione JSON e calcolare:

- connessioni totali;
- IP più contattati;
- porte più usate;
- byte inviati e ricevuti;
- protocolli;
- durata media.

### Esercizio 5 — Unire i dati

Correlare eventi Suricata e connessioni Zeek usando timestamp, IP, porte e protocolli quando possibile.

### Esercizio 6 — Report

Produrre:

```text
Dispositivo: telefono-lab
Connessioni totali: ...
Domini DNS: ...
IP contattati: ...
Avvisi Suricata: ...
Traffico inviato: ...
Traffico ricevuto: ...
```

### Esercizio 7 — Esportazione

Salvare risultati in:

- JSON;
- CSV;
- output testuale;
- successivamente database.

## Struttura Python prevista

```text
python/
|-- README.md
|-- pyproject.toml
|-- src/
|   `-- gateway_analyzer/
|       |-- __init__.py
|       |-- suricata.py
|       |-- zeek.py
|       |-- models.py
|       |-- reports.py
|       `-- cli.py
`-- tests/
```

La struttura verrà creata gradualmente, non tutta in anticipo.

## Qualità minima

Ogni script deve:

- non richiedere `sudo` per leggere esempi copiati;
- non modificare firewall o rete;
- accettare percorsi come argomenti;
- gestire file mancanti;
- saltare o segnalare righe malformate;
- non caricare in memoria log enormi senza necessità;
- separare lettura, analisi e presentazione;
- includere dati di test anonimizzati.

## Test di completamento

- [ ] lettura Suricata funzionante;
- [ ] lettura Zeek funzionante;
- [ ] statistiche verificate manualmente su un piccolo campione;
- [ ] errori gestiti;
- [ ] report JSON e testuale prodotti;
- [ ] codice commentato e spiegato;
- [ ] test automatici essenziali superati.

## Prossimo passo

Salvare i risultati in un database e visualizzarli tramite servizi Docker.