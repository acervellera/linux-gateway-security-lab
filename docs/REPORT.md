# Report tecnico completo — Linux Gateway Security Lab

**Scopo:** costruire e studiare un gateway Linux con routing, NAT, firewall, monitoraggio e futura integrazione Docker.  
**Host:** Ubuntu.  
**Virtualizzazione:** KVM/QEMU, libvirt e virt-manager.  
**Gateway di laboratorio:** Kali Linux.  
**Client di laboratorio:** Parrot OS.  
**Stato documentato:** WAN e LAN della VM gateway configurate; client, forwarding e NAT ancora da completare.

---

## Indice

1. Scopo complessivo
2. Risultato finale desiderato
3. Metodo di lavoro e motivazione del laboratorio virtuale
4. Perché non usare soltanto Docker
5. Teoria di rete fondamentale
6. Router, gateway, bridge, firewall, NAT, proxy e hotspot
7. Inventario tecnico dell'host Ubuntu
8. Analisi della scheda Wi-Fi USB
9. Ambiente KVM/libvirt
10. Lavoro realizzato nella VM Kali
11. Problemi incontrati e diagnosi
12. Stato attuale verificato
13. Prossimi passi operativi
14. Teoria di `nftables` e connection tracking
15. Monitoraggio e raccolta dati
16. Ruolo futuro di Docker e Python
17. Passaggio futuro al gateway fisico
18. Sicurezza operativa e pubblicazione
19. Troubleshooting professionale
20. Roadmap e criteri di completamento

---

# 1. Scopo complessivo

Il progetto nasce dall'esigenza di far uscire il traffico di uno o più dispositivi attraverso un unico punto controllato. Tale punto deve essere in grado di osservare, filtrare e misurare le connessioni senza dipendere dal singolo programma installato sul client.

Il componente centrale sarà un **gateway Linux**. Un gateway collega reti differenti e diventa il passaggio necessario per raggiungere una destinazione esterna. Nel laboratorio, la rete interna non avrà un collegamento diretto a Internet: il client dovrà inviare i pacchetti alla macchina Kali, che li inoltrerà sulla propria interfaccia esterna.

Il progetto dovrà permettere di:

- comprendere il funzionamento delle interfacce di rete Linux;
- distinguere livello di collegamento, livello IP e livello applicativo;
- interpretare indirizzi MAC, IPv4, subnet e rotte;
- configurare una macchina con due interfacce e due ruoli diversi;
- abilitare l'inoltro IPv4;
- applicare una politica firewall esplicita;
- eseguire il NAT tramite masquerading;
- mantenere lo stato delle connessioni;
- visualizzare pacchetti, byte, protocolli e porte;
- creare report con Python;
- usare Docker per dashboard, database e servizi di analisi;
- trasferire in futuro la configurazione su hardware reale.

Il sistema non è pensato per intercettare comunicazioni altrui. Deve essere utilizzato esclusivamente su dispositivi e reti propri o autorizzati.

---

# 2. Risultato finale desiderato

## 2.1 Laboratorio virtuale

La topologia di laboratorio è:

```text
Internet
   |
   v
Ubuntu host
   |
   | rete libvirt "default"
   | subnet 192.168.122.0/24
   | DHCP e NAT forniti da libvirt
   |
   v
Kali gateway
|-- eth0: WAN
|   |-- IPv4 via DHCP
|   |-- indirizzo osservato: 192.168.122.223/24
|   `-- gateway: 192.168.122.1
|
`-- eth1: LAN
    |-- IPv4 statico: 10.10.10.2/24
    |-- nessun gateway predefinito
    `-- rete isolata "lab-lan"
             |
             v
          Parrot client
          |-- IPv4 previsto: 10.10.10.3/24
          |-- gateway previsto: 10.10.10.2
          `-- nessuna interfaccia sulla rete default
```

Il percorso previsto di un pacchetto sarà:

```text
Parrot 10.10.10.3
        |
        | pacchetto destinato a Internet
        v
Kali eth1 10.10.10.2
        |
        | controllo firewall
        | routing
        | NAT/masquerade
        v
Kali eth0 192.168.122.223
        |
        v
Gateway libvirt 192.168.122.1
        |
        v
Ubuntu host
        |
        v
Internet
```

Le risposte seguiranno il percorso inverso. Il connection tracking del kernel consentirà a Kali di associare le risposte alla connessione originata dal client interno.

## 2.2 Evoluzione fisica

Dopo il completamento del laboratorio virtuale, lo stesso modello potrà essere applicato a due schede reali:

```text
Router domestico
       |
       | Wi-Fi o Ethernet verso Internet
       v
Ubuntu gateway fisico
|-- interfaccia WAN
|-- routing e NAT
|-- firewall
|-- monitoraggio
|-- servizi Docker
`-- interfaccia LAN / hotspot Wi-Fi
       |
       v
Telefono, portatile o dispositivi IoT
```

La fase virtuale serve a verificare le regole senza rischiare di interrompere la rete dell'host principale.

---

# 3. Metodo di lavoro e motivazione del laboratorio virtuale

Configurare routing e firewall direttamente sull'Ubuntu principale è possibile, ma un errore potrebbe rimuovere la rotta predefinita, bloccare DNS, interrompere Docker o applicare una politica `drop` senza eccezioni corrette.

KVM e libvirt permettono di confinare gli esperimenti. La VM Kali dispone di:

- proprio kernel;
- proprie interfacce;
- propria tabella di routing;
- propri parametri `sysctl`;
- proprio ruleset `nftables`;
- console virtuale utilizzabile anche se la rete non funziona;
- snapshot ripristinabili.

Il metodo adottato è incrementale:

1. inventario dell'hardware e delle interfacce;
2. verifica della connettività esterna;
3. creazione della rete interna isolata;
4. assegnazione degli indirizzi;
5. test locale tra client e gateway;
6. attivazione del forwarding;
7. introduzione del firewall;
8. introduzione del NAT;
9. verifica end-to-end;
10. aggiunta di monitoraggio e automazione.

Ogni livello viene testato prima di aggiungere il successivo. Questo evita di diagnosticare contemporaneamente problemi di indirizzamento, routing, DNS e firewall.

---

# 4. Perché non usare soltanto Docker

Docker è presente sull'host e sarà importante, ma non è la soluzione più chiara per il primo studio del routing.

Una VM dispone di un kernel virtualizzato indipendente. Un container condivide il kernel dell'host ed è isolato tramite namespace e cgroup. Per consentire a un container di amministrare una rete si ricorre spesso a opzioni come:

```yaml
cap_add:
  - NET_ADMIN
```

oppure:

```yaml
network_mode: host
```

oppure, in modo ancora più invasivo:

```yaml
privileged: true
```

Queste opzioni possono rendere più difficile capire dove vengono applicate le regole e aumentano il rischio di influire sull'host.

Nel sistema esistono già più livelli di NAT:

1. NAT del router domestico;
2. NAT della rete libvirt `default`;
3. futuro NAT della VM Kali;
4. NAT delle reti bridge Docker.

La scelta progettuale è quindi:

```text
Kali VM
    piano di rete:
    routing, forwarding, firewall, NAT

Docker
    piano applicativo:
    dashboard, database, analizzatore, proxy e report
```

In seguito Docker potrà essere installato anche dentro Kali, mantenendo però il routing principale nel sistema della VM.

---

# 5. Teoria di rete fondamentale

## 5.1 Interfaccia di rete

Un'interfaccia è un oggetto del kernel attraverso il quale vengono inviati e ricevuti dati. Può rappresentare:

- una scheda fisica Ethernet;
- una scheda Wi-Fi;
- una scheda virtuale di una VM;
- un bridge;
- un'interfaccia di un container;
- il loopback;
- un tunnel;
- una VLAN.

Sull'host sono state osservate interfacce fisiche, bridge libvirt e bridge Docker. Dentro Kali sono presenti `eth0`, `eth1`, `lo` e un'interfaccia wireless virtuale non utilizzata nel progetto.

## 5.2 Stato amministrativo e stato operativo

Nel risultato di `ip -br link` possono apparire più indicazioni:

- `UP`: interfaccia abilitata amministrativamente;
- `LOWER_UP`: collegamento fisico o virtuale effettivamente operativo;
- `DOWN`: interfaccia non operativa;
- `NO-CARRIER`: nessuna portante o collegamento;
- `UNKNOWN` su `lo`: normale, perché il loopback non ha un mezzo fisico.

Una scheda può essere `UP` ma non avere un indirizzo IPv4. Il livello di collegamento e l'indirizzamento IP sono aspetti distinti.

## 5.3 MAC e IPv4

Il MAC viene usato nel dominio locale di livello 2. L'indirizzo IPv4 viene usato per identificare un nodo in una rete logica e può essere instradato.

Nel repository pubblico gli indirizzi MAC reali sono omessi. Il nome locale dell'interfaccia USB, che incorporava il MAC, viene sostituito con il segnaposto `<USB_WIFI_IFACE>`.

## 5.4 Subnet e CIDR

La rete interna scelta è:

```text
10.10.10.0/24
```

`/24` indica una maschera di 24 bit, equivalente a:

```text
255.255.255.0
```

La subnet contiene:

```text
indirizzo di rete: 10.10.10.0
host tipici:        10.10.10.1 - 10.10.10.254
broadcast:          10.10.10.255
```

Nel laboratorio:

```text
10.10.10.2  Kali lato LAN
10.10.10.3  Parrot client previsto
```

## 5.5 Tabella di routing

La tabella di routing decide dove inviare ogni pacchetto. Viene scelta la rotta con il prefisso più specifico. La rotta `default` viene usata quando nessuna rotta più specifica corrisponde.

Lo stato osservato su Kali è:

```text
default via 192.168.122.1 dev eth0 proto dhcp src 192.168.122.223 metric 100
10.10.10.0/24 dev eth1 proto kernel scope link src 10.10.10.2 metric 101
192.168.122.0/24 dev eth0 proto kernel scope link src 192.168.122.223 metric 100
```

Interpretazione:

- `default`: destinazioni non coperte da altre rotte;
- `via 192.168.122.1`: next hop della WAN;
- `dev eth0`: interfaccia di uscita;
- `proto dhcp`: rotta ricevuta tramite DHCP;
- `proto kernel`: rotta creata dal kernel per una rete direttamente connessa;
- `scope link`: destinazione raggiungibile direttamente sul collegamento;
- `src`: indirizzo sorgente preferito;
- `metric`: costo della rotta; a parità di prefisso viene preferito il valore più basso.

## 5.6 DHCP

DHCP può fornire automaticamente:

- indirizzo IP;
- prefisso o maschera;
- gateway predefinito;
- DNS;
- durata della concessione.

La rete libvirt `default` fornisce DHCP. `lab-lan` è stata invece creata senza DHCP per rendere esplicita la configurazione degli indirizzi.

## 5.7 DNS

DNS traduce nomi come `debian.org` in indirizzi IP. Per diagnosticare la rete si esegue prima un test verso un IP pubblico e solo dopo un test verso un nome. Se l'IP funziona ma il nome no, il problema è probabilmente DNS e non routing.

## 5.8 ARP

In IPv4, ARP permette di trovare il MAC associato a un indirizzo IP locale. Il comando `ip neigh` mostra la tabella dei vicini. Un router sostituisce i MAC a ogni collegamento, mentre gli indirizzi IP vengono trattati dal livello di routing.

## 5.9 TCP, UDP e porte

TCP è orientato alla connessione e mantiene stato, sequenza e ritrasmissioni. UDP invia datagrammi senza creare una connessione equivalente.

Esempi comuni:

```text
TCP 22   SSH
TCP 80   HTTP
TCP 443  HTTPS
UDP 53   DNS tradizionale
UDP 123  NTP
```

Il firewall può filtrare per interfaccia, IP, protocollo, porta e stato della connessione.

---

# 6. Router, gateway, bridge, firewall, NAT, proxy e hotspot

## 6.1 Router e gateway

Un router inoltra pacchetti tra reti IP. Il termine gateway indica spesso il dispositivo usato come uscita da una rete. Nel laboratorio Kali ricopre entrambi i ruoli.

## 6.2 Bridge

Un bridge collega segmenti allo stesso livello Ethernet. Usa indirizzi MAC e non diventa automaticamente un router. `virbr0` e `docker0` sono esempi di bridge virtuali con funzioni aggiuntive gestite rispettivamente da libvirt e Docker.

## 6.3 Firewall

Un firewall decide quali pacchetti accettare o scartare. Il progetto utilizzerà una politica esplicita per il forwarding:

- consentire LAN verso WAN;
- consentire le risposte `established,related`;
- bloccare il resto.

## 6.4 NAT

NAT modifica indirizzi e, talvolta, porte. Per permettere al client `10.10.10.3` di uscire sulla WAN, Kali applicherà `masquerade`.

Prima del NAT:

```text
10.10.10.3:porta-client -> destinazione:porta
```

Dopo il NAT:

```text
192.168.122.223:porta-tradotta -> destinazione:porta
```

Le risposte vengono ricondotte al client originario grazie al connection tracking.

## 6.5 Proxy

Un proxy opera a livello applicativo. Può essere utile per HTTP, controllo degli accessi e log applicativi, ma non sostituisce un gateway generale per tutto il traffico TCP e UDP.

## 6.6 Hotspot

Un hotspot configura una radio Wi-Fi in modalità Access Point. Nel passaggio fisico, la scheda USB Realtek potrà offrire la rete controllata ai client, mentre un'altra interfaccia fornirà la WAN.

---

# 7. Inventario tecnico dell'host Ubuntu

L'host dispone delle seguenti categorie di interfacce:

| Componente | Modello/servizio | Ruolo osservato o futuro |
|---|---|---|
| Ethernet fisica | Realtek RTL8125 2.5GbE | disponibile, nessun cavo durante l'inventario |
| Wi-Fi interna | MediaTek MT7922 802.11ax | connessione reale verso il router |
| Wi-Fi USB | Realtek RTL8812AU | candidata per l'hotspot |
| `virbr0` | bridge libvirt | rete virtuale default |
| `docker0` | bridge Docker | rete bridge predefinita dei container |
| bridge Docker personalizzato | Docker/Compose | rete di un progetto container esistente |

I nomi e gli indirizzi hardware reali della rete domestica non vengono pubblicati.

Comandi di inventario usati:

```bash
ip -br link
nmcli device status
sudo lshw -class network -short
lsusb -t
sudo ethtool -i <USB_WIFI_IFACE>
iw dev <USB_WIFI_IFACE> info
```

---

# 8. Analisi della scheda Wi-Fi USB

La scheda USB è stata riconosciuta dal driver:

```text
rtw88_8812au
```

NetworkManager ha riportato:

```text
WIFI-PROPERTIES.AP: sì
```

`iw` ha mostrato le modalità:

```text
IBSS
managed
AP
AP/VLAN
monitor
```

La presenza di `AP` conferma che il driver dichiara la possibilità di creare un access point.

## 8.1 `wiphy 2` e `phy2`

`wiphy` rappresenta una radio Wi-Fi fisica nel kernel. `wiphy 2` corrisponde normalmente a `phy2`.

```text
radio fisica: phy2 / wiphy 2
        |
        `-- interfaccia logica Wi-Fi USB
```

Il numero 2 non rappresenta il canale, la banda 2,4 GHz o la versione hardware. È un identificatore assegnato dal kernel e può cambiare dopo riavvii o ricollegamenti.

## 8.2 `type managed`

L'interfaccia risultava in modalità `managed`, cioè modalità client. Questo descrive la modalità attuale, non l'unica modalità disponibile. Quando verrà creato l'hotspot, dovrà passare alla modalità AP.

## 8.3 Bus USB

`lsusb -t` ha mostrato la scheda collegata a un percorso USB SuperSpeed e gestita dal driver corretto. La velocità del bus USB non equivale alla velocità reale della rete Wi-Fi.

## 8.4 Tentativo hotspot interrotto

È stato provato il comando:

```bash
sudo nmcli -s device wifi hotspot \
  ifname <USB_WIFI_IFACE> \
  con-name gateway-hotspot \
  ssid <LAB_SSID>
```

L'operazione è stata interrotta con `Ctrl+C`. Il successivo elenco dei profili non ha mostrato `gateway-hotspot`, quindi non risultava una connessione persistente da eliminare.

---

# 9. Ambiente KVM/libvirt

Sono stati verificati:

```text
virsh disponibile
virt-manager disponibile
rete default attiva
rete default persistente
rete default in avvio automatico
```

## 9.1 Rete `default`

La rete `default` usa normalmente:

```text
bridge: virbr0
subnet: 192.168.122.0/24
gateway: 192.168.122.1
modalità: NAT
DHCP: attivo
```

Questa rete rappresenta il lato WAN della VM Kali.

## 9.2 Rete `lab-lan`

È stata creata una rete isolata:

```text
nome: lab-lan
subnet: 10.10.10.0/24
forwarding libvirt: isolato
DHCP: disabilitato
```

La rete isolata evita che il client raggiunga Internet senza attraversare Kali.

## 9.3 Due schede sulla VM gateway

Kali è stata configurata con:

```text
scheda 1 -> default -> WAN
scheda 2 -> lab-lan -> LAN
```

Parrot dovrà avere una sola scheda sulla rete `lab-lan`.

---

# 10. Lavoro realizzato nella VM Kali

## 10.1 Situazione dopo l'aggiunta della seconda scheda

`ip -br link` mostrava `eth0` ed `eth1` entrambe operative a livello di link, ma inizialmente nessuna possedeva un indirizzo IPv4. Questo dimostrava che le schede virtuali erano collegate, ma NetworkManager non aveva applicato correttamente i profili.

## 10.2 Diagnosi con NetworkManager

Il comando:

```bash
nmcli -p device status
```

ha mostrato `eth1` in attesa di configurazione IP con il profilo Ethernet automatico, mentre `eth0` risultava disconnessa.

Poiché `lab-lan` non fornisce DHCP, il profilo automatico non poteva ottenere un indirizzo su `eth1`.

## 10.3 Attivazione della WAN

È stato eseguito:

```bash
sudo nmcli device connect eth0
```

NetworkManager ha applicato il profilo disponibile a `eth0`, ottenendo:

```text
eth0  192.168.122.223/24
```

La rotta predefinita è diventata:

```text
default via 192.168.122.1 dev eth0
```

## 10.4 Test di connettività

Sono stati eseguiti:

```bash
ping -c 3 192.168.122.1
ping -c 3 1.1.1.1
```

Il primo test ha verificato il gateway libvirt. Il secondo ha verificato Internet a livello IP senza dipendere dal DNS. Entrambi hanno risposto.

## 10.5 Creazione del profilo LAN

È stato creato un profilo statico per `eth1`:

```bash
sudo nmcli connection add \
  type ethernet \
  ifname eth1 \
  con-name lab-lan-static \
  ipv4.method manual \
  ipv4.addresses 10.10.10.1/24 \
  ipv4.never-default yes \
  ipv6.method disabled
```

Il tentativo con `10.10.10.1/24` non si è attivato. La causa più plausibile è che il bridge libvirt dell'host possedesse già tale indirizzo.

Il profilo è stato quindi corretto:

```bash
sudo nmcli connection modify lab-lan-static \
  ipv4.method manual \
  ipv4.addresses 10.10.10.2/24 \
  ipv4.gateway "" \
  ipv4.dns "" \
  ipv4.never-default yes

sudo nmcli connection up lab-lan-static
```

L'attivazione è riuscita.

## 10.6 Separazione definitiva dei profili

Il profilo automatico originale è stato rinominato e vincolato alla WAN:

```bash
sudo nmcli connection modify "Wired connection 1" \
  connection.id wan-dhcp \
  connection.interface-name eth0 \
  ipv4.method auto \
  ipv4.never-default no
```

Lo stato finale è:

```text
wan-dhcp        -> eth0
lab-lan-static  -> eth1
```

Questa separazione evita che al riavvio il profilo DHCP venga tentato sulla LAN.

---

# 11. Problemi incontrati e diagnosi

## 11.1 Copia accidentale del simbolo `>`

Il simbolo mostrato dal prompt è stato copiato prima di un comando. In shell `>` è una redirezione e non un semplice carattere grafico. Il risultato è stato un tentativo di eseguire `-f` come comando.

Forma corretta:

```bash
nmcli -f NAME,TYPE,DEVICE connection show
```

## 11.2 Nessun output da `grep`

Il comando che cercava `valid interface combinations` non ha prodotto righe. Questo non indicava un guasto: il driver non esponeva quella sezione o il testo non corrispondeva. La modalità AP era già stata confermata in altri due modi.

## 11.3 DHCP applicato all'interfaccia sbagliata

Dopo l'aggiunta di `eth1`, il profilo automatico tentava di acquisire un IP sulla rete isolata. La soluzione è stata attivare la WAN su `eth0` e creare un profilo statico separato per `eth1`.

## 11.4 Conflitto su `10.10.10.1`

NetworkManager ha rifiutato l'indirizzo iniziale. L'ipotesi più plausibile è un indirizzo duplicato sul bridge dell'host. È stato scelto `10.10.10.2` per Kali.

## 11.5 `virsh` non presente dentro Kali

`virsh` amministra libvirt sull'host. Non è necessario che sia installato nella VM. I comandi relativi alle reti libvirt devono essere eseguiti sull'Ubuntu host.

---

# 12. Stato attuale verificato

Profili NetworkManager:

```text
wan-dhcp        ethernet  eth0
lab-lan-static  ethernet  eth1
lo              loopback  lo
```

Dispositivi:

```text
eth0  collegato  wan-dhcp
eth1  collegato  lab-lan-static
lo    connesso
```

Indirizzi:

```text
lo    127.0.0.1/8
eth0  192.168.122.223/24
eth1  10.10.10.2/24
```

Rotte:

```text
default via 192.168.122.1 dev eth0 proto dhcp src 192.168.122.223 metric 100
10.10.10.0/24 dev eth1 proto kernel scope link src 10.10.10.2 metric 101
192.168.122.0/24 dev eth0 proto kernel scope link src 192.168.122.223 metric 100
```

La VM Kali ha accesso a Internet. Non è stato ancora verificato il traffico di Parrot attraverso Kali, perché mancano il client, il forwarding e il NAT.

---

# 13. Prossimi passi operativi

> I comandi di questa sezione rappresentano il piano successivo. Devono essere eseguiti dopo uno snapshot e dopo aver verificato i nomi reali delle interfacce.

## 13.1 Configurare Parrot

Parrot deve avere una sola scheda collegata a `lab-lan`.

Esempio:

```bash
sudo nmcli connection add \
  type ethernet \
  ifname eth0 \
  con-name lab-client \
  ipv4.method manual \
  ipv4.addresses 10.10.10.3/24 \
  ipv4.gateway 10.10.10.2 \
  ipv4.dns "1.1.1.1 9.9.9.9" \
  ipv4.never-default no \
  ipv6.method disabled

sudo nmcli connection up lab-client
```

Prima verificare il nome dell'interfaccia con:

```bash
ip -br link
nmcli device status
```

## 13.2 Test locale

Da Parrot:

```bash
ping -c 3 10.10.10.2
```

Il ping verso Kali deve funzionare. Internet potrebbe non funzionare ancora, ed è previsto.

## 13.3 Abilitare il forwarding IPv4

Su Kali:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sysctl net.ipv4.ip_forward
```

Il valore `1` autorizza il kernel a inoltrare pacchetti IPv4 tra interfacce.

La persistenza potrà essere aggiunta soltanto dopo il test:

```bash
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-gateway-lab.conf
sudo sysctl --system
```

## 13.4 Applicare il firewall e il NAT

Il file di esempio del repository contiene un ruleset commentato. Il principio è:

```text
forward policy drop
consenti established,related
consenti LAN -> WAN
masquerade sulla WAN
```

## 13.5 Test end-to-end

Da Parrot:

```bash
ping -c 3 10.10.10.2
ping -c 3 1.1.1.1
ping -c 3 debian.org
traceroute -n 1.1.1.1
```

Ordine diagnostico:

1. gateway locale;
2. IP pubblico;
3. nome DNS;
4. percorso.

---

# 14. Teoria di `nftables` e connection tracking

`nftables` organizza le regole in:

```text
tables
  chains
    rules
```

## 14.1 Hook principali

- `input`: pacchetti destinati alla macchina stessa;
- `output`: pacchetti generati dalla macchina;
- `forward`: pacchetti che attraversano la macchina;
- `prerouting`: prima della decisione di routing;
- `postrouting`: dopo la decisione di routing, prima dell'uscita.

Il traffico Parrot → Internet attraversa la catena `forward`, non la catena `input`.

## 14.2 Politica `drop`

Una chain con `policy drop` scarta tutto ciò che non viene accettato esplicitamente. È una base sicura, ma deve essere introdotta con attenzione perché una regola mancante blocca il traffico.

## 14.3 Connection tracking

Il kernel mantiene informazioni sullo stato delle connessioni. Stati importanti:

- `new`: inizio di una connessione;
- `established`: connessione già riconosciuta;
- `related`: traffico correlato;
- `invalid`: pacchetto non associabile correttamente.

La regola:

```text
ct state established,related accept
```

permette il traffico di risposta senza aprire indiscriminatamente WAN verso LAN.

## 14.4 Masquerade

`masquerade` è una forma di source NAT utile quando l'indirizzo dell'interfaccia esterna può cambiare. Il kernel usa dinamicamente l'IP corrente della WAN.

## 14.5 Contatori

La parola `counter` registra pacchetti e byte che corrispondono a una regola. I contatori forniscono dati utili senza memorizzare il contenuto dei pacchetti.

---

# 15. Monitoraggio e raccolta dati

## 15.1 `tcpdump`

Comandi iniziali:

```bash
sudo tcpdump -ni eth1
sudo tcpdump -ni eth1 'port 53'
sudo tcpdump -ni eth1 'tcp port 443'
sudo tcpdump -ni eth0
```

Opzioni:

- `-n`: non risolve indirizzi e porte in nomi;
- `-i`: sceglie l'interfaccia;
- filtro BPF: limita il traffico mostrato.

## 15.2 Statistiche delle interfacce

```bash
ip -s link show dev eth0
ip -s link show dev eth1
```

I dati comprendono byte, pacchetti, errori e pacchetti scartati.

## 15.3 Vicini locali

```bash
ip neigh show dev eth1
```

Mostra gli host conosciuti sulla LAN.

## 15.4 HTTPS

Il gateway vede normalmente:

- IP sorgente e destinazione;
- porte;
- protocollo;
- durata;
- byte e pacchetti;
- informazioni DNS quando non cifrate separatamente.

Non vede automaticamente password o contenuti HTTPS, che restano cifrati.

---

# 16. Ruolo futuro di Docker e Python

Dopo il funzionamento del gateway, Docker potrà ospitare:

- un servizio Python che legge contatori e log;
- un database SQLite o PostgreSQL;
- una dashboard web;
- un proxy esplicito;
- esportatori di metriche;
- servizi di visualizzazione.

Architettura prevista:

```text
Kali VM
|-- routing e nftables nel sistema
|-- log e metriche
`-- Docker
    |-- collector Python
    |-- database
    `-- dashboard
```

## 16.1 Primo analizzatore Python

Il primo programma potrà:

1. eseguire comandi non distruttivi tramite `subprocess`;
2. leggere output JSON di `ip -j` e `nft -j`;
3. normalizzare i dati;
4. salvare timestamp, interfacce, byte e pacchetti;
5. produrre un report Markdown o JSON;
6. segnalare nuove destinazioni o variazioni anomale.

## 16.2 Principio del minimo privilegio

I container non dovranno ricevere `privileged: true` senza necessità. È preferibile:

- montare log in sola lettura;
- esporre porte solo sulla LAN;
- non montare `/var/run/docker.sock`;
- evitare `network_mode: host` quando non necessario;
- separare collector, database e dashboard.

---

# 17. Passaggio futuro al gateway fisico

L'host possiede una radio interna e una radio USB separata. La configurazione fisica prevista è:

```text
interfaccia WAN: scheda collegata al router domestico
interfaccia LAN: scheda USB in modalità AP
```

La Realtek USB ha dichiarato supporto AP. Prima del passaggio fisico sarà necessario verificare:

- stabilità del driver in modalità AP;
- banda e canale;
- dominio normativo;
- DHCP per i client;
- DNS;
- persistenza del ruleset;
- comportamento dopo riavvio;
- rollback locale in caso di perdita di rete.

Il routing e il firewall dovranno rimanere sull'host o su una macchina dedicata. Docker ospiterà i servizi accessori.

---

# 18. Sicurezza operativa e pubblicazione

## 18.1 Prima delle modifiche

- creare snapshot;
- tenere aperta la console della VM;
- salvare lo stato corrente;
- verificare il prompt e l'hostname;
- applicare una modifica alla volta;
- testare immediatamente.

## 18.2 Dati da non pubblicare

- password Wi-Fi;
- SSID domestici reali;
- token API;
- chiavi SSH private;
- file `.env`;
- certificati privati;
- cookie;
- log non revisionati;
- indirizzi MAC reali, quando non necessari;
- percorsi contenenti dati personali.

## 18.3 Cronologia Git

Rimuovere un segreto dall'ultima versione non lo elimina automaticamente dai commit precedenti. Una credenziale pubblicata deve essere revocata e sostituita. Il repository pubblico viene quindi costruito direttamente con dati anonimizzati.

---

# 19. Troubleshooting professionale

Il metodo diagnostico procede dal livello più basso al più alto.

## 19.1 Livello interfaccia

```bash
ip -br link
```

Verificare presenza, `UP` e `LOWER_UP`.

## 19.2 Livello indirizzo

```bash
ip -4 -br address
```

Verificare subnet e assenza di duplicati.

## 19.3 Livello routing

```bash
ip route
```

Verificare:

- default corretta;
- rete LAN su `eth1`;
- rete WAN su `eth0`;
- assenza di un secondo default sulla LAN.

## 19.4 Test locale

```bash
ping -c 3 <gateway-locale>
```

## 19.5 Test Internet senza DNS

```bash
ping -c 3 1.1.1.1
```

## 19.6 Test DNS

```bash
ping -c 3 debian.org
```

## 19.7 Forwarding

```bash
sysctl net.ipv4.ip_forward
```

Deve restituire `1` quando il gateway è attivo.

## 19.8 Firewall

```bash
sudo nft list ruleset
```

Controllare regole, interfacce, contatori e policy.

## 19.9 Osservazione sui due lati

```bash
sudo tcpdump -ni eth1
sudo tcpdump -ni eth0
```

Se il pacchetto entra su `eth1` ma non esce su `eth0`, il problema è nel forwarding o nel firewall. Se esce ma non torna, controllare NAT e gateway esterno.

---

# 20. Roadmap e criteri di completamento

## Fase 1 — Inventario

- [x] hardware identificato;
- [x] driver Wi-Fi identificato;
- [x] supporto AP verificato;
- [x] Docker e libvirt riconosciuti.

## Fase 2 — Laboratorio virtuale

- [x] rete `default` verificata;
- [x] rete `lab-lan` creata;
- [x] Kali con due interfacce;
- [x] WAN configurata;
- [x] LAN configurata;
- [ ] Parrot isolata e configurata.

## Fase 3 — Gateway

- [ ] forwarding IPv4;
- [ ] firewall `forward`;
- [ ] NAT masquerade;
- [ ] test end-to-end;
- [ ] persistenza controllata.

## Fase 4 — Monitoraggio

- [ ] contatori `nftables`;
- [ ] catture diagnostiche;
- [ ] inventario dei client;
- [ ] report periodici;
- [ ] allarmi su errori e nuove destinazioni.

## Fase 5 — Docker e Python

- [ ] collector Python;
- [ ] formato JSON stabile;
- [ ] database;
- [ ] dashboard;
- [ ] Docker Compose con privilegi minimi.

## Fase 6 — Gateway fisico

- [ ] hotspot Wi-Fi di laboratorio;
- [ ] DHCP/DNS della LAN;
- [ ] test con telefono o secondo PC;
- [ ] persistenza e recupero dopo riavvio;
- [ ] documentazione finale riproducibile.

Il progetto potrà essere considerato completo quando un client collegato esclusivamente alla LAN raggiunge Internet passando obbligatoriamente attraverso il gateway, le regole sono persistenti e documentate, e i dati essenziali del traffico sono raccolti senza esporre informazioni sensibili.