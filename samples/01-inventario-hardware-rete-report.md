# Report pubblico anonimizzato — Fase 1

Data verifica: 15 luglio 2026  
Fase: inventario hardware e rete  
Esito: completata e verificata

## Scopo

Identificare il sistema Ubuntu, le interfacce di rete, l'hardware, i driver, l'uplink Internet e la scheda Realtek destinata all'hotspot, senza modificare la configurazione.

## Ambiente verificato

```text
Sistema operativo: Ubuntu 26.04 LTS
Kernel: 7.0.0-27-generic
Architettura: x86_64
```

Hostname, identificativi macchina, indirizzi MAC completi e SSID domestici sono stati rimossi dal report pubblico.

## Interfacce principali

### Uplink Internet

```text
Interfaccia: wlp13s0
Hardware: MediaTek MT7922 802.11ax
Driver: mt7921e
Stato: collegato
Ruolo: uscita Internet dell'host
Rete osservata: 192.168.10.0/24
Gateway: 192.168.10.1
```

### Interfaccia destinata all'hotspot

```text
Interfaccia: wlx<REDACTED>
Hardware: Realtek RTL8812AU
USB ID: 0bda:8812
Driver: rtw88_8812au
Stato iniziale: disconnesso
Modalità iniziale: managed
IPv4 iniziale: non assegnato
Supporto AP dichiarato: sì
rfkill: nessun blocco software o hardware
```

### Ethernet disponibile

```text
Hardware: Realtek RTL8125 2.5GbE
Stato osservato: senza portante
Ruolo futuro possibile: LAN cablata
```

## Reti e bridge osservati

```text
lo                    loopback
wlp13s0               Wi-Fi uplink
wlx<REDACTED>          Realtek USB
<ETHERNET_IF>          Ethernet senza portante
docker0               bridge Docker
br-<REDACTED>          bridge Docker personalizzato
virbr0                rete libvirt default
virbr1                rete libvirt isolata
```

## Capacità Wi-Fi verificate

La radio Realtek dichiarava supporto alle modalità:

```text
managed
AP
AP/VLAN
monitor
```

Il supporto dichiarato non provava ancora la stabilità dell'hotspot, ma confermava che il driver esponeva la modalità Access Point al kernel.

## Comandi principali usati

```bash
hostnamectl
ip -br link
ip -4 -br address
ip -4 route
nmcli device status
nmcli connection show
sudo lshw -class network -short
lsusb
lsusb -t
sudo ethtool -i <AP_IF>
iw dev
iw dev <AP_IF> info
iw list
rfkill list
```

## Significato essenziale

- `ip -br link` mostra interfacce e stato del collegamento;
- `ip -4 -br address` mostra gli indirizzi IPv4;
- `ip -4 route` mostra le rotte e il gateway predefinito;
- `nmcli device status` distingue dispositivi e profili attivi;
- `lshw` identifica l'hardware di rete;
- `ethtool -i` mostra il driver associato;
- `iw` interroga il sottosistema wireless;
- `rfkill` controlla eventuali blocchi radio.

## Privacy applicata

Sono stati rimossi o mascherati:

- hostname personale;
- SSID domestico;
- indirizzi MAC;
- nome completo dell'interfaccia `wlx...`;
- indirizzo IPv4 completo dell'host;
- identificativi macchina e firmware non necessari.

## Esito

- [x] sistema operativo e kernel identificati;
- [x] uplink Internet identificato;
- [x] MediaTek e relativo driver verificati;
- [x] Realtek USB e relativo driver verificati;
- [x] supporto della modalità AP dichiarato;
- [x] stato IPv4 e route predefinita verificati;
- [x] bridge Docker e reti libvirt osservati;
- [x] nessuna configurazione di rete modificata;
- [x] dati pubblici anonimizzati.

## Conclusione

La MediaTek è stata confermata come uplink Internet dell'host Ubuntu. La Realtek RTL8812AU è risultata libera, gestita dal driver `rtw88_8812au` e capace di operare in modalità Access Point. Questi risultati hanno permesso di passare alla progettazione della topologia e dell'indirizzamento della fase 2.
