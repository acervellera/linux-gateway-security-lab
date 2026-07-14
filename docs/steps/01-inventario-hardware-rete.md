# Fase 1 — Inventario hardware e rete

## Stato

```text
IN CORSO — raccolta principale completata, restano due verifiche Realtek
```

## Obiettivo

Identificare senza ambiguità le interfacce MediaTek e Realtek, verificare driver e capacità Wi-Fi e fotografare lo stato della rete prima di qualsiasi modifica.

## Perché serve

I nomi come `wlan0`, `wlp...` e `wlx...` non possono essere indovinati. Usare l'interfaccia sbagliata potrebbe interrompere Internet o modificare una rete non destinata al laboratorio.

## Ambiente verificato

Raccolta eseguita il 14 luglio 2026 con soli comandi di osservazione.

```text
Sistema operativo: Ubuntu 26.04 LTS (Resolute Raccoon)
Kernel: 7.0.0-27-generic
Architettura: x86_64
```

## Risultati verificati

### Uplink verso Internet

```text
Ruolo: UPLINK
Interfaccia locale: wlp13s0
Hardware: MediaTek MT7922 802.11ax
Driver: mt7921e
Configurazione IPv4 osservata: 192.168.10.x/24
Gateway predefinito: 192.168.10.1
Stato NetworkManager: collegato
Radio: phy1
Blocco rfkill: no
```

Il comando `ip route get 1.1.1.1` ha confermato che il traffico Internet usa l'interfaccia MediaTek.

### Scheda destinata all'hotspot

Il nome reale dell'interfaccia incorpora l'indirizzo MAC e non viene pubblicato integralmente nel repository.

```text
Ruolo previsto: AP / hotspot
Interfaccia pubblica: wlx<REDACTED>
Hardware USB: Realtek RTL8812AU
Identificativo USB: 0bda:8812
Stato NetworkManager: disconnesso
Modalità attuale: managed
Radio: phy8
Potenza riportata: 20 dBm
Blocco rfkill: no
Indirizzo IPv4: non assegnato
```

La scheda Realtek è quindi disponibile e non sta trasportando la connessione Internet dell'host.

### Ethernet

```text
Interfaccia: enp12s0
Stato: DOWN / NO-CARRIER
Indirizzo IPv4: non assegnato
```

L'interfaccia Ethernet è disponibile come alternativa futura, ma al momento non ha collegamento fisico.

### Reti virtuali già presenti

Sono state osservate reti create da libvirt e Docker:

```text
virbr0   192.168.122.1/24   rete libvirt default
virbr1   10.10.10.1/24      rete isolata di laboratorio
docker0  172.17.0.1/16      bridge Docker predefinito
br-*     172.18.0.1/16      bridge Docker personalizzato
vnet1 e vnet2               interfacce di VM attive
```

Queste reti devono essere considerate nella fase 2 per evitare sovrapposizioni con la subnet dell'hotspot.

## Checklist

- [x] identificare versione Ubuntu e kernel;
- [x] elencare interfacce e indirizzi;
- [x] identificare la route predefinita;
- [x] verificare profili NetworkManager;
- [x] identificare hardware USB e PCI;
- [x] associare MediaTek e Realtek alle rispettive interfacce;
- [x] verificare il driver MediaTek;
- [ ] verificare nuovamente il driver Realtek sul kernel corrente;
- [ ] verificare nuovamente la modalità `AP` esposta da `phy8`;
- [x] controllare `rfkill`;
- [x] inventariare le reti Docker e libvirt;
- [x] anonimizzare i risultati destinati al repository.

## Ultimi comandi necessari

Usare il nome reale della Realtek soltanto nel terminale locale:

```bash
# Mostra il driver caricato per la scheda Realtek.
sudo ethtool -i wlx00c0cab4ed2d

# Mostra la sezione con le modalità supportate dalla radio Realtek.
iw phy phy8 info | grep -A 15 "Supported interface modes"
```

Nel secondo output deve comparire:

```text
* AP
```

Il supporto dichiarato della modalità `AP` non dimostra ancora la stabilità dell'hotspot; quella verrà verificata nella fase 3.

## Valori acquisiti

```text
OS_VERSION=Ubuntu 26.04 LTS
KERNEL_VERSION=7.0.0-27-generic
UPLINK_IF=wlp13s0
UPLINK_DRIVER=mt7921e
AP_IF=wlx<REDACTED>
AP_DRIVER=DA_RIVERIFICARE
AP_PHY=phy8
DEFAULT_GATEWAY=192.168.10.1
```

## Test di completamento

La fase sarà chiusa quando saranno confermati anche:

1. il driver Realtek effettivamente caricato sul kernel corrente;
2. la presenza della modalità `AP` tra le capacità di `phy8`.

## Modifiche vietate in questa fase

Non creare ancora hotspot, non abilitare forwarding, non modificare `nftables` e non disattivare connessioni esistenti.

## Rollback

Non previsto: i comandi della fase sono di osservazione. Se viene eseguito accidentalmente un comando modificativo, documentarlo immediatamente prima di proseguire.

## Prossimo passo

Dopo i due controlli mancanti, chiudere la fase 1 e definire topologia e piano di indirizzamento nella fase 2.
