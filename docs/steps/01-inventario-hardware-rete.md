# Fase 1 — Inventario hardware e rete

## Stato

```text
COMPLETATA E VERIFICATA
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
Driver: rtw88_8812au
Versione driver riportata: 7.0.0-27-generic
Bus USB: 2-5.1:1.0
Stato NetworkManager: disconnesso
Modalità attuale: managed
Modalità AP dichiarata: sì
Radio: phy8
Potenza riportata: 20 dBm
Blocco rfkill: no
Indirizzo IPv4: non assegnato
```

La scheda Realtek è quindi disponibile, non trasporta la connessione Internet dell'host e dichiara supporto alla modalità Access Point.

Il valore `firmware-version: N/A` mostrato da `ethtool` non prova che il dispositivo funzioni senza firmware. Significa soltanto che il driver non espone una versione firmware tramite questa interrogazione.

Il supporto dichiarato della modalità `AP` non dimostra ancora stabilità, prestazioni o compatibilità con tutti i canali. Questi aspetti verranno verificati durante la creazione e il collaudo dell'hotspot.

### Ethernet

```text
Interfaccia: enp12s0
Stato: DOWN / NO-CARRIER
Indirizzo IPv4: non assegnato
```

L'interfaccia Ethernet è disponibile come alternativa futura, ma al momento non ha collegamento fisico.

### Reti Docker già presenti

Sono state osservate reti create da Docker:

```text
docker0  172.17.0.1/16      bridge Docker predefinito
br-*     172.18.0.1/16      bridge Docker personalizzato
```

Queste reti devono essere considerate nella fase 2 per evitare sovrapposizioni con la subnet dell'hotspot.

## Spiegazione degli ultimi comandi

### Driver Realtek

```bash
sudo ethtool -i <AP_IF>
```

- `sudo` esegue il comando con privilegi amministrativi;
- `ethtool` interroga proprietà e capacità delle interfacce di rete;
- `-i` significa informazioni sul driver;
- `<AP_IF>` rappresenta il nome locale completo della Realtek.

Campi principali osservati:

- `driver`: modulo kernel che controlla la scheda;
- `version`: versione riportata dal driver;
- `firmware-version`: versione firmware esposta dal driver, quando disponibile;
- `bus-info`: percorso del dispositivo sul bus USB;
- `supports-statistics`: indica se il driver espone statistiche tramite `ethtool`.

Un primo errore di autenticazione `sudo` non modifica il sistema. Il comando viene eseguito soltanto dopo l'inserimento corretto della password.

### Modalità supportate dalla radio

```bash
iw phy phy8 info | grep -A 15 "Supported interface modes"
```

- `iw` interroga il sottosistema wireless Linux;
- `phy phy8` seleziona la radio fisica Realtek;
- `info` richiede tutte le informazioni disponibili;
- `|` è una pipe e passa l'output del comando a sinistra al comando a destra;
- `grep` cerca una porzione di testo;
- `-A 15` mostra la riga trovata e le quindici righe successive;
- `"Supported interface modes"` è la stringa cercata.

Modalità osservate:

- `managed`: client Wi-Fi normale;
- `AP`: Access Point;
- `AP/VLAN`: Access Point con interfacce VLAN supportate dal driver;
- `monitor`: osservazione passiva dei frame Wi-Fi;
- `IBSS`: rete ad hoc tra dispositivi.

## Checklist

- [x] identificare versione Ubuntu e kernel;
- [x] elencare interfacce e indirizzi;
- [x] identificare la route predefinita;
- [x] verificare profili NetworkManager;
- [x] identificare hardware USB e PCI;
- [x] associare MediaTek e Realtek alle rispettive interfacce;
- [x] verificare il driver MediaTek;
- [x] verificare il driver Realtek sul kernel corrente;
- [x] verificare la modalità `AP` esposta da `phy8`;
- [x] controllare `rfkill`;
- [x] inventariare le reti Docker;
- [x] anonimizzare i risultati destinati al repository.

## Valori acquisiti

```text
OS_VERSION=Ubuntu 26.04 LTS
KERNEL_VERSION=7.0.0-27-generic
UPLINK_IF=wlp13s0
UPLINK_DRIVER=mt7921e
AP_IF=wlx<REDACTED>
AP_DRIVER=rtw88_8812au
AP_PHY=phy8
DEFAULT_GATEWAY=192.168.10.1
```

## Test di completamento

La fase è completata perché sono stati verificati:

1. sistema operativo e kernel;
2. interfaccia che porta Internet;
3. hardware e driver MediaTek;
4. interfaccia destinata all'hotspot;
5. hardware e driver Realtek;
6. supporto dichiarato della modalità `AP`;
7. assenza di blocchi `rfkill`;
8. reti Docker già presenti;
9. separazione tra uplink e futura interfaccia hotspot.

## Modifiche effettuate

Nessuna configurazione di rete è stata modificata. Tutti i comandi della fase erano di sola osservazione.

## Rollback

Non necessario. Il primo tentativo di autenticazione `sudo` non ha eseguito il comando e non ha prodotto modifiche.

## Prossimo passo

Definire nella fase 2 la topologia definitiva, la subnet dell'hotspot, l'indirizzo del gateway, l'intervallo DHCP e i criteri per evitare sovrapposizioni con le reti già presenti.
