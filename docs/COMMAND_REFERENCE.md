# Riferimento dei comandi e delle opzioni

Questo documento spiega i principali comandi usati nel laboratorio. I nomi delle interfacce fisiche dell'host sono anonimizzati quando potrebbero incorporare dati hardware.

---

# 1. `ip`

`ip` appartiene al pacchetto `iproute2` e gestisce interfacce, indirizzi, rotte, vicini, tunnel e altri oggetti di rete.

Struttura generale:

```bash
ip [OPZIONI] OGGETTO COMANDO
```

## 1.1 Interfacce in formato breve

```bash
ip -br link
```

- `-br`, `-brief`: output compatto;
- `link`: mostra livello di collegamento, MAC, stato e flag.

Esempi di flag visualizzati:

- `UP`: interfaccia abilitata;
- `LOWER_UP`: collegamento operativo;
- `NO-CARRIER`: nessuna portante;
- `BROADCAST`: supporto broadcast;
- `MULTICAST`: supporto multicast;
- `LOOPBACK`: interfaccia locale del sistema.

## 1.2 Indirizzi IPv4

```bash
ip -4 -br address
```

- `-4`: limita a IPv4;
- `address`, abbreviabile in `addr`: mostra indirizzi;
- `-br`: formato compatto.

Per una sola interfaccia:

```bash
ip -4 -br address show dev eth0
```

- `show`: visualizza;
- `dev eth0`: seleziona l'interfaccia.

## 1.3 Tabella di routing

```bash
ip route
```

Esempio:

```text
default via 192.168.122.1 dev eth0 proto dhcp src 192.168.122.223 metric 100
```

- `default`: rotta di ultima scelta;
- `via`: next hop;
- `dev`: interfaccia di uscita;
- `proto dhcp`: origine DHCP;
- `src`: sorgente preferita;
- `metric`: costo.

## 1.4 Statistiche

```bash
ip -s link show dev eth1
```

- `-s`, `-statistics`: contatori RX/TX, errori e scarti;
- ripetere `-s` può mostrare più dettagli su alcuni oggetti.

## 1.5 JSON

```bash
ip -j -p address show
```

- `-j`, `-json`: output JSON;
- `-p`, `-pretty`: JSON indentato.

Questa forma sarà utile per gli script Python.

## 1.6 Attivazione e disattivazione

```bash
sudo ip link set dev eth1 up
sudo ip link set dev eth1 down
```

- `set`: modifica;
- `dev`: seleziona l'interfaccia;
- `up`/`down`: stato amministrativo.

Queste modifiche non creano un profilo persistente NetworkManager.

## 1.7 Tabella dei vicini

```bash
ip neigh show dev eth1
```

Mostra associazioni IP/MAC e stati come `REACHABLE`, `STALE`, `DELAY` o `FAILED`.

---

# 2. `nmcli`

`nmcli` è il client a riga di comando di NetworkManager.

Concetto fondamentale:

```text
device     = interfaccia
connection = profilo di configurazione
```

## 2.1 Stato dei dispositivi

```bash
nmcli -p device status
```

- `-p`, `--pretty`: tabella leggibile;
- `device status`: stato delle interfacce.

## 2.2 Profili

```bash
nmcli -p connection show
```

Mostra profili salvati e interfacce attive.

Solo profili attivi:

```bash
nmcli connection show --active
```

## 2.3 Selezione dei campi

```bash
nmcli -f DEVICE,TYPE,STATE,CONNECTION device status
```

- `-f`, `--fields`: seleziona colonne.

Solo valori:

```bash
nmcli -g GENERAL.STATE device show eth0
```

- `-g`, `--get-values`: nessuna intestazione, utile negli script.

## 2.4 Collegare un dispositivo

```bash
sudo nmcli device connect eth0
```

NetworkManager cerca un profilo compatibile e lo attiva. Nel laboratorio ha riattivato la WAN e ottenuto DHCP.

## 2.5 Creare una connessione statica

```bash
sudo nmcli connection add \
  type ethernet \
  ifname eth1 \
  con-name lab-lan-static \
  ipv4.method manual \
  ipv4.addresses 10.10.10.2/24 \
  ipv4.never-default yes \
  ipv6.method disabled
```

- `connection add`: crea un profilo;
- `type ethernet`: tipo del profilo;
- `ifname eth1`: interfaccia associata;
- `con-name`: nome umano;
- `ipv4.method manual`: configurazione statica;
- `ipv4.addresses`: indirizzo e prefisso;
- `ipv4.never-default yes`: vieta la rotta default;
- `ipv6.method disabled`: disabilita IPv6 su quel profilo.

## 2.6 Modificare un profilo

```bash
sudo nmcli connection modify lab-lan-static \
  ipv4.addresses 10.10.10.2/24 \
  ipv4.gateway "" \
  ipv4.dns "" \
  ipv4.never-default yes
```

Le stringhe vuote rimuovono gateway e DNS dal profilo LAN.

## 2.7 Attivare e disattivare

```bash
sudo nmcli connection up lab-lan-static
sudo nmcli connection down lab-lan-static
```

## 2.8 Rinominare e vincolare un profilo

```bash
sudo nmcli connection modify "Wired connection 1" \
  connection.id wan-dhcp \
  connection.interface-name eth0 \
  ipv4.method auto \
  ipv4.never-default no
```

- `connection.id`: nome del profilo;
- `connection.interface-name`: interfaccia ammessa;
- `ipv4.method auto`: DHCP;
- `ipv4.never-default no`: la WAN può fornire la default route.

## 2.9 Modalità terse

```bash
nmcli -t device status
```

- `-t`, `--terse`: output compatto per script.

## 2.10 Segreti

```bash
nmcli -s connection show
```

- `-s`, `--show-secrets`: può mostrare password. Non pubblicare l'output.

---

# 3. `lshw`

```bash
sudo lshw -class network -short
```

- `sudo`: privilegi necessari per dati completi;
- `lshw`: inventario hardware;
- `-class network`, abbreviabile `-C network`: solo rete;
- `-short`: tabella compatta.

Versione dettagliata:

```bash
sudo lshw -class network
```

Output JSON:

```bash
sudo lshw -json -class network
```

Output ripulito:

```bash
sudo lshw -sanitize -class network
```

---

# 4. `lsusb`

```bash
lsusb -t
```

- `-t`: albero USB;
- mostra bus, porte, hub, classi, driver e velocità del link.

Una voce `5000M` indica un link USB SuperSpeed nominale. Non corrisponde alla velocità del traffico Wi-Fi.

---

# 5. `ethtool`

Informazioni driver:

```bash
sudo ethtool -i <USB_WIFI_IFACE>
```

- `-i`: driver, versione, firmware e bus.

Statistiche specifiche del driver:

```bash
sudo ethtool -S <USB_WIFI_IFACE>
```

- `-S` maiuscola: statistiche.

Non tutti i driver implementano test, EEPROM o dump dei registri.

---

# 6. `iw`

`iw` interroga e configura il sottosistema wireless tramite `nl80211`.

## 6.1 Informazioni interfaccia

```bash
iw dev <USB_WIFI_IFACE> info
```

Campi comuni:

- `ifindex`: indice dell'interfaccia;
- `wdev`: identificatore wireless interno;
- `addr`: MAC;
- `type managed`: modalità client attuale;
- `wiphy 2`: radio fisica;
- `txpower`: potenza riportata.

## 6.2 Capacità della radio

```bash
iw phy phy2 info
```

## 6.3 Estrazione di una sezione

```bash
iw phy phy2 info | grep -A 15 "Supported interface modes"
```

- `|`: passa l'output al comando successivo;
- `grep`: cerca una stringa;
- `-A 15`: mostra 15 righe dopo la corrispondenza.

## 6.4 Dominio normativo

```bash
iw reg get
```

Mostra regole su canali e potenza applicabili alla radio.

---

# 7. `virsh`

`virsh` controlla libvirt e va eseguito sull'host che gestisce le VM.

## 7.1 Versione

```bash
virsh --version
```

## 7.2 Reti

```bash
virsh net-list --all
```

- `net-list`: reti virtuali;
- `--all`: attive e inattive.

Dettagli:

```bash
virsh net-info lab-lan
virsh net-dumpxml lab-lan
```

- `net-info`: stato e bridge;
- `net-dumpxml`: configurazione completa XML.

## 7.3 Avvio e autostart

```bash
sudo virsh net-start lab-lan
sudo virsh net-autostart lab-lan
```

---

# 8. `ping`

```bash
ping -c 3 1.1.1.1
```

- `-c 3`: tre richieste;
- verifica raggiungibilità ICMP e tempi.

Ordine consigliato:

```bash
ping -c 3 10.10.10.2
ping -c 3 1.1.1.1
ping -c 3 debian.org
```

Prima gateway locale, poi Internet senza DNS, infine DNS.

---

# 9. `sysctl`

Leggere:

```bash
sysctl net.ipv4.ip_forward
```

Modificare temporaneamente:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

- `-w`: scrive il valore runtime.

Persistenza:

```bash
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-gateway-lab.conf
sudo sysctl --system
```

- `tee`: scrive con privilegi nel file;
- `sysctl --system`: ricarica i file di configurazione.

---

# 10. `nft`

Visualizzare:

```bash
sudo nft list ruleset
```

Caricare un file:

```bash
sudo nft -f configs/nftables/gateway.nft.example
```

- `-f`: legge comandi da file.

Eliminare solo le tabelle del laboratorio:

```bash
sudo nft delete table inet gateway_filter
sudo nft delete table ip gateway_nat
```

Evitare il flush globale sull'host:

```bash
sudo nft flush ruleset
```

Questo comando elimina tutte le regole del namespace corrente.

---

# 11. `tcpdump`

```bash
sudo tcpdump -ni eth1
```

- `-n`: non risolve nomi;
- `-i eth1`: interfaccia;
- senza filtro mostra tutto il traffico catturabile.

Filtri:

```bash
sudo tcpdump -ni eth1 'port 53'
sudo tcpdump -ni eth1 'tcp port 443'
sudo tcpdump -ni eth1 'host 10.10.10.3'
```

---

# 12. `journalctl`

Log NetworkManager in tempo reale:

```bash
sudo journalctl -fu NetworkManager
```

- `-f`: segue nuove righe;
- `-u`: seleziona un servizio.

Log suggeriti da NetworkManager:

```bash
journalctl -xe NM_CONNECTION=<UUID> + NM_DEVICE=eth1
```

- `-x`: aggiunge spiegazioni quando disponibili;
- `-e`: parte dalla fine;
- filtri per campi del journal.

---

# 13. Operatori della shell

## 13.1 Pipe

```bash
comando1 | comando2
```

Passa lo standard output di `comando1` allo standard input di `comando2`.

## 13.2 Redirezione

```bash
comando > file
```

Sovrascrive `file` con l'output.

```bash
comando >> file
```

Aggiunge in fondo.

Il simbolo `>` mostrato dal prompt non va copiato come parte del comando.

## 13.3 Continuazione di riga

```bash
comando \
  argomento
```

La barra inversa deve essere l'ultimo carattere della riga. Spazi dopo `\` possono produrre comportamenti inattesi.

## 13.4 Codici di uscita

```bash
echo $?
```

- `0`: successo;
- valori diversi da zero: condizioni specifiche o errori;
- `grep` usa `1` per indicare nessuna corrispondenza.

---

# 14. Comandi non distruttivi per una fotografia dello stato

```bash
hostname
ip -br link
ip -4 -br address
ip route
ip neigh
nmcli -p device status
nmcli -p connection show
sysctl net.ipv4.ip_forward
sudo nft list ruleset
```

Lo script `scripts/collect-network-state.sh` automatizza questa raccolta.