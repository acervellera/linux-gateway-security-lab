# Fase 3 — Hotspot Wi-Fi con Realtek USB

## Stato

```text
DA FARE
```

## Obiettivo

Creare un hotspot di laboratorio stabile sulla scheda Realtek USB senza interrompere la connessione Internet della MediaTek.

## Prerequisiti

- fase 1 completata;
- fase 2 completata;
- `AP_IF` e `UPLINK_IF` verificati;
- supporto `AP` dichiarato dalla radio Realtek;
- console locale disponibile;
- password di laboratorio non pubblicata nel repository.

## Approccio iniziale

La prima prova userà NetworkManager, perché consente di creare rapidamente un profilo hotspot e verificare radio, DHCP e associazione del client. In seguito separeremo le funzioni se sarà utile studiare `hostapd` e un server DHCP dedicato.

## Attività previste

- [ ] salvare lo stato dei profili NetworkManager;
- [ ] creare un profilo hotspot con nome riconoscibile;
- [ ] impostare SSID e sicurezza;
- [ ] scegliere banda e canale compatibili;
- [ ] attivare il profilo sulla sola Realtek;
- [ ] verificare che la MediaTek resti collegata;
- [ ] collegare un dispositivo autorizzato;
- [ ] verificare associazione e indirizzo assegnato;
- [ ] fermare e riattivare l'hotspot;
- [ ] verificare il comportamento dopo riavvio solo quando richiesto.

## Comandi da preparare

I comandi definitivi verranno scritti dopo aver raccolto i valori reali. La struttura sarà simile a:

```bash
nmcli connection add type wifi ifname <AP_IF> con-name <HOTSPOT_PROFILE> ssid <LAB_SSID>
nmcli connection modify <HOTSPOT_PROFILE> 802-11-wireless.mode ap
nmcli connection modify <HOTSPOT_PROFILE> ipv4.method shared
nmcli connection up <HOTSPOT_PROFILE>
```

Questi comandi sono solo una traccia. Sicurezza, banda, canale e indirizzamento devono essere configurati e spiegati prima dell'esecuzione.

## Verifiche

```bash
nmcli device status
nmcli connection show --active
iw dev <AP_IF> info
ip -4 address show dev <AP_IF>
```

Dal client controlleremo:

- visibilità dell'SSID;
- autenticazione;
- indirizzo IPv4;
- gateway ricevuto;
- DNS ricevuto;
- raggiungibilità del gateway Ubuntu.

## Condizione di completamento

L'hotspot resta attivo, il client si collega e raggiunge il gateway, mentre l'uplink MediaTek continua a funzionare.

La navigazione Internet non è ancora il criterio principale di questa fase: verrà verificata nella fase 4.

## Rollback previsto

```bash
nmcli connection down <HOTSPOT_PROFILE>
nmcli connection delete <HOTSPOT_PROFILE>
```

Prima di usarli verificheremo il nome esatto del profilo.

## Prossimo passo

Verificare DHCP, routing IPv4 e NAT.