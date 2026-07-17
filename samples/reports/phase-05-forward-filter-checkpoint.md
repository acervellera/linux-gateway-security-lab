# Fase 5 — Checkpoint storico filtro FORWARD nftables

Data del checkpoint: 16 luglio 2026.

## Stato

```text
CHECKPOINT STORICO — SUPERATO DAL REPORT FINALE DEL 17 LUGLIO 2026
```

Questo documento conserva il punto intermedio nel quale era stato verificato soltanto il filtro `FORWARD`. La fase 5 è stata successivamente completata con:

- filtro `INPUT`;
- test attivi dei blocchi verso il gateway e la rete libvirt;
- logging con rate limit;
- script di caricamento;
- servizio systemd dedicato;
- persistenza dopo reboot.

Usare come riferimento aggiornato:

- [`../../docs/steps/05-firewall-nftables.md`](../../docs/steps/05-firewall-nftables.md);
- [`phase-05-firewall-nftables-final.md`](phase-05-firewall-nftables-final.md).

## Ambiente pubblico del checkpoint

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
CLIENT_IP=10.42.0.x
```

Il gateway usava già regole dinamiche create da NetworkManager, Docker e libvirt. Il servizio standard `nftables.service` era disabilitato e non è mai stato eseguito `nft flush ruleset`.

## Politica FORWARD già verificata al checkpoint

```text
hotspot -> uplink, new/established/related  ACCEPT
uplink -> hotspot, established/related      ACCEPT
uplink -> hotspot, new                      DROP
invalid sul percorso hotspot/uplink         DROP
hotspot -> altre interfacce                 DROP
altre interfacce -> hotspot                 DROP
traffico non collegato all'hotspot          invariato
```

Durante traffico reale erano aumentati i contatori delle due regole `accept`. In quel momento le regole finali di blocco non avevano ancora ricevuto un test attivo.

## Coesistenza già verificata

Dopo il caricamento erano rimaste presenti e operative:

- la chain NetworkManager `nm-sh-fw-<AP_IF>`;
- la chain `DOCKER-FORWARD`;
- le chain libvirt;
- DHCP e DNS dell'hotspot;
- il NAT/masquerading della subnet del laboratorio.

## Rollback già verificato

La tabella era stata rimossa esclusivamente con:

```bash
sudo nft delete table inet security_gateway_filter
```

NetworkManager, Docker e libvirt erano rimasti operativi. Il file era stato poi controllato e ricaricato:

```bash
sudo nft --check --file "$FILTER_FILE"
sudo nft --file "$FILTER_FILE"
```

## Evoluzione successiva

Il report finale documenta prove ulteriori non ancora presenti in questo checkpoint:

```text
TCP 631 verso il gateway                LOG + DROP
hotspot verso 192.168.122.0/24          LOG + DROP
mDNS dall'hotspot                       DROP
DHCP e DNS                              ACCEPT
logging limitato                        verificato
reload tramite systemd                  verificato
persistenza dopo reboot                 verificata
```

Questo file resta nel repository per mostrare l'evoluzione reale del lavoro e la differenza tra un checkpoint intermedio e una fase completata.