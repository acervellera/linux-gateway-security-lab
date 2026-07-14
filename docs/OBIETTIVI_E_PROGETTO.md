# Obiettivi e progetto

## 1. Scopo del progetto

Questo progetto ha lo scopo di costruire, studiare e documentare un **gateway Linux controllato**. Il gateway dovrà diventare il punto obbligatorio attraverso cui passa il traffico di una rete interna prima di raggiungere Internet.

Il progetto nasce con due finalità collegate:

1. imparare in modo pratico il networking Linux applicato alla sicurezza;
2. imparare Python costruendo strumenti che raccolgono, analizzano e presentano dati di rete prodotti dal gateway.

Il progetto viene sviluppato inizialmente in un laboratorio virtuale per evitare di modificare direttamente il routing e il firewall dell'Ubuntu principale.

> Tutte le funzioni descritte in questo documento sono obiettivi progettuali. Lo stato realmente completato è registrato separatamente in [`LAVORO_SVOLTO_E_PROSSIMI_PASSI.md`](LAVORO_SVOLTO_E_PROSSIMI_PASSI.md).

---

## 2. Problema che si vuole risolvere

Normalmente un computer collegato alla rete domestica invia il traffico direttamente al router. In questo caso un altro computer non può osservare e controllare in modo completo il percorso dei pacchetti.

L'obiettivo è creare una rete interna separata nella quale i client usino come gateway una macchina Linux controllata:

```text
Client della rete interna
        |
        | gateway predefinito
        v
Gateway Linux
        |
        | routing, firewall e NAT
        v
Rete esterna
        |
        v
Internet
```

Il gateway dovrà poter decidere:

- quali pacchetti inoltrare;
- quali pacchetti bloccare;
- quali connessioni contare;
- quali informazioni registrare;
- quali dati fornire agli strumenti Python;
- quali servizi eseguire tramite Docker.

---

## 3. Risultato finale desiderato

Il risultato finale non sarà un singolo script, ma un piccolo sistema composto da più livelli.

### 3.1 Livello di rete

Il sistema Linux dovrà svolgere le funzioni di:

- router IPv4;
- gateway della rete interna;
- firewall stateful;
- NAT tramite masquerading;
- punto di monitoraggio;
- sorgente di log e contatori.

### 3.2 Livello di analisi

Python dovrà essere usato per:

- eseguire controlli diagnostici;
- leggere output strutturati dei comandi Linux;
- raccogliere contatori;
- produrre file JSON o CSV;
- creare report leggibili;
- individuare errori di configurazione;
- confrontare lo stato della rete nel tempo.

### 3.3 Livello applicativo

Docker potrà essere usato, in una fase successiva, per eseguire:

- una dashboard;
- un database;
- un servizio di raccolta metriche;
- un'applicazione Python;
- eventuali proxy espliciti;
- strumenti di visualizzazione.

Il routing principale non verrà affidato inizialmente a Docker. Il piano di rete resterà nel sistema operativo della VM gateway, mentre Docker verrà usato per i servizi applicativi.

---

## 4. Architettura virtuale prevista

La prima fase usa KVM/QEMU, libvirt e virt-manager.

```text
Internet
   |
   v
Ubuntu host
   |
   | rete libvirt "default"
   | subnet 192.168.122.0/24
   | DHCP e NAT forniti da libvirt
   v
Kali Linux, futura VM gateway
|-- eth0: lato WAN
|   |-- indirizzo tramite DHCP
|   `-- gateway della rete libvirt
|
`-- eth1: lato LAN
    |-- indirizzo statico 10.10.10.2/24
    `-- rete isolata "lab-lan"
             |
             v
          Parrot OS, futuro client
          |-- indirizzo previsto 10.10.10.3/24
          |-- gateway previsto 10.10.10.2
          `-- nessun collegamento diretto alla rete default
```

La separazione è essenziale. Parrot non dovrà possedere una seconda interfaccia sulla rete `default`, perché in quel caso potrebbe raggiungere Internet senza attraversare Kali.

---

## 5. Percorso previsto dei pacchetti

Quando il laboratorio sarà completato, una richiesta generata da Parrot seguirà questo percorso:

```text
Parrot 10.10.10.3
        |
        | pacchetto destinato a una rete esterna
        v
Kali eth1 10.10.10.2
        |
        | controllo della chain forward
        | decisione di routing
        | NAT/masquerading
        v
Kali eth0 192.168.122.x
        |
        v
Gateway libvirt 192.168.122.1
        |
        v
Ubuntu host
        |
        v
Internet
```

La risposta dovrà tornare a Kali, essere riconosciuta dal connection tracking e quindi essere inoltrata al client interno.

---

## 6. Evoluzione fisica prevista

Dopo aver completato e compreso il laboratorio virtuale, lo stesso modello potrà essere trasferito all'hardware reale.

L'host possiede:

- una scheda Wi-Fi interna usata per la connessione verso il router domestico;
- una scheda Wi-Fi USB Realtek RTL8812AU che ha dichiarato supporto alla modalità Access Point;
- una scheda Ethernet cablata disponibile come alternativa futura.

La topologia fisica prevista è:

```text
Router domestico
        |
        | connessione ricevuta dall'interfaccia WAN
        v
Ubuntu gateway fisico
|-- routing
|-- firewall
|-- NAT
|-- monitoraggio
|-- servizi Docker
`-- interfaccia LAN oppure hotspot Wi-Fi
        |
        v
Telefono, portatile o dispositivi IoT autorizzati
```

La possibilità tecnica della modalità AP è stata verificata, ma la creazione stabile dell'hotspot fisico non fa ancora parte del lavoro completato.

---

## 7. Concetti che il progetto deve insegnare

Il progetto è anche un percorso di studio. Dovrà permettere di comprendere:

- differenza tra interfaccia fisica e virtuale;
- differenza tra stato del link e possesso di un indirizzo IP;
- indirizzi MAC e IPv4;
- subnet e notazione CIDR;
- DHCP e configurazione statica;
- tabella di routing;
- gateway predefinito;
- metriche delle rotte;
- bridge e reti virtuali;
- forwarding del kernel;
- firewall stateful;
- connection tracking;
- NAT e masquerading;
- DNS e diagnostica a strati;
- namespace di rete Docker;
- lettura di output JSON con Python;
- produzione di report tecnici.

---

## 8. Differenza tra le principali funzioni

### Router

Collega reti IP differenti e sceglie dove inoltrare un pacchetto.

### Gateway

È il punto di uscita usato dai client per raggiungere reti esterne. Nel laboratorio Kali dovrà essere il gateway di Parrot.

### Bridge

Collega interfacce allo stesso livello Ethernet. Non è automaticamente un router e non crea automaticamente NAT.

### Firewall

Permette o blocca traffico secondo regole. Può valutare interfacce, indirizzi, protocolli, porte e stato delle connessioni.

### NAT

Modifica gli indirizzi dei pacchetti. Il masquerading consentirà ai client della LAN di condividere l'indirizzo WAN del gateway.

### Proxy

Intermedia protocolli applicativi. Non sostituisce automaticamente il routing generale della rete.

### Hotspot

Fornisce accesso Wi-Fi ai client. L'hotspot crea il collegamento radio, ma routing, DHCP, firewall e NAT restano funzioni separate.

---

## 9. Perché viene usata una macchina virtuale

Una VM possiede:

- un proprio kernel;
- proprie interfacce;
- propria tabella di routing;
- propri parametri `sysctl`;
- proprie regole `nftables`;
- una console accessibile anche quando la rete è rotta;
- snapshot ripristinabili.

Questo consente di sperimentare senza applicare immediatamente le regole al sistema principale.

---

## 10. Perché Docker verrà aggiunto dopo

Docker è già presente sull'host, ma un container condivide il kernel dell'host. Per amministrare routing e firewall da un container sarebbero spesso necessarie capacità elevate, per esempio `NET_ADMIN`, rete host o modalità privilegiata.

Inoltre nel sistema esistono più livelli possibili di NAT:

1. NAT del router domestico;
2. NAT della rete libvirt `default`;
3. futuro NAT della VM Kali;
4. NAT delle reti bridge Docker.

Per imparare in modo chiaro si mantiene questa separazione:

```text
Kali VM
    routing, forwarding, firewall e NAT

Docker
    applicazioni, analisi, database e dashboard
```

---

## 11. Informazioni osservabili dal gateway

Senza decifrare HTTPS, il gateway potrà normalmente osservare:

- indirizzi IP sorgente e destinazione;
- protocollo;
- porte TCP o UDP;
- quantità di pacchetti;
- quantità di byte;
- durata delle connessioni;
- errori e pacchetti scartati;
- richieste DNS tradizionali non cifrate;
- frequenza delle connessioni.

Il contenuto HTTPS resta cifrato. Il progetto non ha come obiettivo intercettare credenziali o comunicazioni altrui.

---

## 12. Criteri di completamento

### Fase 1 — Gateway virtuale minimo

La fase sarà completata quando:

- Parrot sarà collegata soltanto a `lab-lan`;
- Parrot raggiungerà Kali sulla LAN;
- Kali inoltrerà i pacchetti;
- il firewall permetterà soltanto il traffico previsto;
- il NAT sarà applicato sulla WAN;
- Parrot raggiungerà Internet passando obbligatoriamente attraverso Kali.

### Fase 2 — Monitoraggio

La fase sarà completata quando:

- saranno presenti contatori affidabili;
- sarà possibile osservare traffico sui due lati;
- saranno prodotti report senza dati sensibili;
- sarà possibile confrontare lo stato prima e dopo una modifica.

### Fase 3 — Python

La fase sarà completata quando uno strumento Python potrà:

- raccogliere dati senza modificare la rete;
- analizzare indirizzi, rotte e contatori;
- segnalare configurazioni incoerenti;
- esportare risultati strutturati;
- generare un report.

### Fase 4 — Docker

La fase sarà completata quando i dati raccolti potranno essere consultati tramite servizi containerizzati senza assegnare ai container privilegi di rete non necessari.

### Fase 5 — Gateway fisico

La fase sarà completata quando un dispositivo reale potrà collegarsi alla LAN o all'hotspot e raggiungere Internet attraverso il gateway fisico con regole equivalenti a quelle verificate nel laboratorio.

---

## 13. Limiti e regole di sicurezza

Il progetto deve essere usato soltanto su:

- sistemi propri;
- reti di laboratorio;
- dispositivi autorizzati;
- ambienti per i quali si possiede consenso esplicito.

Nel repository pubblico non devono essere inseriti:

- password;
- token;
- chiavi private;
- file `.env` reali;
- SSID domestici;
- indirizzi MAC reali non necessari;
- log non revisionati;
- dati personali;
- contenuti di traffico appartenenti a terzi.

---

## 14. Documentazione dello stato reale

Questo file descrive la destinazione del progetto. Non certifica che le funzioni siano già state implementate.

Il lavoro realmente eseguito, i comandi usati, gli errori incontrati e i prossimi passi sono documentati in:

- [`LAVORO_SVOLTO_E_PROSSIMI_PASSI.md`](LAVORO_SVOLTO_E_PROSSIMI_PASSI.md)
