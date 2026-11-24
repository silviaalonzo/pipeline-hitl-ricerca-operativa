#!/usr/bin/env python3
"""Produce statistiche e figure riproducibili per lo Scenario B."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
})


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "RISULTATI_DEFINITIVI_SCENARIO_B.csv"
FIG_DIR = HERE.parent / "figures_cap5"

MODEL_ORDER = [
    "openai/gpt-5.6-sol",
    "anthropic/claude-sonnet-5",
    "deepseek/deepseek-v4-flash",
]
LABELS = {
    "openai/gpt-5.6-sol": "GPT-5.6 Sol",
    "anthropic/claude-sonnet-5": "Claude Sonnet 5",
    "deepseek/deepseek-v4-flash": "DeepSeek V4 Flash",
}
COLORS = {
    "openai/gpt-5.6-sol": "#2F5597",
    "anthropic/claude-sonnet-5": "#5B9BD5",
    "deepseek/deepseek-v4-flash": "#9DC3E6",
}


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    proportion = k / n
    denominator = 1 + z * z / n
    centre = (proportion + z * z / (2 * n)) / denominator
    half = z * math.sqrt(proportion * (1 - proportion) / n + z * z / (4 * n * n)) / denominator
    return centre - half, centre + half


def as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().map({"true": True, "false": False}).fillna(False).astype(bool)


def summarize(df: pd.DataFrame) -> dict:
    result: dict[str, object] = {
        "n_runs": int(len(df)),
        "total_api_cost_usd": float(df["api_cost_usd"].sum()),
        "models": {},
    }
    for model in MODEL_ORDER:
        group = df[df["requested_model"] == model].copy()
        primary = group[group["replicate"] == 1]
        pass_n = int(group["pass"].sum())
        correct_n = int(group["correct"].sum())
        primary_n = int(primary["correct"].sum())
        ci_low, ci_high = wilson(primary_n, len(primary))
        per_problem = group.groupby("problem_id")["correct"].sum()
        by_difficulty = group.groupby("difficulty")["correct"].agg(["sum", "count"])
        by_replicate = group.groupby("replicate")["correct"].agg(["sum", "count"])
        latency = group["response_seconds"]
        result["models"][model] = {
            "label": LABELS[model],
            "n": int(len(group)),
            "pass_n": pass_n,
            "pass_rate": pass_n / len(group),
            "correct_n": correct_n,
            "accuracy": correct_n / len(group),
            "conditional_accuracy": correct_n / pass_n if pass_n else None,
            "primary_correct_n": primary_n,
            "primary_accuracy": primary_n / len(primary),
            "primary_wilson95": [ci_low, ci_high],
            "difficulty": {
                difficulty: {
                    "correct_n": int(row["sum"]),
                    "n": int(row["count"]),
                    "accuracy": float(row["sum"] / row["count"]),
                }
                for difficulty, row in by_difficulty.iterrows()
            },
            "replicates": {
                str(int(replicate)): {
                    "correct_n": int(row["sum"]),
                    "n": int(row["count"]),
                    "accuracy": float(row["sum"] / row["count"]),
                }
                for replicate, row in by_replicate.iterrows()
            },
            "problem_stability": {
                "three_of_three": int((per_problem == 3).sum()),
                "partial": int(((per_problem > 0) & (per_problem < 3)).sum()),
                "zero_of_three": int((per_problem == 0).sum()),
            },
            "response_seconds": {
                "mean": float(latency.mean()),
                "sd": float(latency.std()),
                "median": float(latency.median()),
                "q1": float(latency.quantile(0.25)),
                "q3": float(latency.quantile(0.75)),
            },
            "mean_total_tokens": float(group["total_tokens"].mean()),
            "mean_reasoning_tokens": float(group["reasoning_tokens"].mean()),
            "mean_api_cost_usd": float(group["api_cost_usd"].mean()),
            "total_api_cost_usd": float(group["api_cost_usd"].sum()),
            "api_cost_per_correct_usd": float(group["api_cost_usd"].sum() / correct_n),
        }
    return result


def style_axis(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D9DDE1", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=10)


def plot_pass_accuracy(analysis: dict) -> None:
    labels = [LABELS[m] for m in MODEL_ORDER]
    pass_rates = [analysis["models"][m]["pass_rate"] * 100 for m in MODEL_ORDER]
    accuracies = [analysis["models"][m]["accuracy"] * 100 for m in MODEL_ORDER]
    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    bars1 = ax.bar(
        x - width / 2,
        pass_rates,
        width,
        label="Pass rate",
        color="#C8CDD2",
        edgecolor="#5B6065",
        linewidth=0.55,
    )
    bars2 = ax.bar(
        x + width / 2,
        accuracies,
        width,
        label="Accuratezza",
        color="#34393E",
        edgecolor="#34393E",
        linewidth=0.55,
    )
    ax.set_ylabel("Percentuale delle 60 esecuzioni")
    ax.set_ylim(0, 108)
    ax.set_xticks(x, labels)
    ax.legend(frameon=False, ncols=2, loc="upper right")
    style_axis(ax)
    for bars in (bars1, bars2):
        ax.bar_label(bars, labels=[f"{b.get_height():.1f}%" for b in bars], padding=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "figura_5_1_pass_accuracy.png", dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_difficulty(analysis: dict) -> None:
    labels = [LABELS[m] for m in MODEL_ORDER]
    medium = [analysis["models"][m]["difficulty"]["Media"]["accuracy"] * 100 for m in MODEL_ORDER]
    high = [analysis["models"][m]["difficulty"]["Elevata"]["accuracy"] * 100 for m in MODEL_ORDER]
    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    bars1 = ax.bar(
        x - width / 2,
        medium,
        width,
        label="Difficoltà media",
        color="#C8CDD2",
        edgecolor="#5B6065",
        linewidth=0.55,
    )
    bars2 = ax.bar(
        x + width / 2,
        high,
        width,
        label="Difficoltà elevata",
        color="#34393E",
        edgecolor="#34393E",
        linewidth=0.55,
    )
    ax.set_ylabel("Accuratezza sulle 30 esecuzioni")
    ax.set_ylim(0, 108)
    ax.set_xticks(x, labels)
    ax.legend(frameon=False, ncols=2, loc="upper right")
    style_axis(ax)
    for bars in (bars1, bars2):
        ax.bar_label(bars, labels=[f"{b.get_height():.1f}%" for b in bars], padding=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "figura_5_2_difficulty.png", dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(SOURCE)
    for column in ["pass", "feasible", "correct"]:
        df[column] = as_bool(df[column])
    analysis = summarize(df)
    plot_pass_accuracy(analysis)
    plot_difficulty(analysis)
    print("Figure dello Scenario B aggiornate dai risultati definitivi")


if __name__ == "__main__":
    main()
