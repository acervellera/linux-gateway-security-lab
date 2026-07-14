# Architettura del laboratorio

## 1. Scopo della topologia

La topologia separa chiaramente tre domini:

1. rete esterna virtuale, fornita da libvirt;
2. gateway Linux, rappresentato dalla VM Kali;
3. rete interna isolata, contenente il client Parrot.

```text
Internet
   |
Ubuntu host
   |
virbr0 / libvirt default
192.168.122.0/24
   |
Kali
|-- eth0 192.168.122.223/24
`-- eth1 10.10.10.2/24
       |
       | lab-lan 10.10.10.0/24
       |
       `-- Parrot 10.10.10.3/24
```

## 2. Ruolo dell'host Ubuntu

L'host esegue:

- KVM/QEMU;
- libvirt;
- virt-manager;
- Docker;
- la connessione reale verso Internet.

L'host non è ancora il gateway studiato. Fornisce soltanto l'infrastruttura virtuale e l'uscita esterna della rete `default`.

## 3. Rete libvirt `default`

La rete `default` rappresenta la WAN virtuale di Kali.

```text
subnet: 192.168.122.0/24
gateway: 192.168.122.1
bridge: virbr0
DHCP: attivo
forwarding: NAT
```

Kali riceve automaticamente un indirizzo tramite DHCP. L'indirizzo osservato durante il laboratorio è `192.168.122.223/24`.

## 4. Rete isolata `lab-lan`

`lab-lan` rappresenta la rete interna controllata.

```text
subnet: 10.10.10.0/24
DHCP: disabilitato
forwarding libvirt: isolato
```

L'isolamento è essenziale: Parrot non deve possedere un percorso esterno indipendente da Kali.

## 5. Kali come router

Kali possiede due interfacce:

| Interfaccia | Ruolo | Configurazione |
|---|---|---|
| `eth0` | WAN | DHCP, `192.168.122.223/24`, default via `192.168.122.1` |
| `eth1` | LAN | statico, `10.10.10.2/24`, nessun gateway |

Kali diventa router quando:

1. `net.ipv4.ip_forward` è impostato a `1`;
2. la chain `forward` consente il traffico desiderato;
3. il NAT modifica la sorgente dei pacchetti LAN in uscita.

## 6. Parrot come client

Parrot dovrà avere:

```text
IPv4: 10.10.10.3/24
gateway: 10.10.10.2
DNS: server scelti per il laboratorio
unica interfaccia: lab-lan
```

Non deve essere collegata alla rete libvirt `default`.

## 7. Flusso dei pacchetti

### 7.1 Richiesta in uscita

```text
1. Parrot genera il pacchetto.
2. La destinazione non appartiene a 10.10.10.0/24.
3. Parrot usa il gateway 10.10.10.2.
4. Il pacchetto entra in Kali su eth1.
5. Il kernel consulta la tabella di routing.
6. La rotta default indica eth0 e 192.168.122.1.
7. La chain forward valuta il pacchetto.
8. La regola LAN -> WAN lo accetta.
9. La chain postrouting applica masquerade.
10. Il pacchetto esce da eth0 con sorgente WAN di Kali.
```

### 7.2 Risposta

```text
1. La risposta torna all'indirizzo WAN di Kali.
2. Il connection tracking riconosce la traduzione NAT.
3. Viene ricostruita la destinazione interna.
4. La regola established,related accetta la risposta.
5. Kali inoltra il pacchetto su eth1.
6. Parrot riceve la risposta.
```

## 8. Piano di rete e piano applicativo

Il progetto separa due responsabilità.

### Piano di rete

Eseguito direttamente nella VM Kali:

- indirizzi;
- rotte;
- forwarding;
- firewall;
- NAT;
- cattura diagnostica.

### Piano applicativo

Eseguito in futuro tramite Docker:

- raccolta metriche;
- analisi Python;
- database;
- dashboard;
- proxy esplicito opzionale.

## 9. Evoluzione fisica

La topologia virtuale verrà sostituita da due interfacce reali:

```text
router domestico
     |
interfaccia WAN Ubuntu
     |
routing + firewall + NAT
     |
interfaccia LAN / hotspot
     |
client reali
```

La radio USB Realtek RTL8812AU ha dichiarato supporto alla modalità AP. La fase fisica richiederà ulteriori test di stabilità, DHCP, DNS, canale radio e persistenza.