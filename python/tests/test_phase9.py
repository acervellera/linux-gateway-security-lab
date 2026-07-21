"""Test automatici per gli analizzatori della fase 9."""

import gzip
import io
import json
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stderr
from pathlib import Path

from correlate_logs import (
    canonical_flow_key,
    correlate_logs,
    load_zeek_index,
    parse_iso_timestamp,
    result_to_dict as correlation_to_dict,
)
from read_suricata_json import (
    analyze_log as analyze_suricata,
    get_non_negative_int as suricata_int,
    parse_hour,
    result_to_dict as suricata_to_dict,
    write_json_report as write_suricata_report,
)
from read_zeek_json import (
    AnalysisResult,
    add_services,
    analyze_log as analyze_zeek,
    format_bytes,
    get_non_negative_int,
    get_non_negative_number,
    result_to_dict as zeek_to_dict,
    write_json_report as write_zeek_report,
)

PYTHON_DIR = Path(__file__).resolve().parents[1]
ZEEK_SAMPLE = PYTHON_DIR / "samples" / "zeek_conn_sample.jsonl"
SURICATA_SAMPLE = PYTHON_DIR / "samples" / "suricata_eve_sample.jsonl"
CORRELATION_SAMPLE = PYTHON_DIR / "samples" / "suricata_correlation_sample.jsonl"


class ZeekAnalyzeTests(unittest.TestCase):
    def test_sample_statistics(self) -> None:
        with redirect_stderr(io.StringIO()) as errors:
            result = analyze_zeek(ZEEK_SAMPLE)
        self.assertEqual(result.valid_events, 4)
        self.assertEqual(result.malformed_lines, 1)
        self.assertEqual(result.protocol_counts, Counter({"udp": 2, "tcp": 2}))
        self.assertEqual(result.service_counts, Counter({"dns": 1, "ssl": 1, "quic": 1, "http": 1}))
        self.assertEqual(result.destination_port_counts, Counter({443: 2, 53: 1, 80: 1}))
        self.assertEqual(result.connection_state_counts, Counter({"SF": 3, "S0": 1}))
        self.assertEqual(result.total_orig_bytes, 1512)
        self.assertEqual(result.total_resp_bytes, 6170)
        self.assertAlmostEqual(result.average_duration, 0.57375)
        self.assertIn("Riga 4 ignorata", errors.getvalue())

    def test_gzip_produces_same_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "conn.log.gz"
            with ZEEK_SAMPLE.open(encoding="utf-8") as source:
                with gzip.open(path, "wt", encoding="utf-8") as target:
                    target.write(source.read())
            with redirect_stderr(io.StringIO()):
                result = analyze_zeek(path)
            self.assertEqual(result.valid_events, 4)
            self.assertEqual(result.total_orig_bytes, 1512)

    def test_missing_file_raises_error(self) -> None:
        with self.assertRaises(FileNotFoundError):
            analyze_zeek(PYTHON_DIR / "samples" / "missing.jsonl")

    def test_result_to_dict(self) -> None:
        with redirect_stderr(io.StringIO()):
            result = analyze_zeek(ZEEK_SAMPLE)
        report = zeek_to_dict(ZEEK_SAMPLE, result)
        self.assertEqual(report["traffic"]["total_bytes"], 7682)
        self.assertFalse(report["privacy"]["raw_ip_addresses_included"])

    def test_write_json_report(self) -> None:
        with redirect_stderr(io.StringIO()):
            result = analyze_zeek(ZEEK_SAMPLE)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "report.json"
            write_zeek_report(path, ZEEK_SAMPLE, result)
            self.assertEqual(json.loads(path.read_text())["protocols"]["tcp"], 2)

    def test_multiple_services_are_separated(self) -> None:
        counter: Counter[str] = Counter()
        add_services(counter, "quic,ssl")
        self.assertEqual(counter, Counter({"quic": 1, "ssl": 1}))

    def test_services_ignore_spaces_and_empty_values(self) -> None:
        counter: Counter[str] = Counter()
        add_services(counter, " quic, ssl, , ")
        self.assertEqual(counter, Counter({"quic": 1, "ssl": 1}))

    def test_boolean_is_not_accepted_as_integer(self) -> None:
        self.assertIsNone(get_non_negative_int(True))
        self.assertIsNone(get_non_negative_int(False))

    def test_negative_numbers_are_rejected(self) -> None:
        self.assertIsNone(get_non_negative_int(-1))
        self.assertIsNone(get_non_negative_number(-0.5))

    def test_average_duration_without_events(self) -> None:
        self.assertEqual(AnalysisResult().average_duration, 0.0)

    def test_byte_formatting(self) -> None:
        self.assertEqual(format_bytes(512), "512 B")
        self.assertEqual(format_bytes(1536), "1536 B (1.50 KiB)")


class SuricataTests(unittest.TestCase):
    def test_sample_statistics(self) -> None:
        with redirect_stderr(io.StringIO()) as errors:
            result = analyze_suricata(SURICATA_SAMPLE)
        self.assertEqual(result.valid_events, 6)
        self.assertEqual(result.malformed_lines, 1)
        self.assertEqual(result.protocol_counts, Counter({"TCP": 3, "UDP": 2}))
        self.assertEqual(result.destination_port_counts[443], 4)
        self.assertEqual(result.total_flow_bytes, 6000)
        self.assertEqual(result.alert_action_counts["allowed"], 1)
        self.assertEqual(result.anomaly_type_counts["applayer"], 1)
        self.assertIn("Riga 7 ignorata", errors.getvalue())

    def test_gzip_produces_same_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "eve.json.gz"
            with SURICATA_SAMPLE.open(encoding="utf-8") as source:
                with gzip.open(path, "wt", encoding="utf-8") as target:
                    target.write(source.read())
            with redirect_stderr(io.StringIO()):
                result = analyze_suricata(path)
            self.assertEqual(result.valid_events, 6)
            self.assertEqual(result.total_flow_bytes, 6000)

    def test_report_omits_raw_ip_addresses(self) -> None:
        with redirect_stderr(io.StringIO()):
            result = analyze_suricata(SURICATA_SAMPLE)
        report = suricata_to_dict(SURICATA_SAMPLE, result)
        serialized = json.dumps(report)
        self.assertNotIn("10.42.0.10", serialized)
        self.assertFalse(report["privacy"]["raw_ip_addresses_included"])

    def test_write_json_report(self) -> None:
        with redirect_stderr(io.StringIO()):
            result = analyze_suricata(SURICATA_SAMPLE)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "report.json"
            write_suricata_report(path, SURICATA_SAMPLE, result)
            self.assertEqual(json.loads(path.read_text())["flows"]["total_bytes"], 6000)

    def test_parse_hour(self) -> None:
        self.assertEqual(parse_hour("2026-07-21T14:15:30+02:00"), "2026-07-21 14:00")
        self.assertEqual(parse_hour("2026-07-21T12:15:30Z"), "2026-07-21 12:00")
        self.assertIsNone(parse_hour("non-valido"))

    def test_boolean_is_not_integer(self) -> None:
        self.assertIsNone(suricata_int(True))
        self.assertIsNone(suricata_int(False))


class CorrelationTests(unittest.TestCase):
    def test_direction_does_not_change_key(self) -> None:
        direct = canonical_flow_key("TCP", "10.42.0.10", 53002, "198.51.100.20", 443)
        reverse = canonical_flow_key("tcp", "198.51.100.20", 443, "10.42.0.10", 53002)
        self.assertEqual(direct, reverse)

    def test_iso_timestamp_with_timezone(self) -> None:
        self.assertAlmostEqual(parse_iso_timestamp("2026-07-21T14:05:00.100000+02:00"), 1784635500.1)

    def test_timestamp_without_timezone_is_rejected(self) -> None:
        self.assertIsNone(parse_iso_timestamp("2026-07-21T14:05:00"))

    def test_load_sample_index(self) -> None:
        with redirect_stderr(io.StringIO()):
            index = load_zeek_index(ZEEK_SAMPLE)
        self.assertEqual(index.loaded_connections, 4)
        self.assertEqual(index.malformed_lines, 1)
        self.assertAlmostEqual(index.minimum_timestamp, 1784635500.1)

    def test_sample_correlation(self) -> None:
        with redirect_stderr(io.StringIO()):
            _, result = correlate_logs(ZEEK_SAMPLE, CORRELATION_SAMPLE, 2.0)
        self.assertEqual(result.suricata_valid_events, 8)
        self.assertEqual(result.matched_suricata_events, 5)
        self.assertEqual(result.unmatched_suricata_events, 1)
        self.assertEqual(len(result.matched_zeek_identifiers), 4)
        self.assertAlmostEqual(result.match_percentage, 83.33333333333334)
        self.assertEqual(result.zeek_connection_match_percentage, 100.0)
        self.assertEqual(result.matched_alert_signature_counts["SYNTHETIC correlation alert"], 1)

    def test_json_omits_ips_and_uids(self) -> None:
        with redirect_stderr(io.StringIO()):
            index, result = correlate_logs(ZEEK_SAMPLE, CORRELATION_SAMPLE, 2.0)
        report = correlation_to_dict(ZEEK_SAMPLE, CORRELATION_SAMPLE, index, result, 2.0)
        serialized = json.dumps(report)
        self.assertNotIn("10.42.0.10", serialized)
        self.assertNotIn("C_SAMPLE_001", serialized)
        self.assertFalse(report["privacy"]["raw_ip_addresses_included"])


if __name__ == "__main__":
    unittest.main()
