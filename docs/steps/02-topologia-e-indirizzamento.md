# Fase 2 — Topologia e piano di indirizzamento

## Stato

```text
DA FARE
```

## Obiettivo

Definire prima delle modifiche il ruolo delle interfacce, la subnet del laboratorio, gli indirizzi e il percorso previsto dei pacchetti.

## Prerequisito

La fase 1 deve aver identificato:

```text
UPLINK_IF=<MediaTek>
AP_IF=<Realtek USB>
```

## Topologia prevista

```text
Client di test
    |
    | Wi-Fi laboratorio
    v
<AP_IF> — Ubuntu gateway — <UPLINK_IF>
                                |
                                v
                             Internet
```

## Decisioni da prendere

- subnet IPv4 del laboratorio;
- indirizzo del gateway;
- intervallo DHCP;
- durata dei lease;
- DNS distribuito ai client;
- nome del profilo hotspot;
- SSID di laboratorio non personale;
- banda e canale;
- eventuale isolamento tra client;
- comportamento IPv6 iniziale;
- convivenza con Docker e libvirt.

## Controllo dei conflitti

Prima di scegliere la subnet, confrontarla con:

```bash
ip -4 route
ip -4 address
nmcli connection show
virsh net-list --all
docker network ls
```

Se disponibili, controllare anche le subnet Docker:

```bash
docker network inspect <NOME_RETE>
```

## Piano iniziale proposto

Da confermare dopo l'inventario:

```text
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
DHCP_START=10.42.0.50
DHCP_END=10.42.0.200
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
```

Questi valori sono esempi. Non devono essere applicati se la rete `10.42.0.0/24` è già usata da NetworkManager o da un'altra rete locale.

## Percorso dei pacchetti

```text
client
  -> AP_IF
  -> decisione firewall nella chain forward
  -> routing kernel
  -> NAT/masquerading
  -> UPLINK_IF
  -> Internet
```

La risposta deve tornare attraverso la connessione già tracciata dal kernel.

## Tabella da completare

| Elemento | Valore verificato |
|---|---|
| Interfaccia uplink | |
| Interfaccia hotspot | |
| Subnet laboratorio | |
| Gateway | |
| Range DHCP | |
| DNS | |
| Profilo hotspot | |
| SSID anonimizzato | |
| Banda | |
| Canale | |
| Gestione IPv6 | |

## Test di completamento

- [ ] nessun conflitto di subnet;
- [ ] percorso dei pacchetti disegnato;
- [ ] valori salvati nel documento;
- [ ] nessun segreto pubblicato;
- [ ] nomi delle interfacce verificati;
- [ ] piano di rollback per il profilo hotspot definito.

## Rollback

In questa fase non si applicano modifiche. Se viene creato un profilo di prova, deve essere rimosso esplicitamente e registrato nel documento.

## Prossimo passo

Creare e verificare l'hotspot sulla Realtek USB.