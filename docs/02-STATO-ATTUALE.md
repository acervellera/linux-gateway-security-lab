# Stato attuale del progetto

Ultimo aggiornamento operativo: 15 luglio 2026.

## Obiettivo principale

Costruire un gateway fisico Ubuntu nel quale:

- la scheda Wi-Fi interna MediaTek fornisce l'uscita Internet;
- la scheda Wi-Fi USB Realtek crea l'hotspot per i dispositivi di laboratorio;
- Ubuntu esegue routing, firewall, NAT e monitoraggio;
- Suricata e Zeek producono eventi e log;
- Python analizza i log;
- Docker ospita database e dashboard senza gestire direttamente il routing principale.

## Fase 1 completata: risultati verificati

La raccolta iniziale è stata eseguita su:

```text
Ubuntu 26.04 LTS (Resolute Raccoon)
Kernel 7.0.0-27-generic
Architettura x86_64
```

### Uplink

```text
Interfaccia: wlp13s0
Hardware: MediaTek MT7922 802.11ax
Driver: mt7921e
Rete osservata: 192.168.10.0/24
Gateway predefinito: 192.168.10.1
Stato: collegato e usato per Internet
```

Il nome della rete Wi-Fi domestica, l'indirizzo IPv4 completo dell'host e gli indirizzi MAC non vengono registrati nel repository pubblico.

### Interfaccia hotspot

```text
Interfaccia pubblica: wlx<REDACTED>
Hardware: Realtek RTL8812AU
USB ID: 0bda:8812
Driver: rtw88_8812au
Versione riportata: 7.0.0-27-generic
Bus USB: 2-5.1:1.0
Supporto AP dichiarato: sì
rfkill: nessun blocco software o hardware
```

L'identificatore `phy` assegnato dal kernel può cambiare dopo un riavvio o dopo aver scollegato e ricollegato il dispositivo USB. Per le configurazioni persistenti viene quindi usato il nome dell'interfaccia, conservando il valore completo soltanto nella documentazione privata locale.

## Fase 2 completata: topologia e piano IP

La fase 2 è stata completata il 15 luglio 2026 usando soltanto comandi di osservazione.

### Reti virtuali e locali verificate

```text
192.168.10.0/24    rete locale dell'uplink
192.168.122.0/24   rete libvirt default
10.10.10.0/24      rete isolata libvirt lab-lan
172.17.0.0/16      bridge Docker predefinito
172.18.0.0/16      bridge Docker del laboratorio Python
```

La subnet scelta per l'hotspot non si sovrappone alle reti osservate.

### Piano approvato

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
DHCP_RANGE=10.42.0.50-10.42.0.200
DHCP_LEASE_SECONDS=3600
DNS_SERVER=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
IPV6_MODE=disabled-on-hotspot-initially
CLIENT_ISOLATION=enable-if-supported
```

## Fase 3 completata: hotspot Realtek

La fase 3 è stata completata e verificata il 15 luglio 2026.

### Configurazione applicata

```text
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
WIFI_MODE=ap
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
GATEWAY_IP=10.42.0.1/24
IPV4_METHOD=shared
IPV6_MODE=disabled
AUTOCONNECT=no
```

Il dominio regolamentare è stato richiesto come `IT`; il kernel ha mostrato `country 98: DFS-ETSI`. Il canale 6 a 2,4 GHz è risultato disponibile con potenza indicata di 20 dBm.

### Risultati verificati

- Realtek passata da `managed` a `AP`;
- SSID `SecurityGatewayLab` visibile;
- client reali autenticati, autorizzati e associati;
- almeno un client con indirizzo IPv4 `10.42.0.x` valido;
- gateway Ubuntu `10.42.0.1` raggiunto dal client tramite richiesta HTTP con risposta `200`;
- MediaTek `wlp13s0` rimasta collegata e usata come route predefinita;
- navigazione Internet osservata dal telefono tramite la condivisione IPv4 di NetworkManager;
- stato completo dei profili NetworkManager salvato localmente con segreti nascosti;
- hotspot fermato e riattivato;
- profilo eliminato e ricreato con successo;
- indirizzo della Realtek rimosso correttamente durante il rollback e ripristinato dopo la ricreazione.

Il comportamento dopo riavvio è intenzionalmente rinviato alla fase 11. Il profilo usa `connection.autoconnect=no`, quindi non è previsto che l'hotspot si attivi automaticamente al boot in questa fase.

## Stato delle fasi

| Fase | Stato | Nota |
|---:|---|---|
| 1. Inventario hardware e rete | COMPLETATA | Uplink MediaTek e Realtek AP identificati; driver, route, rfkill e modalità `AP` verificati |
| 2. Topologia e indirizzamento | COMPLETATA | Subnet, gateway, DHCP, DNS, profilo, banda, canale e percorso dei pacchetti definiti senza conflitti locali |
| 3. Hotspot Realtek | COMPLETATA | Hotspot attivo, client associati, gateway raggiunto e rollback completo verificato |
| 4. DHCP, routing e NAT | PROSSIMA | La condivisione IPv4 funziona empiricamente; DHCP, DNS, forwarding e NAT devono essere osservati e documentati nel dettaglio |
| 5. Firewall nftables | DA FARE | Nessun ruleset fisico verificato |
| 6. tcpdump | DA FARE | Nessuna cattura della nuova topologia documentata |
| 7. Suricata | DA FARE | Non installato o configurato per questa topologia |
| 8. Zeek | DA FARE | Non installato o configurato per questa topologia |
| 9. Python | DA FARE | Nessun analizzatore dei log ancora sviluppato |
| 10. Docker dashboard | DA FARE | Nessuno stack definitivo |
| 11. Test e hardening | DA FARE | Include riavvio, persistenza, comportamento con uplink assente e ripristino finale |

## Modifiche di rete applicate finora

Sono stati:

- creati e verificati i parametri del profilo `security-gateway-ap`;
- assegnato `10.42.0.1/24` alla Realtek durante l'attivazione;
- usato `ipv4.method shared` per il DHCP, DNS forwarding e NAT gestiti da NetworkManager;
- disabilitato IPv6 sul solo profilo hotspot iniziale;
- disabilitata l'attivazione automatica del profilo;
- verificati arresto, eliminazione e ricreazione del profilo;
- richiesto temporaneamente il dominio regolamentare italiano, con risultato effettivo `country 98: DFS-ETSI`.

Non sono ancora stati:

- applicati ruleset definitivi `nftables`;
- verificati isolamento tra client e protezione della rete domestica;
- separati manualmente DHCP, DNS, forwarding e NAT dagli automatismi di NetworkManager;
- installati o configurati Suricata e Zeek;
- verificati persistenza e comportamento dopo riavvio.

## Metodo didattico confermato

Per ogni fase vengono documentati:

1. scopo della fase;
2. teoria necessaria;
3. significato di ogni comando;
4. significato di opzioni e flag;
5. librerie e moduli usati negli script Python;
6. output atteso e interpretazione;
7. rischi e modifiche prodotte;
8. test di verifica;
9. rollback;
10. risultati realmente osservati.

Le configurazioni future non verranno indicate come completate finché non saranno state eseguite e verificate sull'ambiente di laboratorio.

## Vincoli di pubblicazione

Non pubblicare nel repository:

- SSID domestici reali;
- password Wi-Fi;
- indirizzi MAC completi;
- nomi `wlx...` completi quando incorporano un MAC;
- indirizzo IPv4 completo dell'host quando non necessario;
- catture PCAP non revisionate;
- log grezzi contenenti dati di dispositivi reali;
- file `.env` con valori locali;
- backup locali completi dei profili NetworkManager.

## Prossima azione

Iniziare la fase 4 e procedere in questo ordine:

```text
1. verificare configurazione IP, gateway e DNS ricevuti dal client
2. osservare il servizio DHCP usato da NetworkManager
3. controllare lo stato del forwarding IPv4
4. identificare le regole NAT create dalla connessione shared
5. verificare separatamente accesso per IP e risoluzione DNS
6. documentare il percorso client -> Realtek -> Ubuntu -> MediaTek -> Internet
```

La fase 4 dovrà distinguere chiaramente ciò che NetworkManager configura automaticamente da ciò che verrà successivamente controllato tramite `nftables`.