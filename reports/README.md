# Report locali

Questa cartella è riservata ai report originali e privati generati durante il laboratorio.

Il file `.gitignore` esclude tutto il contenuto di `reports/`, tranne questo README, perché i report possono contenere:

- indirizzi IPv4 locali e remoti completi;
- porte temporanee;
- indirizzi MAC;
- nomi completi di interfacce `wlx...`;
- hostname e percorsi personali;
- SSID reali;
- domini e query DNS;
- output grezzi degli strumenti;
- log del kernel e AppArmor.

## Regola di separazione

Per ogni fase che produce dati locali conservare due versioni:

```text
reports/<numero>-<nome>-private.md
samples/<numero>-<nome>-report.md
```

La prima è il report privato completo e resta esclusa da Git. La seconda è la copia pubblica anonimizzata e revisionata.

Esempio della fase 6:

```text
reports/06-cattura-tcpdump-private.md
samples/06-cattura-tcpdump-report.md
```

Il PCAP della fase 6 non deve essere conservato nel repository, neppure in `reports/`. Resta nella directory privata esterna:

```text
$HOME/.local/state/linux-security-lab/phase-06/
```

## Immagini private

Le immagini originali devono essere conservate separatamente:

```text
reports/
|-- images/
|   |-- <numero>-<descrizione>-original.png
|   `-- ...
|-- <report-privato>.md
`-- README.md
```

Da un report Markdown in `reports/`:

```markdown
![Descrizione](images/nome-immagine-original.png)
```

## Protezione dei file

Applicare permessi privati:

```bash
chmod 600 reports/<report-privato>.md
```

Verificare che Git ignori il file:

```bash
git check-ignore -v reports/<report-privato>.md
```

Controllare lo stato:

```bash
git status --short
```

Non usare mai:

```bash
git add -f reports/<report-privato>.md
```

## Prima di creare il sample pubblico

1. creare una copia del report privato;
2. rimuovere SSID domestici e nomi personali;
3. sostituire MAC con `<REDACTED>`;
4. sostituire i nomi completi `wlx...` con `wlx<REDACTED>`;
5. mascherare IP locali e remoti non necessari;
6. rimuovere porte temporanee reali;
7. rimuovere query DNS personali;
8. eliminare password, token, chiavi e segreti;
9. ridurre gli output alle sole righe necessarie;
10. controllare manualmente la copia;
11. pubblicare soltanto in `samples/`;
12. non pubblicare PCAP grezzi.

## Fase 6

Report pubblico revisionato:

```text
samples/06-cattura-tcpdump-report.md
```

Report privato locale:

```text
reports/06-cattura-tcpdump-private.md
```

Il report privato conserva interfacce, IP, porte, domini, percorsi e log AppArmor completi e non deve essere inserito nel repository GitHub.