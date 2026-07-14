# Linux Gateway Security Lab

Laboratorio didattico per imparare networking Linux, sicurezza di rete e Python costruendo progressivamente un gateway controllato.

> Il progetto deve essere usato esclusivamente su sistemi propri, reti di laboratorio e ambienti autorizzati.

## Stato reale del progetto

Al momento è stata configurata la base di rete della VM Kali:

```text
eth0  WAN  192.168.122.223/24  DHCP  gateway 192.168.122.1
eth1  LAN  10.10.10.2/24       statico, nessun gateway
```

Sono stati verificati:

- collegamento di Kali alla rete libvirt `default`;
- collegamento di Kali alla rete isolata `lab-lan`;
- accesso Internet dalla WAN di Kali;
- profilo NetworkManager `wan-dhcp` associato a `eth0`;
- profilo NetworkManager `lab-lan-static` associato a `eth1`.

Non sono ancora stati realizzati:

- configurazione di Parrot;
- forwarding IPv4;
- firewall `nftables`;
- NAT/masquerading;
- monitoraggio del traffico;
- script Python;
- dashboard Docker;
- hotspot fisico completo.

## Documentazione

La documentazione è divisa intenzionalmente in due file.

### 1. Obiettivi e progetto

[`docs/OBIETTIVI_E_PROGETTO.md`](docs/OBIETTIVI_E_PROGETTO.md)

Descrive:

- cosa si vuole costruire;
- obiettivi didattici e tecnici;
- architettura virtuale prevista;
- evoluzione fisica futura;
- ruolo di Python e Docker;
- criteri di completamento;
- limiti di sicurezza.

Le funzioni descritte in questo file sono **obiettivi**, non attività già completate.

### 2. Lavoro svolto e prossimi passi

[`docs/LAVORO_SVOLTO_E_PROSSIMI_PASSI.md`](docs/LAVORO_SVOLTO_E_PROSSIMI_PASSI.md)

Contiene:

- inventario realmente eseguito;
- comandi realmente usati;
- spiegazione delle opzioni e delle flag;
- teoria necessaria per comprendere i risultati;
- errori incontrati e relative soluzioni;
- output verificati;
- stato attuale preciso;
- elenco esplicito delle attività non ancora eseguite;
- prossimi passi ordinati.

## Architettura prevista

```text
Internet
   |
Ubuntu host
   |
rete libvirt default
   |
Kali
|-- eth0: WAN
`-- eth1: LAN 10.10.10.2/24
        |
        `-- lab-lan isolata
                |
                `-- Parrot, ancora da configurare
```

## Metodo di lavoro

Ogni fase deve essere verificata prima di passare alla successiva:

```text
interfacce
  -> indirizzi
  -> rotte
  -> collegamento client-gateway
  -> forwarding
  -> firewall
  -> NAT
  -> DNS
  -> monitoraggio
  -> Python
  -> Docker
  -> gateway fisico
```

## Dati pubblici e privacy

Nel repository pubblico non devono essere pubblicati:

- SSID domestici;
- password;
- token;
- chiavi private;
- indirizzi MAC reali non necessari;
- file `.env` reali;
- log non revisionati;
- traffico appartenente a terzi.

Gli indirizzi `10.10.10.0/24` e `192.168.122.0/24` sono reti private usate nel laboratorio.

## Licenza

Il progetto è distribuito con licenza MIT.
