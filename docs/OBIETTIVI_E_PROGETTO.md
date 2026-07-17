# Obiettivi e identità del progetto

## 1. Idea centrale

Questo progetto è un percorso pratico per **imparare sicurezza informatica, networking Linux, Python e Docker costruendo un vero gateway di laboratorio su Ubuntu**.

L’obiettivo non è assemblare strumenti senza comprenderli e non è creare rapidamente un prodotto da mettere in produzione. Ogni componente viene introdotto soltanto dopo aver studiato:

- quale problema risolve;
- dove agisce nel percorso dei pacchetti;
- quali comandi lo controllano;
- quali dati produce;
- quali rischi introduce;
- come verificarlo;
- come rimuoverlo senza danneggiare il resto del sistema.

Il risultato finale deve essere un laboratorio che funzioni realmente e, soprattutto, che possa essere **spiegato, verificato, rotto in modo controllato e ricostruito**.

---

## 2. Obiettivo principale

Trasformare un computer Ubuntu fisico in un gateway di sicurezza attraverso cui far passare il traffico di dispositivi di test autorizzati.

Il gateway deve permettere di studiare direttamente:

```text
client di laboratorio
        |
        | Wi-Fi
        v
Ubuntu gateway
        |
        | routing, firewall, NAT e monitoraggio
        v
uplink Internet
```

Ubuntu diventa quindi il punto in cui osservare e controllare il traffico, invece di lasciare che il dispositivo comunichi direttamente con il router domestico.

---

## 3. Cosa si vuole imparare davvero

### 3.1 Linux e networking

Comprendere con prove reali:

- interfacce fisiche e virtuali;
- indirizzi IPv4 e subnet CIDR;
- gateway e tabelle di routing;
- DHCP e DNS locale;
- forwarding del kernel;
- NAT e masquerading;
- connection tracking;
- differenza tra traffico `INPUT`, `OUTPUT` e `FORWARD`;
- convivenza tra NetworkManager, nftables, Docker e libvirt.

### 3.2 Sicurezza difensiva

Imparare a:

- progettare un firewall stateful;
- consentire soltanto i flussi necessari;
- osservare i contatori prima di applicare blocchi;
- distinguere un problema Wi-Fi, DHCP, routing, NAT o firewall;
- catturare traffico in modo mirato;
- interpretare metadati senza tentare di decifrare comunicazioni private;
- produrre log utili per diagnosi e investigazione;
- preparare sempre un rollback sicuro.

### 3.3 Python

Python non viene usato come scorciatoia per nascondere i comandi Linux.

Viene introdotto dopo aver capito manualmente i dati che dovrà elaborare. Gli script serviranno a:

- leggere output e log reali;
- analizzare JSON, CSV e file testuali;
- contare eventi, connessioni, indirizzi e porte;
- controllare lo stato del gateway;
- segnalare configurazioni incoerenti;
- produrre report tecnici;
- confrontare misurazioni eseguite in momenti differenti.

Ogni programma deve spiegare:

- librerie importate;
- variabili e tipi di dato;
- cicli e condizioni;
- funzioni;
- lettura e scrittura dei file;
- gestione degli errori;
- significato dei dati di rete elaborati.

### 3.4 Docker

Docker viene usato per i servizi applicativi del progetto, non per sostituire il gateway Linux.

I container potranno ospitare:

- importazione dei dati;
- database;
- API;
- dashboard;
- servizi Python.

Il routing principale, il firewall e l’osservazione delle interfacce restano responsabilità dell’host Ubuntu.

---

## 4. Metodo di lavoro

Ogni fase deve seguire lo stesso ciclo:

```text
osservare
    -> capire
    -> documentare
    -> fare backup
    -> modificare poco
    -> verificare
    -> provare il rollback
    -> registrare il risultato reale
```

Non vengono considerate completate attività che esistono soltanto nella documentazione.

Una fase è completata quando:

1. il comando è stato eseguito sul laboratorio reale;
2. l’output è stato interpretato;
3. il risultato atteso è stato confrontato con quello osservato;
4. gli effetti collaterali sono stati controllati;
5. il rollback è noto e, quando necessario, verificato;
6. i dati pubblici sono stati anonimizzati.

---

## 5. Risultati concreti da produrre

Il progetto deve generare materiale utile anche per lo studio futuro:

- guide operative numerate;
- spiegazioni dettagliate dei comandi e dei flag;
- report tecnici privati completi;
- esempi pubblici anonimizzati;
- configurazioni versionate;
- backup verificati;
- script Python commentati;
- dati di test piccoli e controllabili;
- procedure di diagnosi;
- procedure di rollback e ripristino.

Il repository non deve essere soltanto una raccolta di configurazioni. Deve mostrare **come si è arrivati a ogni scelta**.

---

## 6. Architettura del laboratorio

L’architettura principale usa due schede Wi-Fi con ruoli separati:

```text
Telefono, portatile o dispositivo autorizzato
                    |
                    | hotspot SecurityGatewayLab
                    | rete 10.42.0.0/24
                    v
Realtek USB
modalità Access Point
                    |
                    | gateway 10.42.0.1
                    v
Ubuntu gateway fisico
|-- NetworkManager
|-- DHCP e DNS locale iniziali
|-- routing IPv4
|-- NAT / masquerading
|-- nftables
|-- tcpdump
|-- Suricata
|-- Zeek
|-- Python
`-- Docker per database e dashboard
                    |
                    v
MediaTek interna
uplink wlp13s0
                    |
                    v
Router locale
                    |
                    v
Internet
```

Valori pubblicabili:

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
HOTSPOT_PROFILE=security-gateway-ap
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
LAB_SSID=SecurityGatewayLab
```

Nomi completi che incorporano MAC, indirizzi MAC, password e dettagli locali restano nei report privati.

---

## 7. Stato raggiunto

Sono già stati verificati sul gateway fisico:

- identificazione delle interfacce e dei driver;
- scelta della subnet del laboratorio;
- creazione dell’hotspot sulla Realtek;
- associazione di client reali;
- assegnazione di indirizzi `10.42.0.x`;
- raggiungibilità di Ubuntu dal client;
- DHCP e DNS tramite `dnsmasq`;
- forwarding IPv4;
- NAT e masquerading;
- traffico osservato prima e dopo il NAT;
- sicurezza Wi-Fi WPA2-RSN con CCMP;
- filtro nftables `FORWARD` stateful;
- contatori nftables con traffico reale;
- rollback e ricaricamento del filtro;
- convivenza con le regole di NetworkManager, Docker e libvirt.

Restano da completare nella fase firewall:

- filtro del traffico diretto a Ubuntu tramite `INPUT`;
- prove controllate delle regole di blocco;
- logging con rate limit;
- persistenza dopo riavvio.

Dopo il firewall verranno introdotti gradualmente cattura strutturata, IDS, log di rete, analisi Python e dashboard.

---

## 8. Cosa il progetto non vuole essere

Il progetto non ha lo scopo di:

- intercettare password o contenuti privati;
- monitorare dispositivi senza autorizzazione;
- attaccare sistemi esterni;
- creare un access point pubblico;
- trasformare immediatamente il computer in un appliance di produzione;
- copiare configurazioni trovate online senza comprenderle;
- concedere privilegi elevati ai container senza necessità;
- sostituire lo studio con script automatici non spiegati.

Le prove vengono eseguite soltanto su dispositivi, reti e servizi propri o esplicitamente autorizzati.

---

## 9. Criteri di completamento

Il progetto è considerato completo quando è possibile dimostrare e spiegare l’intero percorso:

```text
client autorizzato
    -> associazione Wi-Fi
    -> DHCP e DNS
    -> gateway Ubuntu
    -> firewall stateful
    -> routing e NAT
    -> Internet
    -> cattura e monitoraggio
    -> log Suricata e Zeek
    -> analisi Python
    -> database e dashboard
```

In particolare devono essere verificati:

1. connessione stabile del client all’hotspot;
2. configurazione IP corretta;
3. accesso controllato al gateway;
4. navigazione tramite l’uplink previsto;
5. blocco dei flussi non consentiti;
6. raccolta di catture brevi e mirate;
7. produzione di log IDS e di rete;
8. analisi dei log con programmi Python spiegati;
9. visualizzazione dei risultati tramite servizi Docker;
10. riavvio, backup, ripristino e smontaggio del laboratorio.

Il completamento non richiede soltanto che “funzioni”: richiede che ogni livello sia comprensibile e ripetibile.

---

## 10. Sicurezza, privacy e pubblicazione

Nel repository pubblico non devono comparire:

- password o chiavi;
- token e file `.env` reali;
- SSID domestici;
- indirizzi MAC reali non necessari;
- nomi completi di interfacce che incorporano MAC;
- hostname e percorsi personali non necessari;
- log completi non revisionati;
- file PCAP reali;
- dati personali o traffico appartenente a terzi.

I dati completi restano nei report locali esclusi da Git.

---

## 11. Documenti di riferimento

- [`00-ROADMAP.md`](00-ROADMAP.md): ordine delle fasi;
- [`01-METODO-DI-LAVORO.md`](01-METODO-DI-LAVORO.md): regole operative e documentali;
- [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md): stato realmente verificato;
- [`steps/`](steps): comandi, prove e rollback di ogni fase;
- [`LAVORO_SVOLTO_E_PROSSIMI_PASSI.md`](LAVORO_SVOLTO_E_PROSSIMI_PASSI.md): cronologia e punto di ripresa.
