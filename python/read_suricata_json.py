#!/usr/bin/env python3

"""Analizza Suricata ``eve.json`` in formato JSON Lines.

Supporta file normali, gzip e standard input. Gli indirizzi IP vengono usati
soltanto per contare i valori unici e non vengono stampati o esportati.
"""

import argparse
from collections import Counter
from contextlib import nullcontext
from dataclasses import dataclass, field
from datetime import datetime
import gzip
import json
from pathlib import Path
import sys
from typing import ContextManager, TextIO


@dataclass
class SuricataResult:
    """Statistiche aggregate di un log EVE Suricata."""

    valid_events: int = 0
    malformed_lines: int = 0
    empty_lines: int = 0
    invalid_timestamps: int = 0
    event_type_counts: Counter[str] = field(default_factory=Counter)
    protocol_counts: Counter[str] = field(default_factory=Counter)
    app_protocol_counts: Counter[str] = field(default_factory=Counter)
    destination_port_counts: Counter[int] = field(default_factory=Counter)
    events_per_hour: Counter[str] = field(default_factory=Counter)
    alert_signature_counts: Counter[str] = field(default_factory=Counter)
    alert_category_counts: Counter[str] = field(default_factory=Counter)
    alert_severity_counts: Counter[int] = field(default_factory=Counter)
    alert_action_counts: Counter[str] = field(default_factory=Counter)
    flow_state_counts: Counter[str] = field(default_factory=Counter)
    flow_reason_counts: Counter[str] = field(default_factory=Counter)
    anomaly_type_counts: Counter[str] = field(default_factory=Counter)
    total_bytes_toserver: int = 0
    total_bytes_toclient: int = 0
    flow_events: int = 0
    source_ips: set[str] = field(default_factory=set)
    destination_ips: set[str] = field(default_factory=set)

    @property
    def total_flow_bytes(self) -> int:
        """Traffico totale ricavato dagli eventi ``flow``."""

        return self.total_bytes_toserver + self.total_bytes_toclient


def parse_arguments() -> argparse.Namespace:
    """Legge gli argomenti della riga di comando."""

    parser = argparse.ArgumentParser(
        description=(
            "Analizza Suricata eve.json senza mostrare indirizzi IP e "
            "produce un report testuale e, facoltativamente, JSON."
        )
    )
    parser.add_argument(
        "log_path",
        type=Path,
        help="Percorso di eve.json, eve.json.gz oppure - per stdin.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Percorso facoltativo del report JSON.",
    )
    return parser.parse_args()


def open_text_log(log_path: Path) -> ContextManager[TextIO]:
    """Apre un file normale, gzip oppure la standard input."""

    if str(log_path) == "-":
        return nullcontext(sys.stdin)
    if log_path.suffix.lower() == ".gz":
        return gzip.open(log_path, mode="rt", encoding="utf-8")
    return log_path.open(mode="r", encoding="utf-8")


def add_string_value(counter: Counter[str], value: object) -> None:
    """Conta una stringa non vuota."""

    if not isinstance(value, str):
        return
    clean_value = value.strip()
    if clean_value:
        counter[clean_value] += 1


def get_non_negative_int(value: object) -> int | None:
    """Restituisce un intero non negativo, escludendo i booleani."""

    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    return None


def get_mapping(value: object) -> dict[str, object] | None:
    """Restituisce ``value`` quando è un oggetto JSON/dizionario."""

    return value if isinstance(value, dict) else None


def parse_hour(timestamp: object) -> str | None:
    """Raggruppa un timestamp ISO 8601 all'inizio della relativa ora."""

    if not isinstance(timestamp, str) or not timestamp:
        return None
    normalized = timestamp[:-1] + "+00:00" if timestamp.endswith("Z") else timestamp
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    return parsed.strftime("%Y-%m-%d %H:00")


def analyze_alert(event: dict[str, object], result: SuricataResult) -> None:
    """Estrae firma, categoria, severità e azione da un alert."""

    alert = get_mapping(event.get("alert"))
    if alert is None:
        return
    add_string_value(result.alert_signature_counts, alert.get("signature"))
    add_string_value(result.alert_category_counts, alert.get("category"))
    add_string_value(result.alert_action_counts, alert.get("action"))
    severity = get_non_negative_int(alert.get("severity"))
    if severity is not None:
        result.alert_severity_counts[severity] += 1


def analyze_flow(event: dict[str, object], result: SuricataResult) -> None:
    """Estrae stato, motivo e byte dall'oggetto ``flow``."""

    flow = get_mapping(event.get("flow"))
    if flow is None:
        return
    result.flow_events += 1
    add_string_value(result.flow_state_counts, flow.get("state"))
    add_string_value(result.flow_reason_counts, flow.get("reason"))

    bytes_toserver = get_non_negative_int(flow.get("bytes_toserver"))
    if bytes_toserver is not None:
        result.total_bytes_toserver += bytes_toserver
    bytes_toclient = get_non_negative_int(flow.get("bytes_toclient"))
    if bytes_toclient is not None:
        result.total_bytes_toclient += bytes_toclient


def analyze_anomaly(event: dict[str, object], result: SuricataResult) -> None:
    """Estrae il tipo di anomalia applicativa o di protocollo."""

    anomaly = get_mapping(event.get("anomaly"))
    if anomaly is None:
        return
    anomaly_type = anomaly.get("type")
    if not isinstance(anomaly_type, str) or not anomaly_type.strip():
        anomaly_type = anomaly.get("event")
    add_string_value(result.anomaly_type_counts, anomaly_type)


def analyze_event(event: dict[str, object], result: SuricataResult) -> None:
    """Aggiorna tutte le statistiche usando un singolo evento EVE."""

    event_type = event.get("event_type")
    if not isinstance(event_type, str) or not event_type.strip():
        event_type = "<mancante>"
    event_type = event_type.strip()
    result.event_type_counts[event_type] += 1

    add_string_value(result.protocol_counts, event.get("proto"))
    add_string_value(result.app_protocol_counts, event.get("app_proto"))

    destination_port = get_non_negative_int(event.get("dest_port"))
    if destination_port is not None:
        result.destination_port_counts[destination_port] += 1

    source_ip = event.get("src_ip")
    if isinstance(source_ip, str) and source_ip:
        result.source_ips.add(source_ip)
    destination_ip = event.get("dest_ip")
    if isinstance(destination_ip, str) and destination_ip:
        result.destination_ips.add(destination_ip)

    hour = parse_hour(event.get("timestamp"))
    if hour is None:
        result.invalid_timestamps += 1
    else:
        result.events_per_hour[hour] += 1

    if event_type == "alert":
        analyze_alert(event, result)
    elif event_type == "flow":
        analyze_flow(event, result)
    elif event_type == "anomaly":
        analyze_anomaly(event, result)


def analyze_log(log_path: Path) -> SuricataResult:
    """Legge il log EVE una riga alla volta."""

    result = SuricataResult()
    with open_text_log(log_path) as log_file:
        for line_number, line in enumerate(log_file, start=1):
            clean_line = line.strip()
            if not clean_line:
                result.empty_lines += 1
                continue
            try:
                event = json.loads(clean_line)
            except json.JSONDecodeError as error:
                result.malformed_lines += 1
                print(
                    f"Riga {line_number} ignorata: {error.msg}",
                    file=sys.stderr,
                )
                continue
            if not isinstance(event, dict):
                result.malformed_lines += 1
                print(
                    f"Riga {line_number} ignorata: il JSON non è un oggetto.",
                    file=sys.stderr,
                )
                continue
            result.valid_events += 1
            analyze_event(event, result)
    return result


def format_bytes(byte_count: int) -> str:
    """Mostra i byte esatti e una forma leggibile."""

    units = ("B", "KiB", "MiB", "GiB", "TiB")
    value = float(byte_count)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{byte_count} B"
            return f"{byte_count} B ({value:.2f} {unit})"
        value /= 1024
    return f"{byte_count} B"


def counter_to_string_dict(counter: Counter[object]) -> dict[str, int]:
    """Converte le chiavi di un ``Counter`` in stringhe JSON."""

    return {str(value): count for value, count in counter.most_common()}


def result_to_dict(log_path: Path, result: SuricataResult) -> dict[str, object]:
    """Crea il report JSON senza includere indirizzi IP grezzi."""

    return {
        "source": str(log_path),
        "privacy": {"raw_ip_addresses_included": False},
        "summary": {
            "valid_events": result.valid_events,
            "malformed_lines": result.malformed_lines,
            "empty_lines": result.empty_lines,
            "invalid_timestamps": result.invalid_timestamps,
            "unique_source_ips": len(result.source_ips),
            "unique_destination_ips": len(result.destination_ips),
        },
        "event_types": counter_to_string_dict(result.event_type_counts),
        "network_protocols": counter_to_string_dict(result.protocol_counts),
        "application_protocols": counter_to_string_dict(result.app_protocol_counts),
        "destination_ports": counter_to_string_dict(result.destination_port_counts),
        "events_per_hour": counter_to_string_dict(result.events_per_hour),
        "alerts": {
            "total": result.event_type_counts.get("alert", 0),
            "signatures": counter_to_string_dict(result.alert_signature_counts),
            "categories": counter_to_string_dict(result.alert_category_counts),
            "severities": counter_to_string_dict(result.alert_severity_counts),
            "actions": counter_to_string_dict(result.alert_action_counts),
        },
        "flows": {
            "events": result.flow_events,
            "bytes_toserver": result.total_bytes_toserver,
            "bytes_toclient": result.total_bytes_toclient,
            "total_bytes": result.total_flow_bytes,
            "states": counter_to_string_dict(result.flow_state_counts),
            "reasons": counter_to_string_dict(result.flow_reason_counts),
        },
        "anomalies": counter_to_string_dict(result.anomaly_type_counts),
    }


def write_json_report(
    output_path: Path,
    log_path: Path,
    result: SuricataResult,
) -> None:
    """Salva il report JSON creando le directory mancanti."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open(mode="w", encoding="utf-8") as output_file:
        json.dump(
            result_to_dict(log_path, result),
            output_file,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        output_file.write("\n")


def print_counter(
    title: str,
    counter: Counter[object],
    limit: int | None = None,
) -> None:
    """Stampa un ``Counter`` ordinato per frequenza."""

    print(f"\n{title}:")
    if not counter:
        print("- nessun valore disponibile")
        return
    for value, count in counter.most_common(limit):
        print(f"- {value}: {count}")


def print_report(log_path: Path, result: SuricataResult) -> None:
    """Stampa un report testuale privo di indirizzi IP reali."""

    print(f"File analizzato: {log_path}")
    print(f"Eventi JSON validi: {result.valid_events}")
    print(f"Righe malformate: {result.malformed_lines}")
    print(f"Righe vuote: {result.empty_lines}")
    print(f"Timestamp non validi: {result.invalid_timestamps}")
    print(f"IP sorgente unici: {len(result.source_ips)}")
    print(f"IP destinazione unici: {len(result.destination_ips)}")
    print("Byte verso i server (eventi flow): " f"{format_bytes(result.total_bytes_toserver)}")
    print("Byte verso i client (eventi flow): " f"{format_bytes(result.total_bytes_toclient)}")
    print_counter("Tipi di evento", result.event_type_counts)
    print_counter("Protocolli di rete", result.protocol_counts)
    print_counter("Protocolli applicativi", result.app_protocol_counts)
    print_counter("Porte di destinazione più frequenti", result.destination_port_counts, limit=10)
    print_counter("Eventi per ora", result.events_per_hour)
    print_counter("Firme degli alert", result.alert_signature_counts)
    print_counter("Categorie degli alert", result.alert_category_counts)
    print_counter("Severità degli alert", result.alert_severity_counts)
    print_counter("Azioni degli alert", result.alert_action_counts)
    print_counter("Stati dei flow", result.flow_state_counts)
    print_counter("Motivi di chiusura dei flow", result.flow_reason_counts)
    print_counter("Tipi di anomalia", result.anomaly_type_counts)


def main() -> int:
    """Coordina analisi, stampa ed esportazione JSON."""

    arguments = parse_arguments()
    try:
        result = analyze_log(arguments.log_path)
    except FileNotFoundError:
        print(f"Errore: file non trovato: {arguments.log_path}", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"Errore: permesso negato: {arguments.log_path}", file=sys.stderr)
        return 1
    except IsADirectoryError:
        print(f"Errore: il percorso è una directory: {arguments.log_path}", file=sys.stderr)
        return 1
    except gzip.BadGzipFile:
        print(f"Errore: file gzip non valido: {arguments.log_path}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(f"Errore: testo UTF-8 non valido: {arguments.log_path}", file=sys.stderr)
        return 1

    print_report(arguments.log_path, result)
    if arguments.json_output is not None:
        try:
            write_json_report(arguments.json_output, arguments.log_path, result)
        except OSError as error:
            print(f"Errore durante la scrittura del report JSON: {error}", file=sys.stderr)
            return 1
        print(f"\nReport JSON salvato: {arguments.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
