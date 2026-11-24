#!/usr/bin/env python3
"""Test locali dello Scenario C: non effettuano chiamate API e non alterano la campagna."""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scenario_c_core import (
    ROOT,
    advance_problem,
    automatic_repair_count,
    create_handoff,
    empty_memory,
    evaluate_response,
    load_json,
    load_problems,
    memory_path,
    model_identity_matches,
    new_state,
    parse_traceability,
    retrieve_memory,
    save_json,
    stage_two_assurance_required,
)
from revalidate_aliases import alias_name, remap_candidate
from audit_scenario_b import is_candidate_auxiliary, is_formulation_auxiliary


RUNS_B = ROOT / "esperimenti_cap5" / "runs" / "B"


def archived_response(model: str, problem: str, replicate: int = 1) -> tuple[str, dict]:
    run_dir = RUNS_B / model / problem / f"run_{replicate:02d}"
    return (
        (run_dir / "response.txt").read_text(encoding="utf-8"),
        json.loads((run_dir / "response.json").read_text(encoding="utf-8")),
    )


class ScenarioCTests(unittest.TestCase):
    @staticmethod
    def complete_traceability() -> str:
        return (
            'TRACEABILITY_JSON={"status":"READY","unresolved":[],"undefined_symbols":[],'
            '"requirements_mapped":["r1 -> c1","r2 -> c2","r3 -> c3","r4 -> c4"]}\n'
        )

    def test_known_correct_response_passes_definitive_validation(self) -> None:
        text, raw = archived_response("gpt-5.6-sol", "M01")
        with tempfile.TemporaryDirectory() as directory:
            result = evaluate_response("M01", text, raw, Path(directory))
            self.assertTrue(result["success"])
            private = load_json(Path(directory) / "validation_private.json")
            self.assertEqual(private["known_optimum"], 149.0)
            self.assertTrue(private["projected_feasible"])

    def test_execution_error_is_repairable_at_stage_three(self) -> None:
        text, raw = archived_response("claude-sonnet-5", "H10")
        with tempfile.TemporaryDirectory() as directory:
            result = evaluate_response("H10", text, raw, Path(directory))
            self.assertFalse(result["success"])
            self.assertTrue(result["repairable"])
            self.assertEqual(result["stage"], 3)
            self.assertEqual(result["failure_class"], "errore_di_esecuzione")

    def test_truncated_output_is_repairable_at_stage_three(self) -> None:
        text, raw = archived_response("deepseek-v4-flash", "H01")
        with tempfile.TemporaryDirectory() as directory:
            result = evaluate_response("H01", text, raw, Path(directory))
            self.assertFalse(result["success"])
            self.assertTrue(result["repairable"])
            self.assertEqual(result["stage"], 3)
            self.assertEqual(result["failure_class"], "output_troncato_o_senza_codice")

    def test_traceability_gate(self) -> None:
        text = (
            'TRACEABILITY_JSON={"status":"NEEDS_EXPERT","unresolved":["domanda mancante"],'
            '"undefined_symbols":[],"requirements_mapped":[]}\n'
        )
        result = parse_traceability(text)
        self.assertTrue(result["valid"])
        self.assertTrue(result["needs_expert"])

    def test_ready_traceability_requires_four_concrete_mappings(self) -> None:
        insufficient = parse_traceability(
            'TRACEABILITY_JSON={"status":"READY","unresolved":[],"undefined_symbols":[],'
            '"requirements_mapped":["domanda -> vincolo"]}'
        )
        self.assertFalse(insufficient["valid"])
        self.assertFalse(insufficient["complete_ready"])
        complete = parse_traceability(
            'TRACEABILITY_JSON={"status":"READY","unresolved":[],"undefined_symbols":[],'
            '"requirements_mapped":["r1 -> c1","r2 -> c2","r3 -> c3","r4 -> c4"]}'
        )
        self.assertTrue(complete["valid"])
        self.assertTrue(complete["complete_ready"])
        self.assertFalse(complete["needs_expert"])

    def test_missing_or_malformed_traceability_is_not_accepted(self) -> None:
        missing = parse_traceability("testo senza riga strutturata")
        malformed = parse_traceability("TRACEABILITY_JSON={non-json}")
        self.assertFalse(missing["valid"])
        self.assertFalse(malformed["valid"])
        self.assertTrue(missing["errors"])
        self.assertTrue(malformed["errors"])

    def test_stage_two_assurance_is_risk_based_and_frozen(self) -> None:
        evaluation = {"success": True}
        state = {
            "attempts": [
                {"kind": "INITIAL"},
                {"kind": "AUTO_REPAIR"},
            ],
            "stage_2_assurance_completed": False,
        }
        self.assertEqual(automatic_repair_count(state), 1)
        self.assertTrue(
            stage_two_assurance_required({"difficulty": "Elevata"}, state, evaluation)
        )
        self.assertFalse(
            stage_two_assurance_required({"difficulty": "Media"}, state, evaluation)
        )
        state["stage_2_assurance_completed"] = True
        self.assertFalse(
            stage_two_assurance_required({"difficulty": "Elevata"}, state, evaluation)
        )

    def test_deepseek_versioned_endpoint_is_same_frozen_model_family(self) -> None:
        self.assertTrue(
            model_identity_matches(
                "deepseek/deepseek-v4-flash", "deepseek/deepseek-v4-flash-0731"
            )
        )
        self.assertFalse(
            model_identity_matches(
                "deepseek/deepseek-v4-flash", "deepseek/deepseek-v5"
            )
        )

    def test_h05_synergy_auxiliary_aliases(self) -> None:
        self.assertEqual(alias_name("H05", "y_A_C"), "z_AC")
        self.assertEqual(alias_name("H05", "y_E_K"), "z_EK")
        self.assertEqual(alias_name("H05", "y_AC"), "z_AC")
        self.assertEqual(alias_name("H05", "y_EK"), "z_EK")

    def test_m05_bare_project_aliases(self) -> None:
        self.assertEqual(alias_name("M05", "P1"), "x_P1")
        self.assertEqual(alias_name("M05", "P8"), "x_P8")
        self.assertEqual(alias_name("M05", "x_3"), "x_P3")

    def test_m04_bare_vehicle_names_are_decision_variables(self) -> None:
        self.assertEqual(alias_name("M04", "Autocarro"), "x_Autocarro")
        self.assertEqual(alias_name("M04", "Elettrico"), "x_Elettrico")

    def test_m09_compact_variable_names(self) -> None:
        self.assertEqual(alias_name("M09", "x1"), "q_1")
        self.assertEqual(alias_name("M09", "y4"), "y_4")
        self.assertEqual(alias_name("M09", "I6"), "I_6")

    def test_h09_period_prefix_aliases(self) -> None:
        self.assertEqual(alias_name("H09", "x_A_T1"), "x_A_1")
        self.assertEqual(alias_name("H09", "I_C_T6"), "I_C_6")
        self.assertEqual(alias_name("H09", "y_B_T3"), "y_B_3")
        self.assertEqual(alias_name("H09", "o_T5"), "o_5")
        self.assertEqual(alias_name("H09", "overtime_T5"), "o_5")

    def test_h04_english_size_initials_are_normalized(self) -> None:
        self.assertEqual(alias_name("H04", "x_R3_S"), "x_R3_Piccolo")
        self.assertEqual(alias_name("H04", "x_R4_L"), "x_R4_Grande")
        self.assertEqual(alias_name("H04", "y_R2_M"), "y_R2_Medio")
        self.assertEqual(alias_name("H04", "z_R1_Medio"), "y_R1_Medio")
        self.assertEqual(alias_name("H04", "z_R4_L"), "y_R4_Grande")

    def test_h10_compact_arc_names_are_normalized(self) -> None:
        self.assertEqual(alias_name("H10", "x_SA_K1"), "f_K1_S_A")
        self.assertEqual(alias_name("H10", "x_DT_K2"), "f_K2_D_T")
        self.assertEqual(alias_name("H10", "y_SB"), "y_S_B")

    def test_h03_numeric_employee_and_day_indices_are_normalized(self) -> None:
        self.assertEqual(alias_name("H03", "x_1_1"), "x_E1_Lun")
        self.assertEqual(alias_name("H03", "x_8_7"), "x_E8_Dom")

    def test_h02_zero_based_periods_are_shifted_as_one_convention(self) -> None:
        candidate = {
            "status": "OPTIMAL",
            "objective": 1,
            "variables": {"x_A_0": 8, "x_A_1": 12, "I_C_3": 0, "y_B_2": 1},
        }
        remapped, aliases = remap_candidate("H02", candidate)
        self.assertEqual(remapped["variables"]["x_A_1"], 8)
        self.assertEqual(remapped["variables"]["x_A_2"], 12)
        self.assertEqual(remapped["variables"]["I_C_4"], 0)
        self.assertEqual(remapped["variables"]["y_B_3"], 1)
        self.assertEqual(aliases["x_A_0"], "x_A_1")

    def test_h02_inventory_symbol_s_is_an_alias_of_I(self) -> None:
        self.assertEqual(alias_name("H02", "s_A_1"), "I_A_1")
        self.assertEqual(alias_name("H02", "s_C_T4"), "I_C_4")

    def test_h02_expert_inventory_and_setup_families_are_disambiguated(self) -> None:
        candidate = {
            "status": "OPTIMAL",
            "objective": 1,
            "variables": {
                "x[A,1]": 20,
                "y[A,0]": 0,
                "y[A,1]": 12,
                "delta[A,1]": 1,
            },
        }
        remapped, aliases = remap_candidate("H02", candidate)
        self.assertEqual(remapped["variables"]["x_A_1"], 20)
        self.assertEqual(remapped["variables"]["I_A_0"], 0)
        self.assertEqual(remapped["variables"]["I_A_1"], 12)
        self.assertEqual(remapped["variables"]["y_A_1"], 1)
        self.assertEqual(aliases["delta[A,1]"], "y_A_1")
        self.assertTrue(is_candidate_auxiliary("H02", "I_C_0"))

    def test_h02_ground_truth_families_are_not_swapped_without_delta(self) -> None:
        candidate = {
            "status": "OPTIMAL",
            "objective": 1,
            "variables": {"I_A_1": 12, "y_A_1": 1},
        }
        remapped, _ = remap_candidate("H02", candidate)
        self.assertEqual(remapped["variables"], {"I_A_1": 12, "y_A_1": 1})

    def test_h01_expert_notation_swaps_opening_and_shipment_families(self) -> None:
        self.assertEqual(alias_name("H01", "x_A"), "y_A")
        self.assertEqual(alias_name("H01", "y_A_Z1"), "x_Z1_A")
        self.assertEqual(alias_name("H01", "y_F_Z8"), "x_Z8_F")

    def test_h06_completion_and_order_variables_are_auxiliary(self) -> None:
        self.assertTrue(is_formulation_auxiliary("H06", "C_J4"))
        self.assertTrue(is_formulation_auxiliary("H06", "o_J1_J2"))
        self.assertFalse(is_formulation_auxiliary("H06", "S_J4"))
        self.assertFalse(is_formulation_auxiliary("H06", "T_J4"))

    def test_h06_zero_based_python_indices_are_shifted_to_job_labels(self) -> None:
        candidate = {
            "status": "OPTIMAL",
            "objective": 1,
            "variables": {
                "S[0]": 0,
                "C[6]": 35,
                "T[6]": 10,
                "y[0,1]": 1,
                "y[5,6]": 0,
            },
        }
        remapped, aliases = remap_candidate("H06", candidate)
        self.assertEqual(remapped["variables"]["S_J1"], 0)
        self.assertEqual(remapped["variables"]["C_J7"], 35)
        self.assertEqual(remapped["variables"]["T_J7"], 10)
        self.assertEqual(remapped["variables"]["o_J1_J2"], 1)
        self.assertEqual(remapped["variables"]["o_J6_J7"], 0)
        self.assertEqual(aliases["S[0]"], "S_J1")

    def test_h06_one_based_job_labels_are_not_shifted(self) -> None:
        candidate = {
            "status": "OPTIMAL",
            "objective": 1,
            "variables": {"S_J1": 0, "C_J7": 35, "o_J1_J7": 1},
        }
        remapped, _ = remap_candidate("H06", candidate)
        self.assertEqual(
            remapped["variables"],
            {"S_J1": 0, "C_J7": 35, "o_J1_J7": 1},
        )

    def test_m06_candidate_loads_are_derived_auxiliaries(self) -> None:
        self.assertTrue(is_candidate_auxiliary("M06", "C_A"))
        self.assertTrue(is_candidate_auxiliary("M06", "C_B"))
        self.assertTrue(is_candidate_auxiliary("M06", "Load_A"))
        self.assertTrue(is_candidate_auxiliary("M06", "Load_B"))
        self.assertFalse(is_candidate_auxiliary("M06", "x_J1_A"))
        self.assertEqual(alias_name("M06", "y_J1_A"), "x_J1_A")
        self.assertEqual(alias_name("M06", "makespan"), "Cmax")

    def test_h07_activation_families_are_mapped_by_index_shape(self) -> None:
        self.assertEqual(alias_name("H07", "y_A_C1"), "z_A_C1")
        self.assertEqual(alias_name("H07", "y_F_C3"), "z_F_C3")
        self.assertEqual(alias_name("H07", "z_A"), "y_A")
        self.assertEqual(alias_name("H07", "z_F"), "y_F")

    def test_json_writer_sanitizes_non_finite_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "safe.json"
            save_json(path, {"infinite": math.inf, "nan": math.nan})
            self.assertEqual(load_json(path), {"infinite": None, "nan": None})

    def test_memory_is_separate_and_retrieval_is_tag_based(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model = "test-model"
            memory = empty_memory(model)
            memory["semantic"].append(
                {
                    "id": "S-001",
                    "created_at_utc": "2026-01-01T00:00:00+00:00",
                    "principle": "Collegare ogni binaria di attivazione alla quantità corrispondente.",
                    "tags": ["Produzione", "MILP intera"],
                }
            )
            save_json(memory_path(model, root), memory)
            problem = load_problems()["M02"]
            retrieval = retrieve_memory(model, problem, root)
            self.assertEqual(len(retrieval["semantic"]), 1)
            other = retrieve_memory("other-model", problem, root)
            self.assertEqual(other["semantic"], [])

    def test_handoff_packet_never_contains_known_optimum(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = root / "runs" / "test" / "01_M01"
            attempt_dir = run_dir / "attempt_00"
            attempt_dir.mkdir(parents=True)
            (attempt_dir / "response.txt").write_text("risposta\n", encoding="utf-8")
            (attempt_dir / "generated.py").write_text("print('x')\n", encoding="utf-8")
            save_json(
                attempt_dir / "validation_public.json",
                {"correct": False, "gap_within_tolerance": False},
            )
            problem = load_problems()["M01"]
            state = new_state("test-model", problem, 1, {"semantic": [], "episodic": []})
            failure = {
                "success": False,
                "repairable": False,
                "stage": 4,
                "failure_class": "validazione_indipendente_fallita",
                "detail": "gap oltre soglia",
            }
            state["attempts"].append(
                {"number": 0, "kind": "INITIAL", "directory": "attempt_00", "evaluation": failure}
            )
            handoff_dir = create_handoff(run_dir, state, "Traccia pubblica", failure)
            packet_text = (handoff_dir / "packet.json").read_text(encoding="utf-8")
            self.assertNotIn("known_optimum", packet_text)
            self.assertNotIn('"objective": 149', packet_text)
            self.assertFalse(load_json(handoff_dir / "packet.json")["ground_truth_disclosed"])

    def test_stage_two_assurance_packet_hides_validation_and_allows_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = root / "runs" / "test" / "01_H01"
            attempt_dir = run_dir / "attempt_01"
            attempt_dir.mkdir(parents=True)
            (attempt_dir / "response.txt").write_text("risposta\n", encoding="utf-8")
            (attempt_dir / "generated.py").write_text("print('x')\n", encoding="utf-8")
            save_json(attempt_dir / "validation_public.json", {"correct": True})
            problem = load_problems()["H01"]
            state = new_state("test-model", problem, 1, {"semantic": [], "episodic": []})
            state["attempts"] = [
                {"number": 0, "kind": "INITIAL", "directory": "attempt_00", "evaluation": {"success": False}},
                {"number": 1, "kind": "AUTO_REPAIR", "directory": "attempt_01", "evaluation": {"success": True}},
            ]
            request = {
                "stage": 2,
                "failure_class": "revisione_di_assicurazione_post_riparazione",
                "detail": "revisione richiesta",
                "handoff_mode": "ASSURANCE_REVIEW",
            }
            handoff_dir = create_handoff(run_dir, state, "Traccia pubblica", request)
            packet = load_json(handoff_dir / "packet.json")
            self.assertIsNone(packet["validation"])
            self.assertIn("APPROVE", packet["allowed_actions"])
            self.assertFalse(packet["ground_truth_disclosed"])

    def test_missing_traceability_gets_one_repair_before_medium_problem_finishes(self) -> None:
        text, raw = archived_response("gpt-5.6-sol", "M01")
        with tempfile.TemporaryDirectory() as directory, patch(
            "scenario_c_core.call_openrouter",
            side_effect=[(text, raw), (self.complete_traceability() + text, raw)],
        ) as mocked_call:
            root = Path(directory)
            result = advance_problem("gpt-5.6-sol", "M01", 1, root)
            self.assertEqual(result["status"], "COMPLETED")
            self.assertTrue(result["final"]["correct"])
            self.assertEqual(result["final"]["traceability_repair_count"], 1)
            self.assertEqual(mocked_call.call_count, 2)

    def test_high_problem_after_repair_stops_for_real_stage_two_review(self) -> None:
        text, raw = archived_response("gpt-5.6-sol", "H03")
        with tempfile.TemporaryDirectory() as directory, patch(
            "scenario_c_core.call_openrouter",
            side_effect=[(text, raw), (self.complete_traceability() + text, raw)],
        ):
            root = Path(directory)
            first = advance_problem("gpt-5.6-sol", "H03", 1, root)
            self.assertEqual(first["status"], "AWAITING_HANDOFF")
            handoff_dir = Path(first["handoff_dir"])
            packet = load_json(handoff_dir / "packet.json")
            self.assertEqual(packet["stage"], 2)
            self.assertEqual(packet["handoff_mode"], "ASSURANCE_REVIEW")
            save_json(
                handoff_dir / "expert_response.json",
                {
                    "status": "SUBMITTED",
                    "action": "APPROVE",
                    "active_minutes": 1.5,
                    "expert_instruction": "",
                    "correction_summary": "Modello controllato con la checklist e approvato.",
                    "semantic_principle": "",
                    "submitted_at_utc": "2026-08-24T00:00:00+00:00",
                },
            )
            with patch("scenario_c_core.call_openrouter") as no_more_calls:
                second = advance_problem("gpt-5.6-sol", "H03", 1, root)
            self.assertEqual(second["status"], "COMPLETED")
            self.assertTrue(second["final"]["correct"])
            self.assertEqual(second["final"]["handoff_stages"], [2])
            self.assertEqual(second["final"]["human_minutes"], 1.5)
            no_more_calls.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
