# Fase 4 — Report pubblico DHCP, routing e NAT

**Data della verifica:** 16 luglio 2026  
**Stato:** **COMPLETATA E VERIFICATA**

Questo report descrive le prove realmente eseguite sul gateway Ubuntu fisico. Tutti i valori che potrebbero identificare il sistema locale sono stati rimossi o generalizzati.

## 1. Obiettivo della fase

Dimostrare che un dispositivo autorizzato collegato all'hotspot:

1. riceve automaticamente una configurazione IPv4 tramite DHCP;
2. usa Ubuntu come gateway e server DNS;
3. viene inoltrato dall'interfaccia hotspot all'interfaccia uplink;
4. raggiunge Internet tramite NAT/masquerading;
5. conserva la cifratura applicativa di HTTPS e QUIC;
6. usa un collegamento Wi-Fi configurato con WPA2-RSN e CCMP/AES.

La fase non si limita a verificare che “Internet funziona”: separa DHCP, DNS, forwarding e NAT e raccoglie una prova per ciascun passaggio.

## 2. Architettura verificata

```text
Client autorizzato 10.42.0.x
        |
        v
Realtek USB in modalità AP
Gateway 10.42.0.1
        |
        | routing IPv4
        | NAT / masquerading
        v
MediaTek interna 192.168.10.x
        |
        v
Router 192.168.10.1
        |
        v
Internet
```

Valori pubblicabili:

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
HOTSPOT_PROFILE=security-gateway-ap
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
DNS_SERVER=10.42.0.1
UPLINK_IP=192.168.10.x
UPLINK_GATEWAY=192.168.10.1
```

Il nome completo dell'interfaccia USB, gli indirizzi MAC, l'indirizzo completo dell'host e gli output integrali restano nei report privati locali.

## 3. NetworkManager e `ipv4.method=shared`

Il profilo hotspot usa:

```text
ipv4.method=shared
```

Con questa modalità NetworkManager prepara dinamicamente diversi elementi:

- assegna `10.42.0.1/24` all'interfaccia hotspot;
- avvia una istanza di `dnsmasq` per DHCP e DNS;
- abilita il percorso di forwarding necessario;
- crea regole di filtro e NAT;
- applica masquerading al traffico della subnet del laboratorio.

Questi elementi sono collegati ma svolgono funzioni differenti:

```text
DHCP        assegna indirizzo, gateway e DNS al client
DNS         traduce i nomi in indirizzi IP
forwarding  permette al kernel di inoltrare pacchetti
NAT         sostituisce l'indirizzo sorgente privato sull'uplink
```

## 4. Verifica DHCP

### Porte osservate

```text
0.0.0.0:67/udp        dnsmasq, lato server DHCP
client:68/udp         lato client DHCP
```

La prima richiesta DHCP può essere inviata in broadcast, perché il client non possiede ancora un indirizzo IPv4.

### Sequenza osservata

```text
DHCPDISCOVER
DHCPOFFER
DHCPREQUEST
DHCPACK
```

Significato:

```text
DHCPDISCOVER  il client cerca un server DHCP
DHCPOFFER     il server propone una configurazione
DHCPREQUEST   il client richiede la configurazione proposta
DHCPACK       il server conferma il lease
```

### Risultato

Il client ha ricevuto:

```text
indirizzo: 10.42.0.x
gateway:   10.42.0.1
DNS:       10.42.0.1
subnet:    10.42.0.0/24
```

Durante la prova i dati cellulari sono stati disabilitati, evitando che il telefono usasse un percorso alternativo.

## 5. Verifica DNS

Porte osservate sul gateway:

```text
10.42.0.1:53/udp
10.42.0.1:53/tcp
```

È stata osservata una richiesta DNS tradizionale equivalente a:

```text
10.42.0.x:PORTA_CLIENT > 10.42.0.1:53
A? time.apple.com.
```

Risposta anonimizzata:

```text
10.42.0.1:53 > 10.42.0.x:PORTA_CLIENT
CNAME time.g.aaplimg.com.
A 17.253.x.x
```

Questo dimostra che il DNS tradizionale sulla porta 53 è visibile al gateway. La visibilità del nome DNS non implica la visibilità del contenuto HTTPS successivo.

## 6. Verifica del forwarding IPv4

Valore osservato:

```text
net.ipv4.ip_forward = 1
```

Il valore era già attivo nel sistema e non è stato forzato manualmente durante la prova.

Con il forwarding abilitato, il kernel può ricevere un pacchetto dalla Realtek e inoltrarlo sulla MediaTek. Senza forwarding, DHCP e DNS locali potrebbero funzionare, ma il client non raggiungerebbe Internet attraverso Ubuntu.

## 7. Verifica del NAT

La regola automatica osservata era equivalente a:

```nft
ip saddr 10.42.0.0/24
ip daddr != 10.42.0.0/24
masquerade
```

Significato:

- `ip saddr 10.42.0.0/24`: seleziona il traffico proveniente dal laboratorio;
- `ip daddr != 10.42.0.0/24`: evita di tradurre il traffico interno alla stessa subnet;
- `masquerade`: usa automaticamente l'indirizzo corrente dell'interfaccia di uscita.

I contatori della regola sono aumentati durante la navigazione, confermando che il NAT stava elaborando traffico reale.

Il NAT:

- modifica indirizzi e, quando necessario, porte;
- permette a più client privati di condividere l'indirizzo dell'uplink;
- non cifra il traffico;
- non sostituisce un firewall.

## 8. Cattura prima del NAT

Sulla Realtek, lato hotspot, è stato osservato un flusso equivalente a:

```text
10.42.0.x:PORTA_CLIENT > SERVER_REMOTO:443
SERVER_REMOTO:443 > 10.42.0.x:PORTA_CLIENT
```

In questo punto del percorso il gateway vede ancora l'indirizzo privato originale del client.

## 9. Cattura dopo il NAT

Sulla MediaTek, lato uplink, è stato osservato un flusso equivalente a:

```text
192.168.10.x:PORTA_ESTERNA > SERVER_REMOTO:443
SERVER_REMOTO:443 > 192.168.10.x:PORTA_ESTERNA
```

In questo punto l'indirizzo sorgente è quello del gateway sull'uplink.

Le catture pubblicate sono state eseguite in momenti differenti. Dimostrano i due lati della traduzione, ma non vengono presentate come lo stesso pacchetto abbinato riga per riga.

## 10. TCP 443, UDP 443 e cifratura

Sono stati osservati:

```text
TCP 443   HTTPS tradizionale
UDP 443   QUIC / HTTP/3 possibile
```

La cattura passiva permetteva di vedere metadati come:

- indirizzi IP;
- porte;
- direzione;
- tempi;
- quantità e dimensione dei pacchetti.

Non mostrava in chiaro:

- password;
- cookie applicativi;
- contenuto delle pagine HTTPS;
- messaggi protetti da TLS.

La cifratura applicativa è fornita da TLS/HTTPS/QUIC, non dal NAT.

## 11. Sicurezza del collegamento Wi-Fi

### Configurazione iniziale

Il profilo non esponeva esplicitamente tutti i parametri di protocollo e cifratura. Un client iOS mostrava un avviso relativo a una configurazione compatibile con WPA/WPA2-TKIP.

![Prima della correzione](../docs/images/04-wifi-security-before.svg)

### Correzione applicata

```bash
sudo nmcli connection modify security-gateway-ap \
    802-11-wireless-security.key-mgmt wpa-psk \
    802-11-wireless-security.proto rsn \
    802-11-wireless-security.pairwise ccmp \
    802-11-wireless-security.group ccmp
```

Spiegazione:

```text
key-mgmt wpa-psk  autenticazione con chiave precondivisa
proto rsn         usa il protocollo RSN, normalmente associato a WPA2
pairwise ccmp     cifra il traffico unicast con CCMP/AES
group ccmp        cifra il traffico di gruppo con CCMP/AES
```

### Configurazione finale verificata

```text
key-mgmt: wpa-psk
proto:    rsn
pairwise: ccmp
group:    ccmp
```

Dopo la riattivazione del profilo e la riconnessione, l'avviso è scomparso.

![Dopo la correzione](../docs/images/04-wifi-security-after.svg)

Le immagini sono ricostruzioni anonimizzate e non contengono password, MAC, notifiche personali o barra di stato originale.

## 12. Test di arresto e riattivazione

Il profilo hotspot è stato disattivato e riattivato per verificare che:

- `dnsmasq` venisse fermato e ricreato;
- l'interfaccia recuperasse `10.42.0.1/24`;
- il client potesse ottenere un nuovo lease;
- il percorso verso Internet tornasse operativo;
- la nuova configurazione RSN/CCMP fosse realmente applicata.

## 13. Problemi e interpretazione

### DNS leggibile ma HTTPS protetto

Non è una contraddizione. Il DNS classico e il traffico HTTPS appartengono a protocolli diversi. Il gateway può osservare una richiesta DNS sulla porta 53 senza poter leggere il contenuto TLS sulla porta 443.

### TCP 443 e UDP 443 contemporaneamente

I browser e i sistemi operativi possono usare TCP/TLS oppure QUIC su UDP. La presenza di entrambi non indica un errore.

### NAT non è sicurezza completa

Il masquerading consente la condivisione dell'uplink, ma la politica di sicurezza esplicita viene introdotta nella fase 5 tramite `nftables`.

## 14. Rollback della modifica Wi-Fi

Per rimuovere i vincoli espliciti introdotti nella fase:

```bash
sudo nmcli connection modify security-gateway-ap \
    802-11-wireless-security.proto "" \
    802-11-wireless-security.pairwise "" \
    802-11-wireless-security.group ""
```

Dopo una modifica al profilo è necessario disattivarlo e riattivarlo per applicarla.

Il rollback non elimina automaticamente il profilo hotspot.

## 15. Checklist finale

- [x] client collegato all'hotspot;
- [x] dati cellulari esclusi durante il test;
- [x] sequenza DHCP completa osservata;
- [x] indirizzo `10.42.0.x` assegnato;
- [x] gateway e DNS impostati a `10.42.0.1`;
- [x] DNS TCP/UDP in ascolto;
- [x] `net.ipv4.ip_forward=1` verificato;
- [x] regole automatiche di forwarding osservate;
- [x] masquerading osservato;
- [x] contatori NAT incrementati;
- [x] traffico catturato prima del NAT;
- [x] traffico catturato dopo il NAT;
- [x] DNS tradizionale osservato;
- [x] TCP 443 osservato;
- [x] UDP 443 osservato;
- [x] contenuto HTTPS non leggibile in chiaro;
- [x] WPA2-RSN/CCMP applicato;
- [x] avviso iOS eliminato;
- [x] spegnimento e riattivazione verificati.

## 16. File collegati

```text
docs/steps/04-dhcp-routing-nat.md
samples/04-dhcp-routing-nat-output.md
docs/images/04-wifi-security-before.svg
docs/images/04-wifi-security-after.svg
```

## 17. Privacy

Sono stati rimossi o generalizzati:

- nome completo dell'interfaccia Realtek;
- indirizzi MAC;
- password Wi-Fi;
- SSID domestici;
- IP completi non necessari;
- hostname e percorsi personali;
- output integrali;
- catture PCAP grezze.

## 18. Risultato finale

La fase dimostra l'intero percorso di rete:

```text
DHCP assegna la configurazione
        ↓
DNS risolve i nomi
        ↓
forwarding sposta i pacchetti tra interfacce
        ↓
NAT traduce la sorgente sull'uplink
        ↓
Internet risponde al gateway
        ↓
la risposta torna al client autorizzato
```

Il gateway ha fornito connettività reale al client e ha preparato la base tecnica necessaria per il firewall stateful della fase 5.