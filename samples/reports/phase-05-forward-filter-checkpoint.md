# Fase 5 — Checkpoint filtro FORWARD nftables

Data verifica: 16 luglio 2026.

## Stato

```text
CHECKPOINT VERIFICATO — FILTRO FORWARD ATTIVO, INPUT NON ANCORA IMPLEMENTATO
```

Questo checkpoint documenta la parte completata della fase 5 senza pubblicare nomi completi delle interfacce, indirizzi MAC o output locali completi.

## Ambiente pubblico

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
CLIENT_IP=10.42.0.x
```

Il gateway usa regole dinamiche create da NetworkManager, Docker e libvirt. Il servizio `nftables.service` resta disabilitato durante i test e non è stato eseguito `nft flush ruleset`.

## Tabelle del progetto

```text
table inet security_gateway
    osservazione con soli counter
    hook input e forward
    priority -10
    policy accept

table inet security_gateway_filter
    filtro reale del traffico inoltrato
    hook forward
    priority -20
    policy accept
```

## Politica FORWARD verificata

```text
hotspot -> uplink, new/established/related  ACCEPT
uplink -> hotspot, established/related      ACCEPT
uplink -> hotspot, new                      DROP
invalid sul percorso hotspot/uplink         DROP
hotspot -> altre interfacce                 DROP
altre interfacce -> hotspot                 DROP
traffico non collegato all'hotspot          invariato
```

Durante traffico reale sono aumentati i contatori delle due regole `accept`. Le regole `drop` non hanno incontrato traffico corrispondente durante la prova e sono rimaste a zero.

## Coesistenza con regole dinamiche

Dopo il caricamento del filtro sono rimaste presenti e operative:

- la chain NetworkManager `nm-sh-fw-<AP_IF>`;
- la chain `DOCKER-FORWARD`;
- la chain `LIBVIRT_FWI`;
- DHCP e DNS dell'hotspot;
- il NAT/masquerading della subnet del laboratorio.

La navigazione del client è proseguita e i contatori NetworkManager hanno continuato ad aumentare.

## Rollback verificato

Il filtro reale è stato rimosso esclusivamente con:

```bash
sudo nft delete table inet security_gateway_filter
```

La tabella è risultata assente, mentre NetworkManager, Docker e libvirt sono rimasti operativi. Il file è stato poi ricontrollato e ricaricato:

```bash
sudo nft --check --file "$FILTER_FILE"
sudo nft --file "$FILTER_FILE"
```

Dopo la ricarica i contatori sono ripartiti da zero e hanno ricominciato ad aumentare con traffico reale.

## Risultati verificati

- [x] client verso Internet consentito;
- [x] risposte Internet verso client consentite tramite connessione esistente;
- [x] contatori incrementati;
- [x] rollback e ricaricamento del filtro reale;
- [x] coesistenza con NetworkManager;
- [x] presenza delle chain Docker e libvirt;
- [ ] filtro INPUT del gateway;
- [ ] test attivo di nuove connessioni uplink verso client;
- [ ] test controllato di traffico `invalid`;
- [ ] logging con rate limit;
- [ ] persistenza dopo riavvio.

## Punto di ripresa

La fase riprenderà con l'inventario delle porte in ascolto e delle connessioni amministrative prima di applicare regole `INPUT` al traffico destinato direttamente a Ubuntu.
