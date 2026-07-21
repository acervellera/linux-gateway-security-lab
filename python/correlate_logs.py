#!/usr/bin/env python3

"""Correla connessioni Zeek ed eventi Suricata.

La correlazione usa protocollo, coppie IP/porta e una finestra temporale.
Gli endpoint vengono ordinati in modo canonico, quindi il confronto funziona
anche quando i due sensori rappresentano il traffico in direzioni opposte.
Il report non esporta indirizzi IP o UID Zeek.
"""

import argparse
from collections import Counter
from contextlib import nullcontext
from dataclasses import dataclass, field
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import sys
from typing import ContextManager, TextIO

Endpoint = tuple[str, int]
FlowKey = tuple[str, Endpoint, Endpoint]


@dataclass(frozen=True)
class ZeekConnection:
    """Dati minimi di una connessione Zeek necessari alla correlazione."""

    identifier: str
    timestamp: float
    flow_key: FlowKey


@dataclass
class ZeekIndex:
    """Indice delle connessioni Zeek raggruppate per 5-tupla."""

    connections_by_key: dict[FlowKey, list[ZeekConnection]] = field(default_factory=dict)
    loaded_connections: int = 0
    malformed_lines: int = 0
    skipped_events: int = 0
    minimum_timestamp: float | None = None
    maximum_timestamp: float | None = None


@dataclass
class CorrelationResult:
    """Statistiche aggregate della correlazione."""

    zeek_connections_loaded: int = 0
    zeek_malformed_lines: int = 0
    zeek_skipped_events: int = 0
    suricata_valid_events: int = 0
    suricata_malformed_lines: int = 0
    suricata_empty_lines: int = 0
    suricata_invalid_timestamps: int = 0
    suricata_events_in_time_window: int = 0
    suricata_events_with_flow_key: int = 0
    matched_suricata_events: int = 0
    matched_zeek_identifiers: set[str] = field(default_factory=set)
    matched_event_type_counts: Counter[str] = field(default_factory=Counter)
    matched_protocol_counts: Counter[str] = field(default_factory=Counter)
    matched_alert_signature_counts: Counter[str] = field(default_factory=Counter)
    time_deltas: list[float] = field(default_factory=list)

    @property
    def unmatched_suricata_events(self) -> int:
        return self.suricata_events_with_flow_key - self.matched_suricata_events

    @property
    def match_percentage(self) -> float:
        if self.suricata_events_with_flow_key == 0:
            return 0.0
        return self.matched_suricata_events / self.suricata_events_with_flow_key * 100

    @property
    def zeek_connection_match_percentage(self) -> float:
        if self.zeek_connections_loaded == 0:
            return 0.0
        return len(self.matched_zeek_identifiers) / self.zeek_connections_loaded * 100

    @property
    def average_time_delta(self) -> float:
        if not self.time_deltas:
            return 0.0
        return sum(self.time_deltas) / len(self.time_deltas)

    @property
    def maximum_time_delta(self) -> float:
        if not self.time_deltas:
            return 0.0
        return max(self.time_deltas)


def non_negative_float(value: str) -> float:
    """Converte un argomento in float e rifiuta valori negativi."""

    try:
        converted = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("deve essere un numero") from error
    if converted < 0:
        raise argparse.ArgumentTypeError("non può essere negativo")
    return converted


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Correla connessioni Zeek ed eventi Suricata usando 5-tupla e timestamp."
    )
    parser.add_argument("zeek_log", type=Path, help="Percorso del conn.log JSON o JSON.gz di Zeek.")
    parser.add_argument("suricata_log", type=Path, help="Percorso di eve.json, eve.json.gz oppure - per stdin.")
    parser.add_argument(
        "--window-seconds",
        type=non_negative_float,
        default=5.0,
        help="Differenza temporale massima. Predefinita: 5 secondi.",
    )
    parser.add_argument("--json-output", type=Path, help="Percorso facoltativo del report JSON.")
    return parser.parse_args()


def open_text_log(log_path: Path, allow_stdin: bool = False) -> ContextManager[TextIO]:
    """Apre un file JSONL normale, gzip oppure stdin."""

    if allow_stdin and str(log_path) == "-":
        return nullcontext(sys.stdin)
    if log_path.suffix.lower() == ".gz":
        return gzip.open(log_path, mode="rt", encoding="utf-8")
    return log_path.open(mode="r", encoding="utf-8")


def normalize_protocol(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    return normalized or None


def get_valid_port(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and 0 <= value <= 65535:
        return value
    return None


def canonical_flow_key(
    protocol: object,
    source_ip: object,
    source_port: object,
    destination_ip: object,
    destination_port: object,
) -> FlowKey | None:
    """Crea una chiave indipendente dalla direzione del traffico."""

    normalized_protocol = normalize_protocol(protocol)
    if normalized_protocol is None:
        return None
    if not isinstance(source_ip, str) or not source_ip:
        return None
    if not isinstance(destination_ip, str) or not destination_ip:
        return None
    normalized_source_port = get_valid_port(source_port)
    normalized_destination_port = get_valid_port(destination_port)
    if normalized_source_port is None or normalized_destination_port is None:
        return None

    source_endpoint: Endpoint = (source_ip, normalized_source_port)
    destination_endpoint: Endpoint = (destination_ip, normalized_destination_port)
    first_endpoint, second_endpoint = sorted((source_endpoint, destination_endpoint))
    return normalized_protocol, first_endpoint, second_endpoint


def get_epoch_timestamp(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def parse_iso_timestamp(value: object) -> float | None:
    """Converte un timestamp ISO 8601 Suricata in secondi Unix."""

    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.timestamp()


def extract_suricata_timestamps(event: dict[str, object]) -> list[float]:
    """Estrae il timestamp principale e gli eventuali flow.start/end."""

    timestamps: list[float] = []
    main_timestamp = parse_iso_timestamp(event.get("timestamp"))
    if main_timestamp is not None:
        timestamps.append(main_timestamp)
    flow = event.get("flow")
    if isinstance(flow, dict):
        for field_name in ("start", "end"):
            flow_timestamp = parse_iso_timestamp(flow.get(field_name))
            if flow_timestamp is not None and flow_timestamp not in timestamps:
                timestamps.append(flow_timestamp)
    return timestamps


def load_zeek_index(log_path: Path) -> ZeekIndex:
    """Carica il piccolo log Zeek in memoria e costruisce un indice."""

    index = ZeekIndex()
    with open_text_log(log_path) as log_file:
        for line_number, line in enumerate(log_file, start=1):
            clean_line = line.strip()
            if not clean_line:
                continue
            try:
                event = json.loads(clean_line)
            except json.JSONDecodeError as error:
                index.malformed_lines += 1
                print(f"Zeek, riga {line_number} ignorata: {error.msg}", file=sys.stderr)
                continue
            if not isinstance(event, dict):
                index.malformed_lines += 1
                continue

            timestamp = get_epoch_timestamp(event.get("ts"))
            flow_key = canonical_flow_key(
                event.get("proto"),
                event.get("id.orig_h"),
                event.get("id.orig_p"),
                event.get("id.resp_h"),
                event.get("id.resp_p"),
            )
            if timestamp is None or flow_key is None:
                index.skipped_events += 1
                continue

            uid = event.get("uid")
            if not isinstance(uid, str) or not uid:
                uid = f"line-{line_number}"
            connection = ZeekConnection(uid, timestamp, flow_key)
            index.connections_by_key.setdefault(flow_key, []).append(connection)
            index.loaded_connections += 1

            if index.minimum_timestamp is None or timestamp < index.minimum_timestamp:
                index.minimum_timestamp = timestamp
            if index.maximum_timestamp is None or timestamp > index.maximum_timestamp:
                index.maximum_timestamp = timestamp

    for connections in index.connections_by_key.values():
        connections.sort(key=lambda connection: connection.timestamp)
    return index


def event_is_in_time_window(
    timestamps: list[float],
    minimum_timestamp: float,
    maximum_timestamp: float,
    window_seconds: float,
) -> bool:
    lower_bound = minimum_timestamp - window_seconds
    upper_bound = maximum_timestamp + window_seconds
    return any(lower_bound <= timestamp <= upper_bound for timestamp in timestamps)


def find_closest_connection(
    candidates: list[ZeekConnection],
    timestamps: list[float],
    window_seconds: float,
) -> tuple[ZeekConnection, float] | None:
    best_connection: ZeekConnection | None = None
    best_delta: float | None = None
    for connection in candidates:
        for timestamp in timestamps:
            delta = abs(timestamp - connection.timestamp)
            if best_delta is None or delta < best_delta:
                best_connection = connection
                best_delta = delta
    if best_connection is None or best_delta is None or best_delta > window_seconds:
        return None
    return best_connection, best_delta


def add_matched_alert(event: dict[str, object], result: CorrelationResult) -> None:
    alert = event.get("alert")
    if not isinstance(alert, dict):
        return
    signature = alert.get("signature")
    if isinstance(signature, str) and signature.strip():
        result.matched_alert_signature_counts[signature.strip()] += 1


def correlate_logs(
    zeek_log: Path,
    suricata_log: Path,
    window_seconds: float,
) -> tuple[ZeekIndex, CorrelationResult]:
    """Indicizza Zeek e legge Suricata in streaming."""

    zeek_index = load_zeek_index(zeek_log)
    if zeek_index.minimum_timestamp is None or zeek_index.maximum_timestamp is None:
        raise ValueError("il log Zeek non contiene connessioni correlabili")

    result = CorrelationResult(
        zeek_connections_loaded=zeek_index.loaded_connections,
        zeek_malformed_lines=zeek_index.malformed_lines,
        zeek_skipped_events=zeek_index.skipped_events,
    )
    with open_text_log(suricata_log, allow_stdin=True) as log_file:
        for line_number, line in enumerate(log_file, start=1):
            clean_line = line.strip()
            if not clean_line:
                result.suricata_empty_lines += 1
                continue
            try:
                event = json.loads(clean_line)
            except json.JSONDecodeError as error:
                result.suricata_malformed_lines += 1
                print(f"Suricata, riga {line_number} ignorata: {error.msg}", file=sys.stderr)
                continue
            if not isinstance(event, dict):
                result.suricata_malformed_lines += 1
                continue

            result.suricata_valid_events += 1
            timestamps = extract_suricata_timestamps(event)
            if not timestamps:
                result.suricata_invalid_timestamps += 1
                continue
            if not event_is_in_time_window(
                timestamps,
                zeek_index.minimum_timestamp,
                zeek_index.maximum_timestamp,
                window_seconds,
            ):
                continue

            result.suricata_events_in_time_window += 1
            flow_key = canonical_flow_key(
                event.get("proto"),
                event.get("src_ip"),
                event.get("src_port"),
                event.get("dest_ip"),
                event.get("dest_port"),
            )
            if flow_key is None:
                continue
            result.suricata_events_with_flow_key += 1
            candidates = zeek_index.connections_by_key.get(flow_key)
            if not candidates:
                continue
            match = find_closest_connection(candidates, timestamps, window_seconds)
            if match is None:
                continue

            connection, delta = match
            result.matched_suricata_events += 1
            result.matched_zeek_identifiers.add(connection.identifier)
            result.time_deltas.append(delta)

            event_type = event.get("event_type")
            if not isinstance(event_type, str):
                event_type = "<mancante>"
            result.matched_event_type_counts[event_type] += 1
            protocol = normalize_protocol(event.get("proto"))
            if protocol is not None:
                result.matched_protocol_counts[protocol] += 1
            if event_type == "alert":
                add_matched_alert(event, result)
    return zeek_index, result


def counter_to_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(counter.most_common())


def epoch_to_utc(timestamp: float | None) -> str | None:
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def result_to_dict(
    zeek_log: Path,
    suricata_log: Path,
    zeek_index: ZeekIndex,
    result: CorrelationResult,
    window_seconds: float,
) -> dict[str, object]:
    """Crea il report JSON senza IP e UID."""

    return {
        "sources": {"zeek": str(zeek_log), "suricata": str(suricata_log)},
        "privacy": {"raw_ip_addresses_included": False, "zeek_uids_included": False},
        "configuration": {"window_seconds": window_seconds},
        "zeek_time_range": {
            "start_utc": epoch_to_utc(zeek_index.minimum_timestamp),
            "end_utc": epoch_to_utc(zeek_index.maximum_timestamp),
        },
        "zeek": {
            "connections_loaded": result.zeek_connections_loaded,
            "malformed_lines": result.zeek_malformed_lines,
            "skipped_events": result.zeek_skipped_events,
            "matched_unique_connections": len(result.matched_zeek_identifiers),
            "match_percentage": result.zeek_connection_match_percentage,
        },
        "suricata": {
            "valid_events": result.suricata_valid_events,
            "malformed_lines": result.suricata_malformed_lines,
            "empty_lines": result.suricata_empty_lines,
            "invalid_timestamps": result.suricata_invalid_timestamps,
            "events_in_zeek_time_window": result.suricata_events_in_time_window,
            "events_with_flow_key": result.suricata_events_with_flow_key,
            "matched_events": result.matched_suricata_events,
            "unmatched_events": result.unmatched_suricata_events,
            "match_percentage": result.match_percentage,
        },
        "matched": {
            "event_types": counter_to_dict(result.matched_event_type_counts),
            "protocols": counter_to_dict(result.matched_protocol_counts),
            "alert_signatures": counter_to_dict(result.matched_alert_signature_counts),
        },
        "timing": {
            "average_delta_seconds": result.average_time_delta,
            "maximum_delta_seconds": result.maximum_time_delta,
        },
    }


def write_json_report(
    output_path: Path,
    zeek_log: Path,
    suricata_log: Path,
    zeek_index: ZeekIndex,
    result: CorrelationResult,
    window_seconds: float,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = result_to_dict(zeek_log, suricata_log, zeek_index, result, window_seconds)
    with output_path.open(mode="w", encoding="utf-8") as output_file:
        json.dump(report, output_file, indent=2, ensure_ascii=False, sort_keys=True)
        output_file.write("\n")


def print_counter(title: str, counter: Counter[str]) -> None:
    print(f"\n{title}:")
    if not counter:
        print("- nessun valore")
        return
    for value, count in counter.most_common():
        print(f"- {value}: {count}")


def print_report(
    zeek_index: ZeekIndex,
    result: CorrelationResult,
    window_seconds: float,
) -> None:
    print(f"Finestra di correlazione: {window_seconds:.3f} secondi")
    print(
        "Intervallo Zeek UTC: "
        f"{epoch_to_utc(zeek_index.minimum_timestamp)} → "
        f"{epoch_to_utc(zeek_index.maximum_timestamp)}"
    )
    print(f"Connessioni Zeek caricate: {result.zeek_connections_loaded}")
    print(f"Righe Zeek malformate: {result.zeek_malformed_lines}")
    print(f"Eventi Suricata validi: {result.suricata_valid_events}")
    print(f"Eventi Suricata nella finestra Zeek: {result.suricata_events_in_time_window}")
    print(f"Eventi Suricata con 5-tupla valida: {result.suricata_events_with_flow_key}")
    print(f"Eventi Suricata correlati: {result.matched_suricata_events}")
    print(f"Eventi correlabili non abbinati: {result.unmatched_suricata_events}")
    print(f"Connessioni Zeek distinte abbinate: {len(result.matched_zeek_identifiers)}")
    print(f"Copertura delle connessioni Zeek: {result.zeek_connection_match_percentage:.2f}%")
    print(f"Copertura degli eventi correlabili: {result.match_percentage:.2f}%")
    print(f"Differenza temporale media: {result.average_time_delta:.3f} secondi")
    print(f"Differenza temporale massima: {result.maximum_time_delta:.3f} secondi")
    print_counter("Tipi di evento Suricata correlati", result.matched_event_type_counts)
    print_counter("Protocolli correlati", result.matched_protocol_counts)
    print_counter("Alert Suricata correlati", result.matched_alert_signature_counts)


def main() -> int:
    arguments = parse_arguments()
    try:
        zeek_index, result = correlate_logs(
            arguments.zeek_log,
            arguments.suricata_log,
            arguments.window_seconds,
        )
    except (
        FileNotFoundError,
        PermissionError,
        IsADirectoryError,
        gzip.BadGzipFile,
        UnicodeDecodeError,
        ValueError,
    ) as error:
        print(f"Errore: {error}", file=sys.stderr)
        return 1

    print_report(zeek_index, result, arguments.window_seconds)
    if arguments.json_output is not None:
        try:
            write_json_report(
                arguments.json_output,
                arguments.zeek_log,
                arguments.suricata_log,
                zeek_index,
                result,
                arguments.window_seconds,
            )
        except OSError as error:
            print(f"Errore durante la scrittura del report JSON: {error}", file=sys.stderr)
            return 1
        print(f"\nReport JSON salvato: {arguments.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
