# Linux Gateway Security Lab

Laboratorio didattico e tecnico per costruire, comprendere e documentare un **gateway Linux controllato** con routing IPv4, NAT, firewall `nftables`, monitoraggio del traffico e futura integrazione Docker.

> Il progetto è destinato esclusivamente a sistemi propri, reti di laboratorio e ambienti per i quali si dispone di autorizzazione esplicita.

## Obiettivo

Il progetto crea un percorso di rete obbligatorio nel quale una macchina client isolata deve attraversare una macchina Linux configurata come gateway prima di raggiungere Internet.

```text
Internet
   |
Ubuntu host
   |
rete libvirt "default" — NAT — 192.168.122.0/24
   |
Kali gateway
|-- eth0: WAN, DHCP
`-- eth1: LAN, 10.10.10.2/24
       |
       `-- rete isolata "lab-lan" — 10.10.10.0/24
               |
               `-- Parrot client — 10.10.10.3/24
                   gateway: 10.10.10.2
```

Il gateway dovrà:

- collegare due reti IP differenti;
- inoltrare pacchetti dalla LAN verso la WAN;
- applicare una politica firewall esplicita;
- eseguire NAT tramite masquerading;
- mantenere lo stato delle connessioni;
- registrare pacchetti, byte, errori e destinazioni;
- fornire dati a script Python e servizi Docker;
- essere successivamente trasferibile a un gateway fisico con due schede di rete.

## Stato del progetto

### Completato

- [x] inventario delle interfacce dell'host Ubuntu;
- [x] identificazione della scheda Wi-Fi interna MediaTek MT7922;
- [x] identificazione della scheda Wi-Fi USB Realtek RTL8812AU;
- [x] verifica del driver Linux `rtw88_8812au`;
- [x] verifica della modalità Access Point tramite NetworkManager e `iw`;
- [x] verifica della radio `phy2`/`wiphy 2`;
- [x] verifica della rete libvirt `default` con NAT;
- [x] creazione della rete isolata `lab-lan`;
- [x] aggiunta della seconda interfaccia virtuale a Kali;
- [x] configurazione della WAN di Kali tramite DHCP;
- [x] configurazione della LAN di Kali con indirizzo statico;
- [x] verifica della connettività Internet dalla VM gateway;
- [x] separazione dei profili NetworkManager `wan-dhcp` e `lab-lan-static`.

### Da completare

- [ ] collegare Parrot esclusivamente a `lab-lan`;
- [ ] assegnare a Parrot `10.10.10.3/24`;
- [ ] impostare `10.10.10.2` come gateway del client;
- [ ] abilitare `net.ipv4.ip_forward` su Kali;
- [ ] applicare le regole firewall `nftables`;
- [ ] applicare il masquerading sulla WAN;
- [ ] verificare il percorso end-to-end;
- [ ] aggiungere contatori e logging;
- [ ] creare un analizzatore Python dei dati;
- [ ] integrare una dashboard Docker;
- [ ] provare il gateway fisico con una scheda verso Internet e una verso l'hotspot.

## Stato verificato della VM gateway

```text
eth0  192.168.122.223/24  profilo wan-dhcp
eth1  10.10.10.2/24       profilo lab-lan-static
```

Tabella di routing osservata:

```text
default via 192.168.122.1 dev eth0 proto dhcp src 192.168.122.223 metric 100
10.10.10.0/24 dev eth1 proto kernel scope link src 10.10.10.2 metric 101
192.168.122.0/24 dev eth0 proto kernel scope link src 192.168.122.223 metric 100
```

Gli indirizzi appartengono a reti private di laboratorio. Nella documentazione pubblica non vengono pubblicati SSID, password, token, chiavi, indirizzi MAC reali o altri dati sensibili della rete domestica.

## Tecnologie

- Ubuntu host
- KVM/QEMU
- libvirt
- virt-manager
- Kali Linux come gateway
- Parrot OS come client
- NetworkManager e `nmcli`
- iproute2: `ip link`, `ip address`, `ip route`, `ip neigh`
- `iw` e `ethtool`
- `nftables`
- `tcpdump`
- Docker e Docker Compose per i futuri servizi applicativi
- Python per report e analisi

## Perché VM e Docker vengono usati insieme

La macchina virtuale isola il piano di rete:

```text
Kali VM
|-- kernel della VM
|-- interfacce virtuali
|-- routing
|-- forwarding
`-- nftables
```

Docker verrà usato per il piano applicativo:

```text
Docker
|-- dashboard
|-- database
|-- analizzatore Python
`-- esportazione di metriche
```

Un container condivide il kernel dell'host. Usarlo immediatamente come router richiederebbe capacità elevate come `NET_ADMIN`, rete host o modalità privilegiata. Per lo studio delle basi, una VM è più chiara e riduce il rischio di modificare la rete dell'host.

## Struttura del repository

```text
.
|-- README.md
|-- LICENSE
|-- SECURITY.md
|-- CONTRIBUTING.md
|-- docs/
|   |-- REPORT.md
|   |-- ARCHITECTURE.md
|   |-- COMMAND_REFERENCE.md
|   `-- TROUBLESHOOTING.md
|-- configs/
|   `-- nftables/
|       `-- gateway.nft.example
`-- scripts/
    `-- collect-network-state.sh
```

## Documentazione principale

- [`docs/REPORT.md`](docs/REPORT.md): report completo, teoria, lavoro svolto, errori risolti e roadmap;
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): topologia, ruoli e flusso dei pacchetti;
- [`docs/COMMAND_REFERENCE.md`](docs/COMMAND_REFERENCE.md): spiegazione dei comandi e delle opzioni;
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md): metodo diagnostico a strati;
- [`configs/nftables/gateway.nft.example`](configs/nftables/gateway.nft.example): ruleset didattico commentato;
- [`scripts/collect-network-state.sh`](scripts/collect-network-state.sh): raccolta non distruttiva dello stato di rete.

## Sicurezza prima degli esperimenti

1. creare uno snapshot delle VM;
2. mantenere aperta la console di virt-manager;
3. verificare su quale macchina viene eseguito ogni comando;
4. salvare lo stato iniziale di indirizzi, rotte e ruleset;
5. evitare `nft flush ruleset` sull'host;
6. non pubblicare file `.env`, chiavi private, password o log non revisionati;
7. usare soltanto reti proprie o autorizzate.

## Licenza

Il progetto è distribuito con licenza MIT. La licenza permette uso, modifica e redistribuzione, mantenendo l'avviso di copyright e la licenza originale.