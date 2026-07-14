# Fase 8 — Zeek e log di rete

## Stato

```text
DA FARE
```

## Obiettivo

Installare Zeek sul gateway e produrre log strutturati che descrivano connessioni, DNS, HTTP, TLS ed eventi rilevanti.

## Ruolo di Zeek

Zeek non è principalmente un firewall. Osserva il traffico e crea registri ad alto livello utili per analisi, investigazione e statistiche.

## Prerequisiti

- traffico del laboratorio già visibile;
- interfaccia di cattura scelta;
- orologio corretto;
- spazio disco e rotazione pianificati;
- Suricata funzionante o almeno documentata separatamente.

## Attività previste

- [ ] installare Zeek;
- [ ] registrare versione e percorsi;
- [ ] configurare l'interfaccia;
- [ ] definire la rete locale;
- [ ] eseguire un test manuale;
- [ ] attivare la gestione del servizio;
- [ ] verificare la rotazione dei log;
- [ ] generare traffico controllato;
- [ ] leggere i principali file;
- [ ] decidere se usare TSV o JSON.

## Log principali

```text
conn.log       connessioni e quantità di traffico
dns.log        query e risposte DNS
http.log       metadati HTTP non cifrato
ssl.log        metadati TLS nelle versioni che usano questo nome
x509.log       certificati osservati
notice.log     eventi considerati importanti
weird.log      comportamenti di protocollo insoliti
```

Nelle versioni recenti alcuni nomi o campi possono differire; verranno verificati sul sistema reale.

## Campi da comprendere in conn.log

- timestamp;
- UID della connessione;
- IP e porta origine;
- IP e porta destinazione;
- protocollo;
- servizio riconosciuto;
- durata;
- byte e pacchetti;
- stato della connessione.

## Verifiche previste

```bash
zeek --version
zeek -N
```

I comandi di deploy dipenderanno dal metodo di installazione effettivo e verranno documentati solo dopo la verifica.

## Test di completamento

- [ ] una richiesta DNS compare in `dns.log`;
- [ ] una connessione HTTPS compare in `conn.log` e nel log TLS;
- [ ] gli indirizzi del client sono corretti;
- [ ] byte e durata sono plausibili;
- [ ] i log ruotano;
- [ ] l'arresto di Zeek non interrompe il gateway;
- [ ] un estratto anonimizzato può essere letto da Python.

## Rollback

Fermare il servizio o il processo Zeek, conservare le configurazioni per l'analisi e rimuovere soltanto i log di test non necessari.

## File previsti

```text
configs/zeek/
samples/zeek/
```

## Prossimo passo

Scrivere il primo programma Python che legge i log senza modificare la rete.