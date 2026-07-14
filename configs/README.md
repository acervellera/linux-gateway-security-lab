# Configurazioni

Questa cartella conterrà soltanto configurazioni applicate e verificate nel laboratorio.

Struttura prevista:

```text
configs/
|-- networkmanager/
|-- nftables/
|-- suricata/
`-- zeek/
```

Ogni configurazione deve indicare:

- sistema e versione usati;
- interfacce rappresentate tramite segnaposto quando necessario;
- comando di controllo sintattico;
- procedura di applicazione;
- test eseguiti;
- rollback;
- eventuali dati da sostituire localmente.

Non inserire password, SSID privati, token, chiavi o log reali.