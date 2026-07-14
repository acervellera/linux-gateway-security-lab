# Fase 11 — Test finali, hardening e backup

## Stato

```text
DA FARE
```

## Obiettivo

Verificare che il gateway sia ripetibile, sicuro, osservabile e ripristinabile anche dopo errori o riavvii.

## Test end-to-end

Il dispositivo di laboratorio deve:

1. collegarsi all'hotspot;
2. ricevere indirizzo, gateway e DNS corretti;
3. raggiungere Ubuntu;
4. raggiungere Internet attraverso la MediaTek;
5. essere filtrato da `nftables`;
6. comparire nelle catture `tcpdump`;
7. generare log Suricata;
8. generare log Zeek;
9. comparire nei report Python;
10. comparire nella dashboard.

## Test negativi

- uplink disconnesso;
- hotspot fermato;
- forwarding disabilitato;
- regola firewall volutamente restrittiva;
- Suricata fermata;
- Zeek fermato;
- importer Python fermato;
- database non disponibile;
- disco quasi pieno simulato in modo sicuro;
- file di log malformato;
- riavvio del gateway.

Ogni test deve indicare il comportamento atteso e quello osservato.

## Hardening

Valuteremo:

- servizi in ascolto;
- accesso amministrativo;
- aggiornamenti di sicurezza;
- permessi su configurazioni e log;
- utenti dei servizi;
- porte pubblicate da Docker;
- policy firewall;
- protezione da log eccessivi;
- rotazione;
- spazio disco;
- sincronizzazione oraria;
- disattivazione dei componenti non usati.

## Comandi di inventario finale

```bash
ss -lntup
systemctl --failed
sudo nft list ruleset
ip -4 address
ip -4 route
nmcli connection show --active
docker compose ps
```

I percorsi e i servizi effettivi verranno aggiunti durante il collaudo.

## Backup

Dovranno essere salvati almeno:

- profili NetworkManager esportabili o ricostruibili;
- configurazione `nftables`;
- configurazione Suricata;
- configurazione Zeek;
- codice Python;
- file Compose;
- schema e backup database;
- elenco dei pacchetti;
- documentazione dei valori usati.

I backup non devono includere password in chiaro o log personali non necessari.

## Ripristino

La procedura deve poter ricostruire il laboratorio in ordine:

1. interfacce;
2. hotspot;
3. DHCP e indirizzamento;
4. forwarding;
5. firewall e NAT;
6. Suricata;
7. Zeek;
8. Python;
9. Docker;
10. test end-to-end.

## Smontaggio del laboratorio

Documentare anche come:

- fermare i servizi;
- disattivare l'hotspot;
- rimuovere le sole regole del progetto;
- disabilitare forwarding se non serve ad altro;
- arrestare i container;
- conservare o cancellare i dati;
- ripristinare la configurazione iniziale.

## Condizione di completamento

Il progetto è completo quando:

- tutti i test positivi passano;
- i test negativi falliscono nel modo previsto;
- il gateway riparte correttamente;
- esiste un backup verificato;
- esiste un ripristino verificato;
- esiste una procedura di smontaggio;
- la documentazione descrive soltanto risultati reali.