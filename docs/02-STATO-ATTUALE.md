# Stato attuale del progetto

Ultimo riordino documentale: 14 luglio 2026.

## Nota importante

Questo documento distingue ciò che era già stato registrato nel repository da ciò che deve ancora essere verificato per il nuovo obiettivo principale: **Ubuntu come gateway fisico con hotspot Realtek e uplink MediaTek**.

## Informazioni già documentate

Nel materiale precedente risultano documentati:

- host principale Ubuntu;
- Wi-Fi interna MediaTek MT7922 usata come collegamento alla rete domestica;
- Wi-Fi USB Realtek RTL8812AU disponibile per il laboratorio;
- driver Realtek osservato: `rtw88_8812au`;
- supporto dichiarato della modalità Access Point;
- presenza di Docker;
- presenza di KVM/QEMU, libvirt e virt-manager;
- rete virtuale libvirt `default`;
- rete virtuale isolata `lab-lan`;
- VM Kali configurata con una WAN e una LAN;
- accesso Internet verificato dalla VM Kali.

Queste informazioni devono essere ricontrollate quando verranno usate per una configurazione reale, perché nomi delle interfacce, kernel, driver e profili possono cambiare.

## Esperimento non completato

Era stato iniziato ma interrotto un tentativo di creazione dell'hotspot tramite NetworkManager. Non risultava un profilo persistente completo.

Pertanto l'hotspot fisico è considerato:

```text
DA FARE
```

## Stato delle fasi

| Fase | Stato | Nota |
|---:|---|---|
| 1. Inventario hardware e rete | IN CORSO | Esistono dati precedenti, serve una nuova raccolta completa e aggiornata |
| 2. Topologia e indirizzamento | DA FARE | La subnet definitiva non è stata approvata e testata |
| 3. Hotspot Realtek | DA FARE | Nessun hotspot stabile verificato |
| 4. DHCP, routing e NAT | DA FARE | Nessun client fisico ha navigato attraverso Ubuntu |
| 5. Firewall nftables | DA FARE | Nessun ruleset fisico verificato |
| 6. tcpdump | DA FARE | Nessuna cattura della nuova topologia documentata |
| 7. Suricata | DA FARE | Non installato/configurato per questa topologia |
| 8. Zeek | DA FARE | Non installato/configurato per questa topologia |
| 9. Python | DA FARE | Nessun analizzatore dei log ancora sviluppato |
| 10. Docker dashboard | DA FARE | Nessuno stack definitivo |
| 11. Test e hardening | DA FARE | Dipende dalle fasi precedenti |

## Primo prossimo passo

Eseguire esclusivamente comandi di osservazione sull'host Ubuntu:

```bash
cat /etc/os-release
uname -a
ip -br link
ip -4 -br address
ip route
ip route get 1.1.1.1
nmcli device status
nmcli connection show
lsusb
lspci -nnk | grep -A 4 -Ei 'network|wireless'
iw dev
rfkill list
```

Poi associare con certezza:

```text
UPLINK_IF=<interfaccia MediaTek con Internet>
AP_IF=<interfaccia Realtek USB>
```

## Condizione per passare alla fase 2

La fase 1 potrà essere chiusa soltanto quando avremo documentato:

- versione di Ubuntu;
- versione del kernel;
- nome reale delle due interfacce;
- modello e driver;
- route predefinita;
- supporto AP della Realtek;
- stato NetworkManager;
- assenza di conflitti evidenti;
- output anonimizzati sufficienti a ripetere il controllo.