# Docker

Questa cartella conterrà lo stack applicativo aggiunto nella fase 10.

Docker sarà usato per database, importazione dati, API e dashboard. Il routing, il firewall e l'hotspot resteranno inizialmente sul sistema Ubuntu host.

Regole principali:

- nessun container privilegiato senza motivazione verificata;
- nessun montaggio del socket Docker;
- log montati in sola lettura;
- segreti in file locali esclusi da Git;
- volumi e backup documentati;
- porte pubblicate ridotte al minimo;
- `compose.yaml` controllato con `docker compose config`.