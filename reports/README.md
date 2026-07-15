# Report locali

Questa cartella è riservata ai report originali generati durante il laboratorio.

Il file `.gitignore` esclude il contenuto della cartella perché i report possono contenere:

- indirizzi IPv4 locali completi;
- indirizzi MAC;
- nomi di interfaccia `wlx...` derivati dal MAC;
- SSID reali osservati durante le scansioni;
- domini, host e altri dati della rete locale;
- output grezzi di strumenti di rete.

## Regola di separazione

Per ogni fase che produce dati locali conservare due versioni distinte:

```text
reports/<data>-fase-<numero>-privato.md
samples/<numero>-<nome>-report.md
```

La prima è il report privato completo e rimane esclusa da Git. La seconda è una copia pubblica anonimizzata e revisionata.

Esempio per la fase 2:

```text
reports/2026-07-15-fase-02-topologia-privato.md
samples/02-topologia-e-indirizzamento-report.md
```

## Prima di condividere un report

1. creare una copia del file originale;
2. rimuovere SSID domestici e nomi personali;
3. sostituire gli indirizzi MAC con `<REDACTED>`;
4. sostituire i nomi `wlx...` completi con `wlx<REDACTED>`;
5. mascherare l'indirizzo host, per esempio `192.168.10.x`;
6. eliminare password, token, chiavi e altri segreti;
7. ridurre gli output alle sole righe necessarie;
8. controllare manualmente la copia;
9. pubblicare la copia revisionata soltanto in `samples/`;
10. non forzare mai con `git add -f` un report originale escluso da `.gitignore`.

## Fase 2

Il report pubblico revisionato della fase 2 si trova in:

```text
samples/02-topologia-e-indirizzamento-report.md
```

Il report privato conserva localmente i valori completi, ma non deve essere inserito nel repository GitHub.
