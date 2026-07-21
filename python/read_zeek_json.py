#!/usr/bin/env python3

"""Analizza log Zeek ``conn.log`` in formato JSON Lines.

Il programma usa soltanto la libreria standard Python, legge una riga alla
volta e supporta sia file di testo sia archivi gzip. Il report esportato non
contiene indirizzi IP o UID Zeek.
"""

import argparse
from collections import Counter
from dataclasses import dataclass, field
import gzip
import json
from pathlib import Path
import sys
from typing import TextIO


@dataclass
class AnalysisResult:
    """Statistiche aggregate di un ``conn.log`` Zeek."""

    valid_events: int = 0
    malformed_lines: int = 0
    empty_lines: int = 0
    protocol_counts: Counter[str] = field(default_factory=Counter)
    service_counts: Counter[str] = field(default_factory=Counter)
    destination_port_counts: Counter[int] = field(default_factory=Counter)
    connection_state_counts: Counter[str] = field(default_factory=Counter)
    total_orig_bytes: int = 0
    total_resp_bytes: int = 0
    total_duration: float = 0.0
    events_with_duration: int = 0

    @property
    def average_duration(self) -> float:
        """Durata media degli eventi con un campo ``duration`` valido."""

        if self.events_with_duration == 0:
            return 0.0
        return self.total_duration / self.events_with_duration


def parse_arguments() -> argparse.Namespace:
    """Legge gli argomenti della riga di comando."""

    parser = argparse.ArgumentParser(
        description=(
            "Analizza un conn.log JSON di Zeek, anche compresso, "
            "e produce statistiche testuali e JSON."
        )
    )
    parser.add_argument(
        "log_path",
        type=Path,
        help="Percorso del file Zeek JSONL oppure JSONL.gz.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Percorso facoltativo nel quale salvare il report JSON.",
    )
    return parser.parse_args()


def open_text_log(log_path: Path) -> TextIO:
    """Apre un file normale oppure gzip in modalità testo UTF-8."""

    if log_path.suffix.lower() == ".gz":
        return gzip.open(log_path, mode="rt", encoding="utf-8")
    return log_path.open(mode="r", encoding="utf-8")


def add_string_value(counter: Counter[str], value: object) -> None:
    """Conta ``value`` soltanto quando è una stringa non vuota."""

    if not isinstance(value, str):
        return
    clean_value = value.strip()
    if clean_value:
        counter[clean_value] += 1


def add_services(counter: Counter[str], value: object) -> None:
    """Separa e conta servizi multipli, per esempio ``quic,ssl``."""

    if not isinstance(value, str):
        return
    for service in value.split(","):
        clean_service = service.strip()
        if clean_service:
            counter[clean_service] += 1


def get_non_negative_int(value: object) -> int | None:
    """Restituisce un intero non negativo, escludendo i booleani."""

    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    return None


def get_non_negative_number(value: object) -> float | None:
    """Restituisce un numero non negativo convertito in ``float``."""

    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and value >= 0:
        return float(value)
    return None


def analyze_log(log_path: Path) -> AnalysisResult:
    """Legge il log una riga alla volta e calcola le statistiche."""

    result = AnalysisResult()
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
            add_string_value(result.protocol_counts, event.get("proto"))
            add_services(result.service_counts, event.get("service"))
            add_string_value(
                result.connection_state_counts,
                event.get("conn_state"),
            )

            destination_port = get_non_negative_int(event.get("id.resp_p"))
            if destination_port is not None:
                result.destination_port_counts[destination_port] += 1

            orig_bytes = get_non_negative_int(event.get("orig_bytes"))
            if orig_bytes is not None:
                result.total_orig_bytes += orig_bytes

            resp_bytes = get_non_negative_int(event.get("resp_bytes"))
            if resp_bytes is not None:
                result.total_resp_bytes += resp_bytes

            duration = get_non_negative_number(event.get("duration"))
            if duration is not None:
                result.total_duration += duration
                result.events_with_duration += 1

    return result


def format_bytes(byte_count: int) -> str:
    """Mostra i byte esatti e una rappresentazione leggibile."""

    units = ("B", "KiB", "MiB", "GiB")
    value = float(byte_count)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{byte_count} B"
            return f"{byte_count} B ({value:.2f} {unit})"
        value /= 1024
    return f"{byte_count} B"


def result_to_dict(log_path: Path, result: AnalysisResult) -> dict[str, object]:
    """Converte i risultati in una struttura JSON priva di dati grezzi."""

    destination_ports = {
        str(port): count
        for port, count in result.destination_port_counts.most_common()
    }
    return {
        "source": str(log_path),
        "privacy": {
            "raw_ip_addresses_included": False,
            "zeek_uids_included": False,
        },
        "summary": {
            "valid_events": result.valid_events,
            "malformed_lines": result.malformed_lines,
            "empty_lines": result.empty_lines,
        },
        "traffic": {
            "orig_bytes": result.total_orig_bytes,
            "resp_bytes": result.total_resp_bytes,
            "total_bytes": result.total_orig_bytes + result.total_resp_bytes,
        },
        "duration": {
            "events_with_duration": result.events_with_duration,
            "total_seconds": result.total_duration,
            "average_seconds": result.average_duration,
        },
        "protocols": dict(result.protocol_counts.most_common()),
        "services": dict(result.service_counts.most_common()),
        "destination_ports": destination_ports,
        "connection_states": dict(result.connection_state_counts.most_common()),
    }


def write_json_report(
    output_path: Path,
    log_path: Path,
    result: AnalysisResult,
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
    counter: Counter[str] | Counter[int],
    limit: int | None = None,
) -> None:
    """Stampa un ``Counter`` ordinato per frequenza."""

    print(f"\n{title}:")
    if not counter:
        print("- nessun valore disponibile")
        return
    for value, count in counter.most_common(limit):
        print(f"- {value}: {count}")


def print_report(log_path: Path, result: AnalysisResult) -> None:
    """Stampa il report testuale."""

    print(f"File analizzato: {log_path}")
    print(f"Eventi JSON validi: {result.valid_events}")
    print(f"Righe malformate: {result.malformed_lines}")
    print(f"Righe vuote: {result.empty_lines}")
    print("Byte inviati dall'origine: " f"{format_bytes(result.total_orig_bytes)}")
    print("Byte ricevuti dall'origine: " f"{format_bytes(result.total_resp_bytes)}")
    print(
        "Durata media: "
        f"{result.average_duration:.3f} secondi "
        f"su {result.events_with_duration} eventi"
    )
    print_counter("Protocolli", result.protocol_counts)
    print_counter("Servizi", result.service_counts)
    print_counter(
        "Porte di destinazione più usate",
        result.destination_port_counts,
        limit=10,
    )
    print_counter("Stati delle connessioni", result.connection_state_counts)


def main() -> int:
    """Coordina lettura, presentazione ed esportazione."""

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
        print(
            f"Errore: il percorso è una directory: {arguments.log_path}",
            file=sys.stderr,
        )
        return 1
    except gzip.BadGzipFile:
        print(f"Errore: file gzip non valido: {arguments.log_path}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(
            f"Errore: il file non contiene testo UTF-8 valido: {arguments.log_path}",
            file=sys.stderr,
        )
        return 1

    print_report(arguments.log_path, result)
    if arguments.json_output is not None:
        try:
            write_json_report(arguments.json_output, arguments.log_path, result)
        except OSError as error:
            print(
                f"Errore durante la scrittura del report JSON: {error}",
                file=sys.stderr,
            )
            return 1
        print(f"\nReport JSON salvato: {arguments.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
