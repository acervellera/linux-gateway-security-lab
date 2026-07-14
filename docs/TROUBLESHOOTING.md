# Troubleshooting del gateway

Questa guida usa un metodo a strati. Non modificare più componenti contemporaneamente: verificare prima il livello più basso e procedere solo dopo che funziona.

---

# 1. Identificare la macchina corretta

Prima di ogni comando:

```bash
hostname
whoami
pwd
```

Nel progetto esistono almeno tre ambienti:

- Ubuntu host;
- Kali gateway;
- Parrot client.

`virsh` va normalmente eseguito sull'host. `nftables` del gateway va configurato dentro Kali. La configurazione client va applicata dentro Parrot.

---

# 2. Controllare le interfacce

```bash
ip -br link
```

Atteso su Kali:

```text
eth0  UP ... LOWER_UP
eth1  UP ... LOWER_UP
```

Problemi:

- interfaccia assente: controllare l'hardware virtuale in virt-manager;
- `DOWN`: attivare il profilo o il link;
- nessun `LOWER_UP`: controllare che la scheda sia collegata a una rete virtuale attiva.

---

# 3. Controllare NetworkManager

```bash
nmcli -p device status
nmcli -p connection show
```

Atteso su Kali:

```text
eth0 -> wan-dhcp
eth1 -> lab-lan-static
```

Se il profilo DHCP tenta di attivarsi su `eth1`, verificare:

```bash
nmcli -g connection.interface-name connection show wan-dhcp
```

Deve restituire `eth0`.

---

# 4. Controllare gli indirizzi

```bash
ip -4 -br address
```

Atteso su Kali:

```text
eth0  192.168.122.x/24
eth1  10.10.10.2/24
```

Atteso su Parrot:

```text
interfaccia-client  10.10.10.3/24
```

Errori comuni:

- indirizzo duplicato;
- prefisso errato;
- IP assegnato all'interfaccia sbagliata;
- client su una subnet diversa;
- indirizzo della rete `.0` usato come host;
- broadcast `.255` assegnato a un host.

---

# 5. Controllare le rotte

Su Kali:

```bash
ip route
```

Atteso:

```text
default via 192.168.122.1 dev eth0
10.10.10.0/24 dev eth1
192.168.122.0/24 dev eth0
```

Su Parrot:

```text
default via 10.10.10.2 dev <client-iface>
10.10.10.0/24 dev <client-iface>
```

Problemi comuni:

- nessuna default route;
- default route sulla LAN di Kali;
- due default route concorrenti;
- gateway non appartenente alla subnet locale;
- Parrot ancora collegata alla rete libvirt `default`.

---

# 6. Testare il collegamento locale

Da Parrot:

```bash
ping -c 3 10.10.10.2
```

Se fallisce:

1. verificare che entrambe le VM siano su `lab-lan`;
2. controllare indirizzi e prefissi;
3. controllare `ip neigh`;
4. osservare con `tcpdump` su Kali:

```bash
sudo tcpdump -ni eth1 'icmp or arp'
```

Se non appare alcun pacchetto, il problema è prima di Kali.

---

# 7. Testare la WAN di Kali

Da Kali:

```bash
ping -c 3 192.168.122.1
ping -c 3 1.1.1.1
ping -c 3 debian.org
```

Interpretazione:

- gateway fallisce: problema tra Kali e libvirt `default`;
- gateway funziona ma IP pubblico no: problema di NAT libvirt o host;
- IP pubblico funziona ma nome no: problema DNS.

---

# 8. Controllare il forwarding

```bash
sysctl net.ipv4.ip_forward
```

Atteso:

```text
net.ipv4.ip_forward = 1
```

Se restituisce `0`:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

Questa modifica è temporanea.

---

# 9. Controllare `nftables`

```bash
sudo nft list ruleset
```

Verificare:

- chain con hook `forward`;
- regola `established,related`;
- regola `eth1` verso `eth0`;
- NAT in `postrouting`;
- `masquerade` limitato alla subnet LAN;
- assenza di errori nei nomi delle interfacce.

Per vedere le tabelle del laboratorio:

```bash
sudo nft list table inet gateway_filter
sudo nft list table ip gateway_nat
```

---

# 10. Osservare il pacchetto sui due lati

Aprire due terminali su Kali.

Terminale LAN:

```bash
sudo tcpdump -ni eth1 'icmp or port 53'
```

Terminale WAN:

```bash
sudo tcpdump -ni eth0 'icmp or port 53'
```

Poi generare traffico da Parrot.

## Interpretazione

### Pacchetto non presente su `eth1`

Problema client o rete `lab-lan`.

### Presente su `eth1`, assente su `eth0`

Problema di forwarding o chain `forward`.

### Presente su entrambi, sorgente ancora `10.10.10.3`

NAT non applicato.

### Presente su `eth0` con sorgente WAN, nessuna risposta

Controllare default route di Kali, NAT libvirt e destinazione.

### Risposta presente su `eth0`, assente su `eth1`

Controllare connection tracking e regola `established,related`.

---

# 11. Controllare i contatori

```bash
sudo nft list ruleset
ip -s link show dev eth0
ip -s link show dev eth1
```

Se i contatori di una regola restano a zero, il pacchetto non la sta attraversando oppure una regola precedente prende la decisione.

---

# 12. Problemi DNS

Se:

```bash
ping -c 3 1.1.1.1
```

funziona, ma:

```bash
ping -c 3 debian.org
```

fallisce, controllare:

```bash
resolvectl status
nmcli device show
cat /etc/resolv.conf
```

Su Parrot verificare che il profilo contenga DNS validi.

---

# 13. Problemi NetworkManager

Log in tempo reale:

```bash
sudo journalctl -fu NetworkManager
```

Dettagli di un profilo:

```bash
nmcli connection show wan-dhcp
nmcli connection show lab-lan-static
```

Riattivazione controllata:

```bash
sudo nmcli connection down lab-lan-static
sudo nmcli connection up lab-lan-static
```

Non disattivare la WAN durante una sessione remota senza console di emergenza.

---

# 14. Problemi libvirt

Sull'host:

```bash
virsh net-list --all
virsh net-info default
virsh net-info lab-lan
virsh net-dumpxml lab-lan
```

Controllare che:

- entrambe le reti siano attive;
- `default` usi NAT;
- `lab-lan` sia isolata;
- le schede delle VM siano collegate alle reti corrette.

---

# 15. Rollback

Per rimuovere solo il ruleset del laboratorio:

```bash
sudo nft delete table inet gateway_filter
sudo nft delete table ip gateway_nat
```

Per disattivare il forwarding runtime:

```bash
sudo sysctl -w net.ipv4.ip_forward=0
```

Per rimuovere la persistenza, se creata:

```bash
sudo rm /etc/sysctl.d/99-gateway-lab.conf
sudo sysctl --system
```

Per problemi gravi, usare lo snapshot della VM.

---

# 16. Raccolta dello stato

Eseguire:

```bash
sudo ./scripts/collect-network-state.sh
```

Lo script non modifica la rete. Produce un report utile per confrontare lo stato prima e dopo una modifica.

Prima di condividere il report, controllare che non contenga dati che non si desidera pubblicare.