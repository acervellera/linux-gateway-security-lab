# Fase 5 — Firewall con nftables

## Stato

```text
DA FARE
```

## Obiettivo

Creare un firewall stateful che protegga Ubuntu e permetta soltanto il traffico necessario dal laboratorio verso Internet.

## Prerequisiti

- hotspot funzionante;
- DHCP, routing e NAT verificati;
- nomi delle interfacce confermati;
- accesso locale alla macchina;
- backup del ruleset attuale;
- procedura di rollback pronta.

## Concetti da studiare

- table, chain e rule;
- hook `input`, `forward`, `output`, `prerouting` e `postrouting`;
- priorità;
- policy;
- connection tracking;
- stati `new`, `established`, `related` e `invalid`;
- differenza tra filtro e NAT;
- contatori;
- logging con rate limit.

## Backup obbligatorio

```bash
sudo nft list ruleset > nftables-before-lab.nft
```

Il file deve essere revisionato prima di essere pubblicato.

## Politica prevista

Il ruleset definitivo dovrà:

- permettere loopback;
- non interrompere la connessione amministrativa in uso;
- accettare traffico di ritorno `established,related`;
- scartare traffico `invalid`;
- permettere DHCP e DNS necessari sull'interfaccia hotspot;
- permettere inoltro dal laboratorio verso l'uplink;
- bloccare inoltri non previsti;
- limitare il NAT alla subnet del laboratorio;
- registrare eventi selezionati senza riempire il disco.

## Strategia sicura

1. scrivere il ruleset in un file;
2. controllare la sintassi;
3. caricarlo con console locale;
4. verificare accesso al gateway;
5. verificare navigazione del client;
6. controllare contatori;
7. rendere persistente solo dopo successo.

## Controllo sintattico

```bash
sudo nft --check --file <RULESET_FILE>
```

## Verifiche

```bash
sudo nft list ruleset
sudo nft list ruleset -a
sudo nft monitor trace
```

`nft monitor trace` verrà usato solo per test brevi e controllati.

## Test richiesti

- [ ] client → gateway consentito solo per i servizi previsti;
- [ ] client → Internet consentito;
- [ ] risposta Internet → client consentita tramite connessione esistente;
- [ ] nuove connessioni WAN → client bloccate;
- [ ] traffico invalido bloccato;
- [ ] contatori incrementano;
- [ ] rollback verificato.

## Rollback

Il rollback deve ripristinare il file salvato oppure rimuovere esclusivamente la table creata dal progetto. Non usare `nft flush ruleset` senza aver verificato che non esistano regole appartenenti al sistema o ad altri servizi.

## File previsto

```text
configs/nftables/security-gateway.nft
```

Il file verrà creato solo dopo una prova reale.

## Prossimo passo

Osservare il traffico con `tcpdump` prima di installare IDS e analizzatori.