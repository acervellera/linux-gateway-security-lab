# Fase 6 — Cattura del traffico con tcpdump

## Stato

```text
DA FARE
```

## Obiettivo

Imparare a osservare il traffico che attraversa il gateway e confermare il percorso dei pacchetti sui due lati.

## Concetti da studiare

- pacchetto e frame;
- interfaccia di cattura;
- filtri BPF;
- differenza tra DNS, TCP, UDP, ICMP e TLS;
- indirizzi prima e dopo il NAT;
- snapshot length;
- formato PCAP;
- limiti di privacy.

## Prime osservazioni

```bash
sudo tcpdump -ni <AP_IF>
sudo tcpdump -ni <UPLINK_IF>
```

Spiegheremo:

- `-n`: non risolvere nomi;
- `-i`: scegliere l'interfaccia;
- perché evitare una cattura senza limiti per troppo tempo.

## Filtri previsti

```bash
# Traffico del solo client.
sudo tcpdump -ni <AP_IF> host <CLIENT_IP>

# DNS tradizionale.
sudo tcpdump -ni <AP_IF> 'udp port 53 or tcp port 53'

# Handshake TCP e traffico web cifrato.
sudo tcpdump -ni <AP_IF> 'tcp port 80 or tcp port 443'

# ICMP per i test ping.
sudo tcpdump -ni <AP_IF> icmp
```

I comandi definitivi verranno adattati ai valori reali.

## Confronto prima e dopo il NAT

Eseguiremo due catture brevi:

1. sulla Realtek, dove la sorgente sarà il client;
2. sulla MediaTek, dove la sorgente potrà essere l'indirizzo del gateway dopo il masquerading.

Questo test serve a rendere visibile il funzionamento del NAT.

## Salvataggio controllato

```bash
sudo tcpdump -ni <AP_IF> -c <NUMERO_PACCHETTI> -w <FILE.pcap> <FILTRO>
```

Ogni cattura deve avere:

- limite di pacchetti o durata;
- filtro preciso;
- dispositivo di test noto;
- revisione prima della conservazione;
- esclusione dal repository salvo esempio anonimizzato.

## Test di completamento

- [ ] richiesta DNS osservata;
- [ ] ping osservato;
- [ ] handshake TCP osservato;
- [ ] traffico TLS riconosciuto senza decifrarne il contenuto;
- [ ] stesso flusso riconosciuto sui due lati;
- [ ] effetto del NAT compreso;
- [ ] nessun PCAP sensibile pubblicato.

## Rollback

`tcpdump` non modifica la rete. Terminare la cattura con `Ctrl+C` e rimuovere in modo sicuro eventuali file non necessari.

## Prossimo passo

Installare e configurare Suricata usando le conoscenze ottenute dalle catture manuali.