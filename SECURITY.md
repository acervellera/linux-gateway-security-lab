# Security Policy

## Uso autorizzato

Questo progetto è destinato esclusivamente a:

- reti proprie;
- macchine virtuali di laboratorio;
- dispositivi propri;
- ambienti per i quali si dispone di autorizzazione esplicita.

Non utilizzare configurazioni, catture o strumenti del progetto per osservare, modificare o interrompere traffico di terzi senza autorizzazione.

## Dati sensibili

Non inserire nel repository:

- password Wi-Fi;
- SSID domestici reali quando non necessari;
- token API;
- chiavi SSH private;
- certificati e chiavi private;
- file `.env`;
- cookie o sessioni;
- backup di configurazioni contenenti segreti;
- log non revisionati;
- indirizzi MAC reali quando non indispensabili;
- dati personali di utenti o dispositivi.

Usare segnaposto come:

```text
<USB_WIFI_IFACE>
<LAB_SSID>
<CLIENT_IP>
<WAN_IFACE>
<LAN_IFACE>
```

## Segreti pubblicati accidentalmente

Rimuovere un segreto dall'ultima versione di un file non lo elimina dalla cronologia Git.

In caso di pubblicazione accidentale:

1. revocare o cambiare immediatamente la credenziale;
2. interrompere l'uso della credenziale compromessa;
3. verificare commit, branch, tag, issue e workflow;
4. riscrivere la cronologia solo dopo aver compreso le conseguenze;
5. informare eventuali collaboratori che gli hash dei commit potrebbero cambiare.

## Modifiche di rete rischiose

Prima di modificare routing, forwarding o firewall:

- creare uno snapshot della VM;
- mantenere aperta una console locale;
- salvare `ip address`, `ip route` e `nft list ruleset`;
- verificare l'hostname;
- non eseguire `nft flush ruleset` sull'host;
- introdurre una modifica alla volta;
- preparare un rollback mirato.

## Container

Evitare salvo necessità documentata:

```yaml
privileged: true
network_mode: host
```

Evitare inoltre di montare:

```text
/var/run/docker.sock
```

Applicare il principio del minimo privilegio e montare log o configurazioni in sola lettura quando possibile.

## Segnalazione di problemi

Per vulnerabilità o dati sensibili non aprire una issue pubblica contenente dettagli sfruttabili o credenziali. Utilizzare i canali privati messi a disposizione dal proprietario del repository, quando configurati.

## Ambito del supporto

Il progetto è didattico. Le configurazioni devono essere verificate nel proprio ambiente. Driver, nomi delle interfacce, versioni del kernel e comportamento di NetworkManager possono variare.