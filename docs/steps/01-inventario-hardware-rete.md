# Fase 1 — Inventario hardware e rete

## Stato

```text
IN CORSO
```

## Obiettivo

Identificare senza ambiguità le interfacce MediaTek e Realtek, verificare driver e capacità Wi-Fi e fotografare lo stato della rete prima di qualsiasi modifica.

## Perché serve

I nomi come `wlan0`, `wlp...` e `wlx...` non possono essere indovinati. Usare l'interfaccia sbagliata potrebbe interrompere Internet o modificare una rete non destinata al laboratorio.

## Attività previste

- [ ] identificare versione Ubuntu e kernel;
- [ ] elencare interfacce e indirizzi;
- [ ] identificare la route predefinita;
- [ ] verificare profili NetworkManager;
- [ ] identificare hardware USB e PCI;
- [ ] associare ogni interfaccia al relativo hardware;
- [ ] verificare driver;
- [ ] verificare modalità AP;
- [ ] controllare `rfkill`;
- [ ] verificare eventuali conflitti con Docker e libvirt;
- [ ] anonimizzare e registrare gli output.

## Comandi di sola lettura

```bash
# Sistema operativo e kernel.
cat /etc/os-release
uname -a

# Stato delle interfacce e indirizzi IPv4.
ip -br link
ip -4 -br address

# Rotte e interfaccia usata per uscire verso Internet.
ip route
ip route get 1.1.1.1

# Stato dei dispositivi e dei profili NetworkManager.
nmcli device status
nmcli connection show

# Hardware USB e PCI.
lsusb
lspci -nnk | grep -A 4 -Ei 'network|wireless'

# Interfacce wireless e blocchi radio.
iw dev
rfkill list
```

## Verifica specifica della Realtek

Dopo aver identificato la radio e l'interfaccia:

```bash
sudo ethtool -i <AP_IF>
iw dev <AP_IF> info
iw phy <PHY_REALTEK> info
```

Nel risultato di `iw phy` deve comparire la modalità:

```text
* AP
```

Questo dimostra il supporto dichiarato, non ancora la stabilità dell'hotspot.

## Valori da ottenere

```text
OS_VERSION=
KERNEL_VERSION=
UPLINK_IF=
UPLINK_DRIVER=
AP_IF=
AP_DRIVER=
AP_PHY=
DEFAULT_GATEWAY=
```

## Test di completamento

La fase è completata quando possiamo rispondere con certezza:

1. quale scheda porta Internet;
2. quale scheda verrà usata come hotspot;
3. quale driver usa ciascuna scheda;
4. quale radio supporta `AP`;
5. quali reti virtuali sono già presenti;
6. quali nomi reali useremo nei documenti successivi.

## Modifiche vietate in questa fase

Non creare ancora hotspot, non abilitare forwarding, non modificare `nftables` e non disattivare connessioni esistenti.

## Rollback

Non previsto: i comandi della fase sono di osservazione. Se viene eseguito accidentalmente un comando modificativo, documentarlo immediatamente prima di proseguire.

## Prossimo passo

Definire topologia e piano di indirizzamento nella fase 2.