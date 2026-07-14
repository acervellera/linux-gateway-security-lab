# Lavoro svolto, teoria dei comandi e prossimi passi

## 1. Scopo di questo documento

Questo documento registra soltanto:

- attività realmente eseguite;
- risultati realmente osservati;
- problemi incontrati;
- spiegazione teorica dei comandi usati;
- stato attuale verificato;
- attività future chiaramente indicate come **non ancora eseguite**.

Il documento non presenta forwarding, `nftables`, NAT, monitoraggio Python o dashboard Docker come funzioni già completate.

Per la descrizione del risultato finale desiderato consultare [`OBIETTIVI_E_PROGETTO.md`](OBIETTIVI_E_PROGETTO.md).

---

# 2. Stato sintetico

## 2.1 Completato e verificato

- inventario delle interfacce dell'host Ubuntu;
- identificazione delle schede di rete principali;
- verifica della scheda Wi-Fi USB Realtek RTL8812AU;
- verifica del driver `rtw88_8812au`;
- verifica del supporto della modalità Access Point;
- verifica della presenza di KVM/libvirt e virt-manager;
- verifica della rete libvirt `default`;
- creazione della rete isolata `lab-lan`;
- aggiunta di una seconda interfaccia virtuale alla VM Kali;
- configurazione di `eth0` come WAN tramite DHCP;
- configurazione di `eth1` come LAN statica `10.10.10.2/24`;
- separazione dei profili NetworkManager;
- verifica del gateway libvirt;
- verifica della connettività Internet dalla VM Kali.

## 2.2 Non ancora eseguito

- configurazione di Parrot sulla rete `lab-lan`;
- test di comunicazione Parrot → Kali;
- attivazione di `net.ipv4.ip_forward`;
- creazione del firewall `nftables`;
- creazione del NAT/masquerading;
- test end-to-end da Parrot a Internet;
- cattura del traffico con `tcpdump` nel laboratorio;
- creazione di script Python;
- integrazione Docker per dashboard o analisi;
- creazione stabile dell'hotspot Wi-Fi fisico.

---

# 3. Ambiente di partenza

Il sistema principale è un host Ubuntu che esegue:

- Docker;
- KVM/QEMU;
- libvirt;
- virt-manager;
- una VM Kali;
- una VM Parrot.

Sull'host sono state osservate tre interfacce fisiche principali:

| Tipo | Hardware | Stato osservato | Ruolo possibile |
|---|---|---|---|
| Wi-Fi interna | MediaTek MT7922 | collegata alla rete domestica | uscita Internet reale |
| Wi-Fi USB | Realtek RTL8812AU | disponibile, non collegata | hotspot futuro |
| Ethernet | Realtek RTL8125 2.5GbE | senza portante | LAN cablata futura |

Nel repository pubblico i nomi che incorporano indirizzi MAC e l'SSID reale sono omessi.

Sono stati osservati anche bridge virtuali creati da Docker e libvirt, tra cui:

- `docker0`;
- un bridge Docker personalizzato;
- `virbr0` per la rete libvirt `default`.

---

# 4. Inventario delle interfacce dell'host

## 4.1 Comando usato

```bash
ip -br link
```

## 4.2 Spiegazione

`ip` appartiene al pacchetto `iproute2`. È lo strumento moderno per gestire e interrogare:

- interfacce;
- indirizzi;
- rotte;
- vicini ARP/NDP;
- tunnel;
- namespace e altri oggetti di rete.

La struttura generale è:

```text
ip [opzioni] oggetto comando
```

Nel comando usato:

- `-br` significa `--brief` e produce un formato compatto;
- `link` seleziona gli oggetti di livello collegamento.

L'output mostra tipicamente:

- nome dell'interfaccia;
- stato;
- indirizzo MAC;
- flag del link.

## 4.3 Teoria dei flag osservati

### `UP`

L'interfaccia è amministrativamente abilitata. Non significa necessariamente che possieda un indirizzo IP.

### `LOWER_UP`

Il livello inferiore è operativo. Su una scheda fisica indica normalmente che esiste portante; su una scheda virtuale indica che il collegamento virtuale è presente.

### `NO-CARRIER`

L'interfaccia è abilitata, ma non rileva un collegamento. È normale, per esempio, su una Ethernet senza cavo.

### `DOWN`

L'interfaccia non è operativa.

### `UNKNOWN` su `lo`

È normale per il loopback, perché non esiste un mezzo fisico da misurare.

## 4.4 Concetto importante

Una scheda può essere:

```text
UP + LOWER_UP
```

ma non avere alcun indirizzo IPv4. Lo stato del link e la configurazione IP appartengono a livelli diversi.

---

# 5. Stato delle connessioni NetworkManager sull'host

## 5.1 Comandi usati

```bash
nmcli -p device status
nmcli -p connection show
```

## 5.2 Differenza tra `device` e `connection`

In NetworkManager:

```text
device     = interfaccia reale o virtuale
connection = profilo di configurazione salvato
```

Una scheda può esistere senza un profilo attivo. Un profilo può esistere senza essere attualmente attivo su una scheda.

## 5.3 Flag e oggetti

- `nmcli` è il client a riga di comando di NetworkManager;
- `-p` significa `--pretty` e produce una tabella leggibile;
- `device status` mostra lo stato dei dispositivi;
- `connection show` mostra i profili salvati e l'eventuale interfaccia associata.

L'uso di questi comandi ha permesso di distinguere la connessione Wi-Fi reale, le interfacce disconnesse e i bridge virtuali.

---

# 6. Inventario hardware

## 6.1 Comando usato

```bash
sudo lshw -class network -short
```

## 6.2 Spiegazione

- `sudo` esegue il comando con privilegi amministrativi;
- `lshw` significa hardware lister;
- `-class network` limita l'output alla classe rete;
- `-short` produce una tabella compatta.

La versione lunga, non necessaria per il primo controllo, sarebbe:

```bash
sudo lshw -class network
```

L'inventario ha permesso di identificare:

- MediaTek MT7922;
- Realtek RTL8812AU USB;
- Realtek RTL8125 2.5GbE.

---

# 7. Verifica della scheda Wi-Fi USB

## 7.1 Albero USB

Comando usato:

```bash
lsusb -t
```

Spiegazione:

- `lsusb` elenca i dispositivi USB;
- `-t` mostra una struttura ad albero con bus, hub, porte, driver e velocità del collegamento.

La scheda Realtek è risultata collegata tramite un percorso USB SuperSpeed e gestita dal driver `rtw88_8812au`.

Una voce come:

```text
5000M
```

indica la velocità nominale del collegamento USB. Non indica la velocità reale della rete Wi-Fi.

## 7.2 Driver

Comando usato:

```bash
sudo ethtool -i <USB_WIFI_IFACE>
```

Spiegazione:

- `ethtool` interroga e configura molte proprietà delle interfacce;
- `-i` mostra informazioni sul driver;
- `<USB_WIFI_IFACE>` rappresenta il nome reale dell'interfaccia, anonimizzato nel repository pubblico.

Il risultato ha mostrato:

```text
driver: rtw88_8812au
```

Sono state mostrate anche informazioni sul bus. Il campo firmware poteva risultare non disponibile; ciò non dimostra automaticamente l'assenza di firmware, ma soltanto che quella versione del driver non espone il dato tramite `ethtool`.

---

# 8. Verifica delle capacità Wi-Fi

## 8.1 Informazioni sull'interfaccia

Comando usato:

```bash
iw dev <USB_WIFI_IFACE> info
```

`iw` comunica con il sottosistema wireless Linux tramite `nl80211`.

L'output ha mostrato campi come:

- `ifindex`: indice dell'interfaccia nel namespace;
- `wdev`: identificatore wireless interno;
- `addr`: indirizzo MAC;
- `type managed`: modalità client attuale;
- `wiphy 2`: radio fisica associata;
- `txpower`: potenza riportata.

## 8.2 Significato di `wiphy 2`

`wiphy` identifica una radio Wi-Fi fisica nel kernel.

```text
wiphy 2 = phy2
```

Il numero `2` non significa:

- banda 2,4 GHz;
- canale 2;
- seconda antenna.

È soltanto un identificatore assegnato dal kernel alla radio fisica.

## 8.3 Modalità supportate

Comando usato:

```bash
iw phy phy2 info | grep -A 15 "Supported interface modes"
```

Spiegazione:

- `iw phy phy2 info` mostra le capacità della radio;
- `|` è una pipe: passa l'output al comando successivo;
- `grep` cerca una stringa;
- `-A 15` significa mostrare anche 15 righe dopo la corrispondenza.

Tra le modalità osservate erano presenti:

- `managed`;
- `AP`;
- `AP/VLAN`;
- `monitor`;
- `IBSS`.

Questo ha verificato che il driver dichiara supporto alla modalità Access Point.

## 8.4 Cosa non è stato ancora verificato

Il supporto dichiarato non prova ancora:

- stabilità dell'hotspot per molte ore;
- qualità del segnale;
- compatibilità con tutti i canali;
- prestazioni reali;
- corretto funzionamento contemporaneo di DHCP, NAT e firewall sull'hardware reale.

---

# 9. Tentativo di hotspot interrotto

È stato avviato un comando simile a:

```bash
sudo nmcli -s device wifi hotspot \
  ifname <USB_WIFI_IFACE> \
  con-name gateway-hotspot \
  ssid <SSID_DI_LABORATORIO>
```

Il comando è stato interrotto con `Ctrl+C`.

## 9.1 Spiegazione delle parti

- `sudo`: privilegi amministrativi;
- `nmcli`: client NetworkManager;
- `-s`: in questo contesto consente l'uso di segreti; l'output va trattato con cautela;
- `device wifi hotspot`: chiede a NetworkManager di creare un hotspot;
- `ifname`: seleziona l'interfaccia;
- `con-name`: assegna un nome al profilo;
- `ssid`: assegna il nome trasmesso dalla rete Wi-Fi;
- `\`: continuazione di riga della shell.

## 9.2 Risultato effettivo

Dopo l'interruzione è stato controllato l'elenco dei profili e non risultava un profilo persistente chiamato `gateway-hotspot`.

Di conseguenza:

- l'hotspot fisico non è stato completato;
- non viene presentato come funzione realizzata;
- non è stato necessario rimuovere un profilo rimasto attivo.

---

# 10. Verifica dell'ambiente KVM/libvirt

Sono stati verificati:

```bash
virsh --version
virt-manager --version
virsh net-list --all
```

## 10.1 Teoria

- KVM fornisce virtualizzazione assistita dal kernel;
- QEMU emula e presenta l'hardware virtuale;
- libvirt gestisce VM, storage e reti;
- `virsh` è il client a riga di comando di libvirt;
- virt-manager è l'interfaccia grafica.

## 10.2 Flag

- `--version` mostra la versione installata;
- `net-list` elenca le reti libvirt;
- `--all` include reti attive e inattive.

La rete `default` risultava attiva e configurata per l'avvio automatico.

## 10.3 Dove eseguire `virsh`

`virsh` deve essere eseguito sull'host che gestisce libvirt. Quando è stato provato dentro Kali, il comando non era installato:

```text
sudo: virsh: comando non trovato
```

Questo non indicava un guasto della rete. Indicava soltanto che libvirt è amministrato dall'Ubuntu host, non dalla VM Kali.

---

# 11. Rete libvirt `default`

La rete `default` è stata usata come WAN virtuale di Kali.

Caratteristiche osservate:

```text
subnet: 192.168.122.0/24
gateway: 192.168.122.1
DHCP: attivo
modalità: NAT
bridge: virbr0
```

La funzione di questa rete è fornire alla VM:

- un indirizzo automatico;
- una rotta predefinita;
- accesso verso l'esterno tramite NAT dell'host.

---

# 12. Creazione della rete isolata `lab-lan`

È stata creata tramite virt-manager una seconda rete libvirt con queste proprietà:

```text
nome: lab-lan
rete IPv4: 10.10.10.0/24
modalità: isolata
DHCP IPv4: disabilitato
IPv6: disabilitato nella configurazione iniziale
```

## 12.1 Perché isolata

Una rete isolata consente alle VM collegate di comunicare localmente, ma non fornisce automaticamente un percorso verso Internet.

Questo è necessario perché il futuro client Parrot dovrà dipendere da Kali.

## 12.2 Perché DHCP è stato disabilitato

Il DHCP è stato disabilitato per assegnare manualmente indirizzi semplici e prevedibili:

```text
Kali LAN:   10.10.10.2/24
Parrot:     10.10.10.3/24, previsto
```

## 12.3 Nota sul prefisso

La rete deve essere scritta:

```text
10.10.10.0/24
```

La barra `/` fa parte della notazione CIDR. `/24` equivale alla maschera:

```text
255.255.255.0
```

---

# 13. Stato iniziale di Kali con una sola interfaccia

Prima di aggiungere la LAN, Kali mostrava:

```text
eth0  192.168.122.223/24
```

La tabella di routing includeva:

```text
default via 192.168.122.1 dev eth0 proto dhcp src 192.168.122.223 metric 100
192.168.122.0/24 dev eth0 proto kernel scope link src 192.168.122.223 metric 100
```

Questo dimostrava che:

- `eth0` era collegata alla rete libvirt `default`;
- DHCP aveva assegnato l'indirizzo;
- `192.168.122.1` era il gateway;
- Kali possedeva una rotta verso Internet.

---

# 14. Aggiunta della seconda interfaccia a Kali

La VM Kali è stata spenta e in virt-manager è stata aggiunta una seconda scheda virtuale collegata a `lab-lan`.

Dopo il riavvio:

```bash
ip -br link
```

mostrava:

```text
eth0  UP ... LOWER_UP
eth1  UP ... LOWER_UP
```

Questo confermava che entrambe le schede virtuali esistevano e avevano collegamento.

Tuttavia:

```bash
ip -4 -br address
```

mostrava inizialmente soltanto:

```text
lo  127.0.0.1/8
```

## 14.1 Interpretazione

Le schede erano presenti a livello link, ma nessuna delle due aveva ancora un IPv4 attivo.

Questo è un esempio importante della differenza tra:

```text
link disponibile
```

e:

```text
configurazione IP disponibile
```

---

# 15. Diagnosi con NetworkManager dentro Kali

Comandi eseguiti:

```bash
nmcli -p device status
nmcli -p connection show
```

Il risultato mostrava:

```text
eth1  connessione in corso, acquisizione configurazione IP  Wired connection 1
eth0  disconnesso
```

Esisteva un solo profilo Ethernet:

```text
Wired connection 1
```

## 15.1 Diagnosi

Il profilo DHCP che prima serviva `eth0` stava tentando di attivarsi su `eth1`.

Poiché `lab-lan` non disponeva di DHCP, NetworkManager attendeva un indirizzo che non sarebbe arrivato.

---

# 16. Ripristino della WAN di Kali

Comando eseguito:

```bash
sudo nmcli device connect eth0
```

## 16.1 Spiegazione

- `sudo`: esecuzione amministrativa;
- `nmcli`: client NetworkManager;
- `device`: opera sul dispositivo;
- `connect`: cerca e attiva un profilo compatibile;
- `eth0`: interfaccia selezionata.

NetworkManager ha attivato con successo il profilo esistente su `eth0`.

## 16.2 Risultato

```bash
ip -4 -br address show dev eth0
ip route
```

ha mostrato:

```text
eth0  UP  192.168.122.223/24

default via 192.168.122.1 dev eth0 proto dhcp src 192.168.122.223 metric 100
192.168.122.0/24 dev eth0 proto kernel scope link src 192.168.122.223 metric 100
```

---

# 17. Verifica della connettività di Kali

Sono stati eseguiti:

```bash
ping -c 3 192.168.122.1
ping -c 3 1.1.1.1
```

Entrambi i test hanno ricevuto risposta.

## 17.1 Spiegazione

- `ping` invia ICMP Echo Request;
- `-c 3` limita il test a tre pacchetti;
- `192.168.122.1` verifica il collegamento con il gateway libvirt;
- `1.1.1.1` verifica il percorso verso un IP pubblico senza dipendere dal DNS.

## 17.2 Metodo diagnostico

L'ordine corretto è:

```text
1. gateway locale
2. IP pubblico
3. nome DNS
```

Se il gateway risponde ma l'IP pubblico no, il problema è oltre il collegamento locale.

Se l'IP pubblico risponde ma un nome no, il problema può essere DNS.

Nel lavoro documentato è stata verificata con successo la raggiungibilità IP pubblica.

---

# 18. Creazione del profilo LAN statico

È stato creato inizialmente questo profilo:

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

## 18.1 Significato delle proprietà

- `connection add`: crea un profilo;
- `type ethernet`: profilo Ethernet;
- `ifname eth1`: associa il profilo a `eth1`;
- `con-name lab-lan-static`: nome leggibile del profilo;
- `ipv4.method manual`: configurazione IPv4 statica;
- `ipv4.addresses`: indirizzo e prefisso;
- `ipv4.never-default yes`: la LAN non deve creare una rotta predefinita;
- `ipv6.method disabled`: IPv6 disabilitato su quel profilo;
- `\`: continua il comando sulla riga successiva.

## 18.2 Primo errore

Il tentativo di attivazione:

```bash
sudo nmcli connection up lab-lan-static
```

ha restituito un errore relativo all'impossibilità di riservare la configurazione IP.

L'indirizzo iniziale era:

```text
10.10.10.1/24
```

È plausibile che `10.10.10.1` fosse già usato dal bridge libvirt dell'host, ma questa ipotesi non è stata confermata dentro Kali. Il comando `virsh` non era disponibile nella VM e il controllo dell'indirizzo del bridge deve essere eseguito sull'host.

Perciò il documento considera il conflitto **probabile**, non dimostrato definitivamente.

---

# 19. Correzione dell'indirizzo LAN

Il profilo è stato modificato:

```bash
sudo nmcli connection modify lab-lan-static \
  ipv4.method manual \
  ipv4.addresses 10.10.10.2/24 \
  ipv4.gateway "" \
  ipv4.dns "" \
  ipv4.never-default yes
```

## 19.1 Significato

### `connection modify`

Modifica un profilo già esistente senza crearne uno nuovo.

### `ipv4.addresses 10.10.10.2/24`

Assegna a Kali l'indirizzo LAN `10.10.10.2` con prefisso `/24`.

### `ipv4.gateway ""`

La stringa vuota rimuove il gateway dal profilo LAN.

La LAN non deve fornire la rotta predefinita. L'uscita Internet resta su `eth0`.

### `ipv4.dns ""`

Rimuove server DNS dal profilo LAN, evitando che questa connessione sostituisca la configurazione DNS della WAN.

### `ipv4.never-default yes`

Impedisce al profilo di diventare la connessione predefinita.

## 19.2 Attivazione

```bash
sudo nmcli connection up lab-lan-static
```

Questa volta la connessione è stata attivata con successo.

---

# 20. Stato di rete ottenuto

I comandi:

```bash
ip -4 -br address
ip route
```

hanno mostrato:

```text
lo    UNKNOWN  127.0.0.1/8
eth0  UP       192.168.122.223/24
eth1  UP       10.10.10.2/24
```

Rotte:

```text
default via 192.168.122.1 dev eth0 proto dhcp src 192.168.122.223 metric 100
10.10.10.0/24 dev eth1 proto kernel scope link src 10.10.10.2 metric 101
192.168.122.0/24 dev eth0 proto kernel scope link src 192.168.122.223 metric 100
```

---

# 21. Teoria della tabella di routing osservata

## 21.1 Rotta predefinita

```text
default via 192.168.122.1 dev eth0
```

Significa che le destinazioni non coperte da una rotta più specifica vengono inviate al gateway `192.168.122.1` tramite `eth0`.

## 21.2 Rete LAN direttamente connessa

```text
10.10.10.0/24 dev eth1
```

Significa che gli host della rete `10.10.10.0/24` sono raggiungibili direttamente tramite `eth1`.

## 21.3 Rete WAN direttamente connessa

```text
192.168.122.0/24 dev eth0
```

Significa che la rete WAN virtuale è collegata direttamente a `eth0`.

## 21.4 `proto dhcp`

La rotta è stata ricevuta tramite DHCP.

## 21.5 `proto kernel`

La rotta è stata creata automaticamente dal kernel quando è stato assegnato l'indirizzo all'interfaccia.

## 21.6 `scope link`

La destinazione è raggiungibile direttamente sul collegamento locale.

## 21.7 `src`

Indica l'indirizzo sorgente preferito per quella rotta.

## 21.8 `metric`

È il costo della rotta. Tra rotte con lo stesso prefisso viene normalmente preferito il valore più basso.

La differenza tra metriche `100` e `101` non trasforma la LAN in uscita Internet. La scelta principale dipende dalla specificità della rotta e dalla presenza della rotta `default` su `eth0`.

---

# 22. Rinominare e vincolare il profilo WAN

Il profilo generico è stato modificato:

```bash
sudo nmcli connection modify "Wired connection 1" \
  connection.id wan-dhcp \
  connection.interface-name eth0 \
  ipv4.method auto \
  ipv4.never-default no
```

## 22.1 Spiegazione

### `connection.id wan-dhcp`

Rinomina il profilo con un nome che descrive il ruolo.

### `connection.interface-name eth0`

Vincola il profilo a `eth0`, evitando che tenti di attivarsi su `eth1`.

### `ipv4.method auto`

Usa DHCP.

### `ipv4.never-default no`

Consente alla WAN di fornire la rotta predefinita.

---

# 23. Verifica finale dei profili NetworkManager

Sono stati eseguiti:

```bash
nmcli -p connection show
nmcli -p device status
```

Risultato osservato:

```text
NAME            TYPE      DEVICE
wan-dhcp        ethernet  eth0
lab-lan-static  ethernet  eth1
lo              loopback  lo
```

Stato dispositivi:

```text
eth0  ethernet  collegato  wan-dhcp
eth1  ethernet  collegato  lab-lan-static
lo    loopback  connesso   lo
wlan0 wifi      disconnesso
```

Questo è lo stato attuale verificato della VM gateway.

---

# 24. Significato dello stato attuale

Kali possiede adesso due ruoli distinti:

```text
eth0 = WAN
eth1 = LAN
```

La WAN:

- riceve configurazione tramite DHCP;
- possiede la rotta predefinita;
- raggiunge Internet.

La LAN:

- possiede un indirizzo statico;
- non possiede gateway;
- non sostituisce la rotta predefinita;
- è pronta per comunicare con un futuro client.

Kali non è ancora un router completo, perché non è stato verificato né attivato l'inoltro dei pacchetti tra le interfacce.

---

# 25. Errori incontrati e lezione appresa

## 25.1 Schede presenti ma senza IPv4

### Sintomo

`ip -br link` mostrava `eth0` ed `eth1`, ma `ip -4 -br address` mostrava soltanto `lo`.

### Causa

Il profilo DHCP non era attivo sulla WAN e stava tentando di ottenere un indirizzo sulla LAN isolata.

### Soluzione

```bash
sudo nmcli device connect eth0
```

### Lezione

Il livello link può funzionare anche senza configurazione IP.

## 25.2 DHCP sulla rete sbagliata

### Sintomo

`eth1` restava in acquisizione configurazione IP.

### Causa

`lab-lan` non ha un server DHCP.

### Soluzione

Creare un profilo statico per `eth1` e vincolare il profilo DHCP a `eth0`.

## 25.3 Errore con `10.10.10.1`

### Sintomo

NetworkManager non riusciva a riservare la configurazione IP.

### Causa probabile

Possibile indirizzo già usato dal bridge libvirt dell'host.

### Soluzione applicata

Usare `10.10.10.2/24` per Kali.

### Nota di accuratezza

Il duplicato non è stato confermato con `virsh net-dumpxml` sull'host durante la sessione documentata.

## 25.4 `virsh` non trovato dentro Kali

### Causa

Il comando appartiene agli strumenti di amministrazione libvirt dell'host.

### Lezione

Prima di eseguire un comando bisogna identificare l'ambiente corretto:

```text
Ubuntu host
Kali gateway
Parrot client
```

## 25.5 Copia del simbolo `>`

In una shell il simbolo `>` non è parte del prompt da copiare: è un operatore di redirezione.

Un comando mostrato come:

```text
> nmcli ...
```

va digitato senza `>`.

Copiare il simbolo può creare o svuotare un file e far interpretare la parte successiva come un comando separato.

---

# 26. Stato attuale verificato e riproducibile

```text
Kali eth0
  ruolo: WAN
  profilo: wan-dhcp
  IPv4 osservato: 192.168.122.223/24
  gateway: 192.168.122.1
  Internet: verificato tramite ping a 1.1.1.1

Kali eth1
  ruolo: LAN
  profilo: lab-lan-static
  IPv4: 10.10.10.2/24
  gateway: nessuno
  default route: vietata dal profilo

Rete libvirt default
  subnet: 192.168.122.0/24
  DHCP: attivo
  NAT: attivo

Rete libvirt lab-lan
  subnet: 10.10.10.0/24
  isolamento: attivo
  DHCP: disabilitato
```

---

# 27. Comandi eseguiti principali

```bash
# Lettura delle interfacce
ip -br link
ip -4 -br address
ip route

# NetworkManager
nmcli -p device status
nmcli -p connection show
sudo nmcli device connect eth0

# Test WAN
ping -c 3 192.168.122.1
ping -c 3 1.1.1.1

# Creazione del profilo LAN, primo tentativo
sudo nmcli connection add \
  type ethernet \
  ifname eth1 \
  con-name lab-lan-static \
  ipv4.method manual \
  ipv4.addresses 10.10.10.1/24 \
  ipv4.never-default yes \
  ipv6.method disabled

# Correzione dell'indirizzo LAN
sudo nmcli connection modify lab-lan-static \
  ipv4.method manual \
  ipv4.addresses 10.10.10.2/24 \
  ipv4.gateway "" \
  ipv4.dns "" \
  ipv4.never-default yes

sudo nmcli connection up lab-lan-static

# Rinomina e associazione del profilo WAN
sudo nmcli connection modify "Wired connection 1" \
  connection.id wan-dhcp \
  connection.interface-name eth0 \
  ipv4.method auto \
  ipv4.never-default no

# Verifica finale
nmcli -p connection show
nmcli -p device status
ip -4 -br address
ip route
```

---

# 28. Prossimi passi — non ancora eseguiti

Questa sezione è una roadmap. I passaggi seguenti non fanno parte dello stato completato.

## Passo 1 — Creare snapshot

Prima di modificare forwarding o firewall:

- creare uno snapshot di Kali;
- creare uno snapshot di Parrot;
- mantenere disponibile la console virt-manager.

## Passo 2 — Collegare Parrot soltanto a `lab-lan`

In virt-manager:

- rimuovere o disconnettere l'eventuale scheda collegata a `default`;
- lasciare una sola scheda collegata a `lab-lan`.

Questo impedirà a Parrot di bypassare Kali.

## Passo 3 — Verificare il nome dell'interfaccia di Parrot

Comandi da eseguire in futuro dentro Parrot:

```bash
ip -br link
nmcli -p device status
```

Non bisogna presumere che la scheda si chiami necessariamente `eth0`.

## Passo 4 — Configurare Parrot

Configurazione prevista:

```text
IPv4: 10.10.10.3/24
gateway: 10.10.10.2
DNS: da definire per il laboratorio
```

Dopo la configurazione, il primo test dovrà essere:

```bash
ping -c 3 10.10.10.2
```

Questo test verifica soltanto la comunicazione locale tra Parrot e Kali.

## Passo 5 — Verificare lo stato di `ip_forward`

Dentro Kali sarà necessario leggere:

```bash
sysctl net.ipv4.ip_forward
```

Lettura teorica:

- valore `0`: il kernel non inoltra IPv4;
- valore `1`: il kernel può inoltrare IPv4, se il firewall lo permette.

L'attivazione non è stata ancora eseguita.

## Passo 6 — Progettare il firewall

La futura politica dovrà almeno:

- permettere le risposte `established,related`;
- permettere connessioni iniziate dalla LAN verso la WAN;
- bloccare il forwarding non autorizzato;
- usare contatori;
- evitare regole globali non necessarie.

Il ruleset non è ancora stato applicato e non è più presente come configurazione pronta nel repository, per evitare di confonderlo con lavoro già svolto.

## Passo 7 — Applicare NAT/masquerading

Il NAT dovrà essere applicato in `postrouting` sulla WAN, limitandolo alla sorgente `10.10.10.0/24`.

Obiettivo teorico:

```text
prima del NAT:
10.10.10.3 -> destinazione Internet

dopo il masquerading:
192.168.122.x -> destinazione Internet
```

Il NAT non è ancora stato configurato.

## Passo 8 — Test end-to-end

Ordine previsto dei test da Parrot:

```text
1. ping verso 10.10.10.2
2. ping verso un IP pubblico
3. test di un nome DNS
4. controllo della rotta
5. osservazione dei contatori firewall
```

## Passo 9 — Monitoraggio

Solo dopo il funzionamento del percorso si potrà aggiungere:

- `tcpdump` su `eth1`;
- `tcpdump` su `eth0`;
- statistiche `ip -s link`;
- contatori `nftables`;
- log selettivi.

## Passo 10 — Python

Il primo programma Python dovrà essere non distruttivo e limitarsi a:

- eseguire comandi di sola lettura;
- controllare codici di uscita;
- interpretare output JSON quando disponibile;
- creare un report locale;
- non richiedere privilegi se non indispensabile.

Ogni libreria e ogni parte del codice dovranno essere commentate per trasformare il progetto in materiale di studio.

## Passo 11 — Docker

Docker verrà integrato soltanto dopo che routing e NAT funzioneranno senza container.

Possibili servizi futuri:

- applicazione Python;
- database;
- dashboard;
- esportazione metriche.

Non è stato ancora creato alcun `compose.yaml` per questa funzione.

## Passo 12 — Hotspot fisico

L'hotspot con la Realtek USB verrà ripreso soltanto dopo il completamento del laboratorio virtuale.

Dovranno essere verificati separatamente:

- profilo Wi-Fi;
- canale e banda;
- password di laboratorio;
- DHCP per i client reali;
- routing;
- NAT;
- firewall;
- stabilità del driver.

---

# 29. Criterio per considerare completata la prossima fase

La prossima fase sarà completata soltanto quando sarà dimostrato che:

```text
Parrot
   |
   | unica rete: lab-lan
   v
Kali eth1
   |
   | forwarding e firewall
   | NAT sulla WAN
   v
Kali eth0
   |
   v
Internet
```

Le prove richieste saranno:

- indirizzi corretti;
- rotte corrette;
- ping locale riuscito;
- raggiungibilità di un IP pubblico;
- DNS funzionante;
- nessuna interfaccia di bypass su Parrot;
- contatori firewall in aumento;
- traffico osservabile su entrambe le interfacce di Kali.

Fino a quel momento il progetto deve essere descritto come **gateway con interfacce configurate**, non come gateway NAT completo.
