# Lavoro svolto e prossimi passi

## 1. Funzione del documento

Questo file riassume l'evoluzione reale del progetto e chiarisce il rapporto tra:

- il primo laboratorio virtuale con Kali e Parrot;
- il gateway fisico Ubuntu con MediaTek e Realtek;
- la roadmap attuale nelle guide numerate.

Per lo stato operativo più aggiornato usare [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md). Per i comandi, i test e i rollback usare i documenti nella cartella [`steps`](steps).

---

## 2. Evoluzione del progetto

### 2.1 Prima impostazione: laboratorio virtuale

Il progetto è nato come laboratorio KVM/QEMU gestito con libvirt e virt-manager:

```text
Parrot VM
10.10.10.3/24
Gateway 10.10.10.2
       |
       | rete isolata lab-lan
       v
Kali VM
eth1: 10.10.10.2/24 LAN
eth0: DHCP sulla rete libvirt default
       |
       v
Ubuntu host
       |
       v
Internet
```

In questo modello:

- Kali svolge il ruolo di gateway;
- Parrot svolge il ruolo di client;
- Parrot non deve avere una seconda interfaccia sulla rete `default`;
- routing, forwarding, firewall e NAT devono essere configurati dentro Kali.

### 2.2 Stato verificato del laboratorio virtuale

Sono stati verificati:

- presenza di KVM/QEMU, libvirt e virt-manager;
- rete libvirt `default`;
- rete isolata `lab-lan`;
- seconda interfaccia virtuale della VM Kali;
- `eth0` di Kali come WAN tramite DHCP;
- `eth1` di Kali come LAN statica `10.10.10.2/24`;
- separazione dei profili NetworkManager;
- connettività Internet dalla VM Kali.

Non sono ancora documentati come completati:

- configurazione definitiva di Parrot su `lab-lan`;
- percorso obbligatorio Parrot → Kali → Internet;
- firewall e NAT definitivi dentro Kali;
- monitoraggio completo del laboratorio virtuale.

Il laboratorio virtuale resta disponibile come ambiente secondario isolato, ma non è più la sequenza principale della roadmap.

---

## 3. Percorso attuale: gateway fisico Ubuntu

Il progetto è proseguito direttamente sull'hardware reale:

```text
Telefono / portatile autorizzato
              |
              | SecurityGatewayLab
              | 10.42.0.0/24
              v
Realtek RTL8812AU USB
modalità Access Point
              |
              | 10.42.0.1
              v
Ubuntu gateway
              |
              v
MediaTek MT7922 / wlp13s0
              |
              v
Router domestico
              |
              v
Internet
```

Ubuntu ha quindi assunto il ruolo che Kali avrebbe avuto nel laboratorio virtuale; il telefono o portatile collegato all'hotspot assume il ruolo del client Parrot.

---

## 4. Fase 1 completata: inventario hardware e rete

Sono stati verificati:

- Ubuntu 26.04 LTS;
- kernel `7.0.0-27-generic`;
- MediaTek MT7922 come uplink Internet;
- driver MediaTek `mt7921e`;
- Realtek RTL8812AU USB come interfaccia hotspot;
- driver Realtek `rtw88_8812au`;
- supporto dichiarato delle modalità `managed`, `AP`, `AP/VLAN` e `monitor`;
- assenza di blocchi `rfkill`;
- reti Docker e libvirt già presenti;
- route predefinita tramite `wlp13s0`.

Il nome completo `wlx...`, gli indirizzi MAC, gli SSID domestici e gli indirizzi completi non necessari non vengono pubblicati.

---

## 5. Fase 2 completata: topologia e piano IP

È stato approvato e verificato il piano:

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
DHCP_START=10.42.0.50
DHCP_END=10.42.0.200
DHCP_LEASE_SECONDS=3600
DNS_SERVER=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
IPV6_MODE=disabled-on-hotspot-initially
```

La subnet non risultava in conflitto con:

- rete dell'uplink;
- reti libvirt;
- reti Docker;
- indirizzi e rotte attive;
- profili NetworkManager osservati.

---

## 6. Fase 3 completata: hotspot Realtek

È stato creato il profilo:

```text
security-gateway-ap
```

Parametri verificati:

```text
connection.autoconnect=no
802-11-wireless.mode=ap
802-11-wireless.band=bg
802-11-wireless.channel=6
802-11-wireless-security.key-mgmt=wpa-psk
ipv4.method=shared
ipv4.addresses=10.42.0.1/24
ipv4.never-default=yes
ipv6.method=disabled
```

Risultati osservati:

- Realtek passata da `managed` a `AP`;
- SSID `SecurityGatewayLab` visibile;
- canale 6 a 2437 MHz;
- client reali autenticati, autorizzati e associati;
- almeno un client con indirizzo `10.42.0.x` valido;
- gateway `10.42.0.1` raggiunto dal client;
- richiesta HTTP ricevuta con risposta `200`;
- navigazione Internet osservata dal telefono;
- MediaTek rimasta la route predefinita dell'host;
- stato NetworkManager salvato localmente con segreti nascosti;
- hotspot fermato e riattivato;
- profilo eliminato e ricreato con successo;
- comportamento dopo riavvio verificato.

Dopo il riavvio:

```text
security-gateway-ap presente
connection.autoconnect=no
Realtek disconnessa
nessun 10.42.0.1 assegnato automaticamente
wlp13s0 collegata
route Internet tramite wlp13s0
```

Il profilo resta disponibile e viene attivato manualmente:

```bash
sudo nmcli connection up security-gateway-ap
```

Per fermarlo:

```bash
sudo nmcli connection down security-gateway-ap
```

La password WPA non è riportata nel repository.

---

## 7. Perché il telefono naviga già

Il profilo usa:

```text
ipv4.method=shared
```

NetworkManager ha quindi predisposto automaticamente una condivisione IPv4 che comprende, in modo iniziale:

- assegnazione degli indirizzi ai client;
- inoltro DNS;
- forwarding IPv4;
- NAT/masquerading verso la connessione predefinita.

Il percorso osservato è:

```text
client 10.42.0.x
  -> Realtek 10.42.0.1
  -> Ubuntu
  -> forwarding e NAT gestiti da NetworkManager
  -> wlp13s0
  -> router 192.168.10.1
  -> Internet
```

Questo dimostra il funzionamento empirico, ma non sostituisce l'analisi dettagliata prevista nella fase 4.

---

## 8. Stato corrente delle fasi

| Fase | Stato | Risultato |
|---:|---|---|
| 1. Inventario hardware e rete | COMPLETATA | Interfacce, hardware, driver, route e supporto AP verificati |
| 2. Topologia e indirizzamento | COMPLETATA | Subnet, gateway, profilo, banda e canale definiti |
| 3. Hotspot Realtek | COMPLETATA | Client reali collegati, gateway raggiunto, Internet e rollback verificati |
| 4. DHCP, routing e NAT | PROSSIMA | Osservare e documentare gli automatismi di `ipv4.method=shared` |
| 5. Firewall nftables | DA FARE | Applicare regole stateful e protezione tra le reti |
| 6. tcpdump | DA FARE | Osservare il traffico sui lati hotspot e uplink |
| 7. Suricata | DA FARE | Generare e analizzare eventi IDS |
| 8. Zeek | DA FARE | Produrre log di rete strutturati |
| 9. Python | DA FARE | Analizzare log e generare report commentati |
| 10. Docker | DA FARE | Database e dashboard senza routing privilegiato |
| 11. Test e hardening | DA FARE | Persistenza completa, backup, isolamento e ripristino finale |

---

## 9. Prossimi passi immediati

La prossima attività è la fase 4, documentata in [`steps/04-dhcp-routing-nat.md`](steps/04-dhcp-routing-nat.md).

L'ordine previsto è:

1. attivare manualmente `security-gateway-ap`;
2. verificare indirizzo, gateway e DNS ricevuti dal client;
3. osservare i processi e le configurazioni create da NetworkManager;
4. controllare lo stato di `net.ipv4.ip_forward`;
5. ispezionare route e regole NAT senza modificarle alla cieca;
6. osservare una connessione con `conntrack`;
7. verificare separatamente accesso tramite IP e risoluzione DNS;
8. documentare rollback e dipendenze;
9. passare al firewall solo dopo aver compreso il percorso attuale.

---

## 10. Ruolo futuro di Python

Python verrà introdotto dopo la produzione di dati e log reali. Gli script dovranno essere didattici e includere:

- docstring;
- import e librerie spiegati;
- funzioni piccole;
- commenti utili;
- gestione degli errori;
- percorsi configurabili;
- output JSON o CSV;
- dati anonimizzati;
- test quando il programma diventa stabile.

Primi strumenti previsti:

- inventario di interfacce e route;
- controllo della coerenza del gateway;
- lettura dei contatori `nftables`;
- analisi di `eve.json` di Suricata;
- analisi dei log Zeek;
- produzione di report temporali.

---

## 11. Ruolo futuro di Docker

Docker verrà usato per servizi applicativi:

- database;
- dashboard;
- importazione dei log;
- metriche e visualizzazione.

Non gestirà inizialmente il routing del gateway. Non verranno assegnati `NET_ADMIN`, rete host o modalità privilegiata senza una necessità tecnica verificata.

---

## 12. Report pubblici e privati

Nel repository vengono conservati soltanto:

- documentazione revisionata;
- configurazioni verificate senza segreti;
- output brevi e anonimizzati;
- immagini ricostruite o oscurate.

La cartella locale:

```text
reports/
```

è ignorata da Git e può contenere:

- report privati completi;
- nomi reali delle interfacce;
- output integrali;
- screenshot originali;
- dati necessari al ripristino.

Anche nei report privati è preferibile non duplicare password quando NetworkManager le conserva già in modo protetto.

---

## 13. Regole di sicurezza

Il laboratorio deve essere usato soltanto con:

- sistemi propri;
- dispositivi autorizzati;
- reti controllate;
- traffico per il quale si possiede consenso.

Non pubblicare password, token, chiavi private, SSID domestici, MAC reali non necessari, log grezzi, PCAP non revisionati o contenuti appartenenti a terzi.
