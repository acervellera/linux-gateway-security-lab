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

### Interfaccia hotspot prevista

```text
Interfaccia pubblica: wlx<REDACTED>
Hardware: Realtek RTL8812AU
USB ID: 0bda:8812
Driver: rtw88_8812au
Versione riportata: 7.0.0-27-generic
Bus USB: 2-5.1:1.0
Stato: disconnesso
Modalità attuale: managed
Supporto AP dichiarato: sì
IPv4: non assegnato
rfkill: nessun blocco software o hardware
```

La Realtek risulta libera, non viene usata come uscita Internet e dichiara supporto alla modalità Access Point.

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

La scansione Wi-Fi ha mostrato occupazione locale sui canali 1 e 10 della banda 2,4 GHz. Il canale 6 è stato scelto come punto di partenza per il collaudo; la qualità reale dovrà essere verificata con un client collegato.

Il dominio regolamentare osservato era `GB`. Prima di attivare l'hotspot dovrà essere impostato e verificato `IT`, senza modificare inutilmente la connettività dell'uplink.

### Percorso previsto

```text
client 10.42.0.x
  -> Realtek USB / hotspot
  -> firewall nella chain forward
  -> routing IPv4
  -> NAT/masquerading
  -> wlp13s0
  -> router 192.168.10.1
  -> Internet
```

Il percorso è stato progettato ma non ancora collaudato end-to-end. Hotspot, DHCP operativo, forwarding, NAT e firewall appartengono alle fasi successive.

## Stato delle fasi

| Fase | Stato | Nota |
|---:|---|---|
| 1. Inventario hardware e rete | COMPLETATA | Uplink MediaTek e Realtek AP identificati; driver, route, rfkill e modalità `AP` verificati |
| 2. Topologia e indirizzamento | COMPLETATA | Subnet, gateway, DHCP, DNS, profilo, banda, canale e percorso dei pacchetti definiti senza conflitti locali |
| 3. Hotspot Realtek | PROSSIMA | Correggere il dominio regolamentare, creare il profilo e collegare un client autorizzato |
| 4. DHCP, routing e NAT | DA FARE | Nessun client fisico ha ancora navigato attraverso Ubuntu |
| 5. Firewall nftables | DA FARE | Nessun ruleset fisico verificato |
| 6. tcpdump | DA FARE | Nessuna cattura della nuova topologia documentata |
| 7. Suricata | DA FARE | Non installato o configurato per questa topologia |
| 8. Zeek | DA FARE | Non installato o configurato per questa topologia |
| 9. Python | DA FARE | Nessun analizzatore dei log ancora sviluppato |
| 10. Docker dashboard | DA FARE | Nessuno stack definitivo |
| 11. Test e hardening | DA FARE | Dipende dalle fasi precedenti |

## Modifiche di rete applicate finora

Le fasi 1 e 2 hanno usato soltanto comandi di osservazione.

Non sono ancora stati:

- creati profili hotspot persistenti;
- assegnati indirizzi alla Realtek;
- attivati forwarding o NAT;
- applicati ruleset `nftables`;
- modificati DNS del sistema;
- modificato il dominio regolamentare.

## Metodo didattico confermato

Per ogni fase verranno documentati:

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
- file `.env` con valori locali.

## Prossima azione

Iniziare la fase 3 e procedere in questo ordine:

```text
1. verificare e correggere il dominio regolamentare a IT
2. creare security-gateway-ap sulla Realtek USB
3. impostare SecurityGatewayLab, banda 2.4 GHz, canale 6
4. collegare un solo client autorizzato
5. verificare associazione, indirizzo IP e disconnessione
6. provare il rollback eliminando il profilo quando richiesto
```

La fase 3 non dovrà essere indicata come completata finché un client reale non sarà riuscito ad associarsi in modo stabile e il profilo non sarà stato verificato e documentato.
