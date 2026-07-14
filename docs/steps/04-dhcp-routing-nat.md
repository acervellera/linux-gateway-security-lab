# Fase 4 — DHCP, routing IPv4 e NAT

## Stato

```text
DA FARE
```

## Obiettivo

Fare in modo che un client collegato all'hotspot usi Ubuntu come gateway e raggiunga Internet esclusivamente tramite l'interfaccia MediaTek.

## Concetti da comprendere

- DHCP assegna indirizzo, subnet, gateway e DNS;
- il routing decide dove inoltrare i pacchetti;
- `net.ipv4.ip_forward` abilita l'inoltro IPv4 nel kernel;
- il NAT modifica l'indirizzo sorgente dei pacchetti in uscita;
- il masquerading è adatto quando l'indirizzo dell'uplink può cambiare.

## Ordine dei test

1. client associato all'hotspot;
2. indirizzo DHCP ricevuto;
3. ping client → gateway;
4. verifica route del client;
5. verifica forwarding sul gateway;
6. connessione verso un IP esterno;
7. risoluzione DNS;
8. controllo del percorso con `tcpdump`;
9. verifica che il client non possieda un percorso alternativo.

## Osservazione iniziale

```bash
ip -4 address
ip -4 route
sysctl net.ipv4.ip_forward
nmcli connection show <HOTSPOT_PROFILE>
```

## Attivazione temporanea del forwarding

Il comando definitivo verrà eseguito soltanto con console locale e stato salvato:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

La persistenza verrà configurata solo dopo i test.

## NAT

Il NAT verrà implementato in modo esplicito e documentato con `nftables`. Se NetworkManager crea temporaneamente regole automatiche con `ipv4.method shared`, queste verranno prima osservate e comprese.

La regola definitiva dovrà essere limitata almeno da:

- subnet del laboratorio;
- interfaccia di uscita;
- famiglia IPv4.

## Verifiche sul gateway

```bash
ip route get 1.1.1.1
sudo nft list ruleset
sudo conntrack -L 2>/dev/null || true
```

## Verifiche dal client

```bash
ip -4 address
ip -4 route
ping -c 3 <GATEWAY_IP>
ping -c 3 1.1.1.1
getent hosts example.com
```

## Condizione di completamento

- il client riceve configurazione corretta;
- il client raggiunge Ubuntu;
- il client raggiunge un IP Internet;
- il DNS funziona;
- il traffico passa sulla Realtek in ingresso e sulla MediaTek in uscita;
- il comportamento è ripetibile;
- forwarding e NAT hanno una procedura di rollback.

## Rollback

La procedura dovrà includere:

```bash
sudo sysctl -w net.ipv4.ip_forward=0
```

oltre alla rimozione mirata delle sole regole NAT create dal progetto. Non verrà usato un `flush ruleset` indiscriminato.

## Prossimo passo

Sostituire le regole provvisorie con un firewall `nftables` stateful e controllato.