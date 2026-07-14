# Stato attuale del progetto

Ultimo aggiornamento operativo: 14 luglio 2026.

## Obiettivo principale

Costruire un gateway fisico Ubuntu nel quale:

- la scheda Wi-Fi interna MediaTek fornisce l'uscita Internet;
- la scheda Wi-Fi USB Realtek crea l'hotspot per i dispositivi di laboratorio;
- Ubuntu esegue routing, firewall, NAT e monitoraggio;
- Suricata e Zeek producono eventi e log;
- Python analizza i log;
- Docker ospita database e dashboard senza gestire direttamente il routing principale.

## Fase 1: risultati verificati

La raccolta aggiornata è stata eseguita su:

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
Gateway predefinito: 192.168.10.1
Stato: collegato e usato per Internet
Radio: phy1
```

Il nome della rete Wi-Fi domestica e gli indirizzi MAC non vengono registrati nel repository pubblico.

### Interfaccia hotspot prevista

```text
Interfaccia pubblica: wlx<REDACTED>
Hardware: Realtek RTL8812AU
USB ID: 0bda:8812
Stato: disconnesso
Modalità attuale: managed
Radio: phy8
IPv4: non assegnato
rfkill: nessun blocco software o hardware
```

La Realtek risulta libera e non viene usata come uscita Internet.

### Reti virtuali presenti

```text
192.168.122.0/24   libvirt default
10.10.10.0/24      rete isolata libvirt
172.17.0.0/16      Docker predefinita
172.18.0.0/16      bridge Docker personalizzato
```

Sono inoltre presenti interfacce `vnet` associate a macchine virtuali attive. La subnet futura dell'hotspot dovrà evitare queste reti.

## Verifiche ancora necessarie per chiudere la fase 1

Restano due controlli di sola lettura sulla Realtek:

```bash
sudo ethtool -i wlx00c0cab4ed2d
iw phy phy8 info | grep -A 15 "Supported interface modes"
```

Devono confermare:

- il driver Realtek effettivamente caricato sul kernel corrente;
- la presenza della modalità `AP`.

## Stato delle fasi

| Fase | Stato | Nota |
|---:|---|---|
| 1. Inventario hardware e rete | IN CORSO | Raccolta principale completata; mancano driver Realtek e controllo `AP` aggiornato |
| 2. Topologia e indirizzamento | DA FARE | Le reti esistenti sono note; manca la scelta definitiva della subnet hotspot |
| 3. Hotspot Realtek | DA FARE | Nessun hotspot stabile verificato |
| 4. DHCP, routing e NAT | DA FARE | Nessun client fisico ha ancora navigato attraverso Ubuntu |
| 5. Firewall nftables | DA FARE | Nessun ruleset fisico verificato |
| 6. tcpdump | DA FARE | Nessuna cattura della nuova topologia documentata |
| 7. Suricata | DA FARE | Non installato o configurato per questa topologia |
| 8. Zeek | DA FARE | Non installato o configurato per questa topologia |
| 9. Python | DA FARE | Nessun analizzatore dei log ancora sviluppato |
| 10. Docker dashboard | DA FARE | Nessuno stack definitivo |
| 11. Test e hardening | DA FARE | Dipende dalle fasi precedenti |

## Vincoli di pubblicazione

Non pubblicare nel repository:

- SSID reali;
- password Wi-Fi;
- indirizzi MAC completi;
- nomi `wlx...` completi quando incorporano un MAC;
- catture PCAP non revisionate;
- log grezzi contenenti dati di dispositivi reali;
- file `.env` con valori locali.

## Prossima azione

Eseguire i due controlli Realtek indicati sopra. Dopo la conferma, la fase 1 potrà essere marcata `COMPLETATA` e inizierà la fase 2: scelta della topologia e della subnet per l'hotspot.
