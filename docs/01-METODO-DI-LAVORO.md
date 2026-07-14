# Metodo di lavoro

## Principio principale

Procediamo con una sola modifica di rete alla volta. Prima osserviamo, poi modifichiamo, quindi verifichiamo e infine documentiamo.

## Ciclo usato in ogni fase

```text
inventario
   -> teoria
   -> backup
   -> modifica minima
   -> test
   -> raccolta output
   -> rollback se necessario
   -> documentazione
```

## Stati consentiti

- **DA FARE**: non sono stati eseguiti comandi modificativi.
- **IN CORSO**: esiste lavoro reale, ma mancano verifiche o documentazione.
- **BLOCCATO**: una dipendenza o un errore impedisce di proseguire.
- **COMPLETATO**: obiettivo, test e rollback sono stati verificati.

## Regole per i comandi

Ogni comando inserito nei documenti deve indicare:

- su quale macchina va eseguito;
- se richiede `sudo`;
- che cosa modifica;
- che cosa significa ogni opzione importante;
- quale output ci aspettiamo;
- come capire se è fallito;
- come annullarne l'effetto.

I segnaposto devono essere riconoscibili:

```text
<UPLINK_IF>
<AP_IF>
<LAB_SSID>
<LAB_SUBNET>
<GATEWAY_IP>
<CLIENT_IP>
```

Non copiare un comando con segnaposto senza prima sostituirli con valori verificati.

## Regole per il codice Python

Ogni programma deve includere:

- docstring iniziale;
- import spiegati;
- funzioni piccole;
- nomi descrittivi;
- commenti didattici utili;
- controllo degli errori;
- percorsi configurabili;
- dati di esempio anonimizzati;
- test quando il programma diventa stabile.

Le librerie standard verranno preferite inizialmente. Le dipendenze esterne verranno aggiunte solo quando servono davvero.

## Regole per le configurazioni

Una configurazione viene copiata in `configs/` soltanto quando:

1. è stata applicata in laboratorio;
2. il servizio l'ha accettata;
3. i test previsti sono passati;
4. è presente un rollback;
5. non contiene segreti.

## Output e prove

Nei documenti conserviamo output brevi e anonimizzati. I file completi restano locali quando contengono:

- indirizzi MAC;
- SSID;
- hostname personali;
- IP pubblici;
- query DNS personali;
- nomi di dispositivi;
- contenuti di pacchetti.

## Regole per Git

Per ogni fase:

1. aggiornare il documento della fase;
2. aggiungere solo file realmente usati;
3. evitare commit con log o catture grezze;
4. usare messaggi chiari;
5. separare documentazione, configurazione e codice quando possibile.

Esempi:

```text
docs: document Realtek interface inventory
feat: add verified nftables gateway rules
feat: parse Zeek connection logs
fix: handle malformed Suricata JSON records
```

## Definizione di completato

Una fase è completata solo se il documento contiene:

- data e ambiente di test;
- valori usati;
- comandi realmente eseguiti;
- output essenziali;
- test superati;
- eventuali problemi;
- rollback;
- conclusione tecnica.