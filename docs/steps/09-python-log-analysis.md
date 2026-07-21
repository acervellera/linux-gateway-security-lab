# Fase 9 — Analisi dei log con Python

## Stato

```text
PROSSIMA
```

I prerequisiti sono disponibili: Suricata produce `eve.json` e Zeek produce log JSON come `conn.log`, `dns.log`, `ssl.log` e `quic.log`.

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

Prima di scrivere codice verrà sempre valutato il metodo più diretto e semplice. Non verranno introdotte librerie esterne quando la libreria standard è sufficiente.

## Dati disponibili

Suricata:

```text
/var/log/suricata/eve.json
```

Zeek:

```text
/opt/zeek/logs/current/*.log
/opt/zeek/logs/.../*.log.gz
```

Gli esercizi useranno copie piccole e anonimizzate leggibili senza `sudo`. I log integrali resteranno privati.

## Percorso degli esercizi

### Esercizio 1 — Leggere un log JSON riga per riga

Aprire un piccolo estratto Zeek, leggere ogni riga, convertirla in un dizionario Python e contare gli eventi.

Concetti:

- `pathlib.Path`;
- context manager `with`;
- encoding UTF-8;
- libreria standard `json`;
- eccezioni di base.

### Esercizio 2 — Contare valori

Estrarre un campo e usare `collections.Counter` per trovare gli elementi più frequenti.

### Esercizio 3 — Zeek `conn.log`

Calcolare:

- connessioni totali;
- protocolli e servizi;
- porte più usate;
- byte inviati e ricevuti;
- durata media;
- stati delle connessioni.

### Esercizio 4 — Suricata JSON

Leggere `eve.json` una riga alla volta con la libreria standard `json`.

Statistiche iniziali:

- tipi di evento;
- alert per firma;
- IP sorgente e destinazione;
- porte;
- eventi per ora.

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
- includere dati di test anonimizzati;
- usare nomi chiari e commenti utili, non commenti ridondanti.

## Test di completamento

- [ ] lettura Zeek funzionante;
- [ ] lettura Suricata funzionante;
- [ ] statistiche verificate manualmente su un piccolo campione;
- [ ] errori gestiti;
- [ ] report JSON e testuale prodotti;
- [ ] codice commentato e spiegato;
- [ ] test automatici essenziali superati.

## Primo passo

Creare un piccolo estratto anonimizzato di `conn.log` e scrivere il programma Python più semplice che lo legge riga per riga e conta gli eventi.

## Passo successivo

Salvare i risultati in un database e visualizzarli tramite servizi Docker.
