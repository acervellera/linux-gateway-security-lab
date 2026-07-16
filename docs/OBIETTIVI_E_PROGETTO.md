# Obiettivi e architettura del progetto

## 1. Scopo

Questo progetto serve a costruire, studiare e documentare un **gateway di sicurezza Linux su Ubuntu**. Il gateway è il punto attraverso cui passa il traffico dei dispositivi di laboratorio prima di raggiungere Internet.

Le finalità sono collegate:

1. imparare networking Linux applicato alla sicurezza;
2. comprendere hotspot, DHCP, routing, forwarding, NAT e firewall;
3. osservare il traffico con strumenti difensivi;
4. imparare Python sviluppando programmi che leggono log e stato della rete;
5. usare Docker per database e dashboard senza affidargli il routing principale.

L'intero percorso operativo è basato sul **gateway fisico Ubuntu**, collegato a dispositivi reali autorizzati attraverso l'hotspot Wi-Fi del laboratorio.

Lo stato realmente verificato è registrato in [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md) e nelle guide numerate della cartella [`steps`](steps).

---

## 2. Problema affrontato

Un dispositivo collegato normalmente alla rete domestica invia il proprio traffico direttamente al router. In questa situazione Ubuntu non è il punto obbligatorio del percorso e non può applicare in modo completo regole, contatori e monitoraggio.

Il progetto crea invece una rete separata:

```text
Client autorizzato
        |
        | gateway predefinito
        v
Ubuntu Security Gateway
        |
        | routing, firewall e NAT
        v
Router domestico
        |
        v
Internet
```

Ubuntu dovrà poter decidere:

- quali pacchetti inoltrare;
- quali pacchetti bloccare;
- quali connessioni contare;
- quali eventi registrare;
- quali dati fornire agli strumenti Python;
- quali servizi applicativi eseguire tramite Docker.

---

## 3. Architettura fisica principale

L'ambiente operativo principale usa due schede Wi-Fi con ruoli distinti:

```text
Telefono / portatile / dispositivo autorizzato
                    |
                    | SSID SecurityGatewayLab
                    | rete 10.42.0.0/24
                    v
Realtek RTL8812AU USB
modalità Access Point
                    |
                    | gateway 10.42.0.1
                    v
Ubuntu gateway fisico
|-- NetworkManager: profilo hotspot
|-- DHCP e inoltro DNS iniziali
|-- routing IPv4
|-- NAT / masquerading
|-- nftables
|-- tcpdump
|-- Suricata
|-- Zeek
|-- Python
`-- Docker per servizi applicativi
                    |
                    v
MediaTek MT7922 interna
uplink wlp13s0
                    |
                    v
Router domestico
                    |
                    v
Internet
```

Ruoli verificati:

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
HOTSPOT_PROFILE=security-gateway-ap
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
LAB_SSID=SecurityGatewayLab
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
```

Il nome completo della Realtek, gli indirizzi MAC, gli IP completi non necessari e i segreti restano nei report locali ignorati da Git.

---

## 4. Stato già raggiunto sul gateway fisico

Sono già stati verificati:

- inventario hardware e driver;
- ruolo della MediaTek come uplink Internet;
- supporto AP della Realtek USB;
- assenza di conflitti per la subnet `10.42.0.0/24`;
- creazione del profilo `security-gateway-ap`;
- modalità AP sulla Realtek;
- SSID WPA-PSK sulla banda 2,4 GHz, canale 6;
- assegnazione di `10.42.0.1/24` al gateway;
- associazione e autenticazione di client reali;
- assegnazione di indirizzi `10.42.0.x`;
- raggiungibilità del gateway da un client con risposta HTTP `200`;
- navigazione Internet tramite la condivisione IPv4 di NetworkManager;
- arresto e riattivazione dell'hotspot;
- eliminazione e ricreazione completa del profilo;
- comportamento dopo riavvio con `connection.autoconnect=no`.

La navigazione funziona già empiricamente tramite `ipv4.method=shared`; DHCP, DNS, forwarding e NAT devono però essere osservati e documentati nel dettaglio nella fase successiva.

---

## 5. Livelli del sistema finale

### 5.1 Livello di rete

Ubuntu dovrà svolgere le funzioni di:

- router IPv4;
- gateway della rete hotspot;
- firewall stateful;
- NAT tramite masquerading;
- punto di monitoraggio;
- sorgente di log e contatori.

### 5.2 Livello di osservazione

Verranno usati:

- `ip` e `ss` per stato e diagnostica;
- `nft` per firewall, contatori e NAT;
- `conntrack` per lo stato delle connessioni;
- `tcpdump` per catture mirate;
- Suricata per eventi IDS;
- Zeek per log di connessione, DNS, HTTP e TLS.

### 5.3 Livello Python

Python verrà usato per:

- eseguire controlli diagnostici senza modificare la rete;
- leggere output strutturati e log;
- raccogliere contatori;
- produrre JSON e CSV;
- generare report leggibili;
- rilevare configurazioni incoerenti;
- confrontare lo stato della rete nel tempo.

Ogni script dovrà includere import spiegati, funzioni piccole, commenti didattici, gestione degli errori e dati di esempio anonimizzati.

### 5.4 Livello Docker

Docker verrà usato in seguito per:

- database;
- dashboard;
- applicazioni Python;
- raccolta e visualizzazione delle metriche.

Il routing principale rimane nel sistema operativo Ubuntu. I container non devono ricevere privilegi di rete elevati senza una necessità dimostrata.

---

## 6. Concetti da imparare

Il progetto deve permettere di comprendere:

- interfacce di rete fisiche;
- link, indirizzi MAC e IPv4;
- subnet e notazione CIDR;
- DHCP e configurazione statica;
- gateway e tabella di routing;
- metriche delle rotte;
- bridge e reti Docker;
- forwarding del kernel;
- firewall stateful;
- connection tracking;
- NAT e masquerading;
- DNS e diagnostica a strati;
- access point Wi-Fi;
- cattura e analisi difensiva del traffico;
- lettura di log con Python;
- produzione di report tecnici.

---

## 7. Funzioni principali

### Router

Collega reti IP differenti e sceglie dove inoltrare un pacchetto.

### Gateway

È il punto di uscita usato dai client. In questo progetto il gateway è il sistema Ubuntu fisico.

### Bridge

Collega interfacce allo stesso livello Ethernet. Non è automaticamente un router e non crea automaticamente NAT.

### Firewall

Permette o blocca traffico in base a interfacce, indirizzi, protocolli, porte e stato delle connessioni.

### NAT

Modifica gli indirizzi dei pacchetti. Il masquerading permette ai client della rete interna di condividere l'indirizzo dell'interfaccia uplink.

### Hotspot

Fornisce il collegamento radio ai client. Non va confuso con routing, DHCP, firewall o NAT, anche se NetworkManager può configurare automaticamente alcune di queste funzioni con `ipv4.method=shared`.

### Proxy

Intermedia protocolli applicativi specifici. Non sostituisce il routing generale della rete.

---

## 8. Informazioni osservabili

Senza decifrare HTTPS, il gateway può normalmente osservare:

- IP sorgente e destinazione;
- protocollo;
- porte TCP e UDP;
- numero di pacchetti e byte;
- durata delle connessioni;
- errori e pacchetti scartati;
- DNS tradizionale non cifrato;
- frequenza e direzione delle connessioni.

Il contenuto HTTPS resta cifrato. Il progetto non ha lo scopo di intercettare credenziali o comunicazioni altrui.

---

## 9. Criteri di completamento del progetto fisico

Il progetto sarà completato quando un dispositivo autorizzato:

1. si collega stabilmente all'hotspot Realtek;
2. riceve una configurazione IP corretta;
3. usa Ubuntu come gateway;
4. raggiunge Internet tramite la MediaTek;
5. è filtrato da un ruleset `nftables` verificato;
6. genera traffico osservabile con `tcpdump`;
7. produce eventi e log utili in Suricata e Zeek;
8. compare nei report Python;
9. compare nella dashboard Docker;
10. continua a funzionare dopo test di riavvio, backup e ripristino.

I primi quattro punti sono già stati osservati; le guide numerate documentano lo stato preciso delle fasi.

---

## 10. Regole di sicurezza e privacy

Il progetto deve essere usato soltanto su:

- sistemi propri;
- reti di laboratorio;
- dispositivi autorizzati;
- ambienti per i quali esiste consenso esplicito.

Nel repository pubblico non devono essere inseriti:

- password;
- token;
- chiavi private;
- file `.env` reali;
- SSID domestici;
- nomi di interfaccia che incorporano MAC quando non necessari;
- indirizzi MAC reali non necessari;
- log e PCAP non revisionati;
- dati personali;
- contenuti di traffico appartenenti a terzi.

I dati completi devono restare nella cartella locale `reports/`, esclusa tramite `.gitignore`.

---

## 11. Documentazione autorevole

Per evitare incoerenze:

1. [`00-ROADMAP.md`](00-ROADMAP.md) definisce l'ordine delle fasi;
2. [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md) descrive lo stato verificato;
3. [`steps/`](steps) contiene comandi, test e rollback delle singole fasi;
4. questo documento descrive obiettivi e architettura generale;
5. [`LAVORO_SVOLTO_E_PROSSIMI_PASSI.md`](LAVORO_SVOLTO_E_PROSSIMI_PASSI.md) riassume la cronologia del lavoro e i prossimi passi del gateway fisico.
