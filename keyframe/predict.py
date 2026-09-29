"""The deployable model: one object that predicts and explains from raw readings (R1-R2)."""

from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import shap

from keyframe import evaluate, experiments, explain, features, lockbox, paths, tuning

MODEL_FILE = "keyframe_xgboost.joblib"
META_FILE = "model_meta.json"
LIBRARIES = ("xgboost-cpu", "shap", "scikit-learn", "pandas", "numpy", "joblib")
TOP_FEATURES = 8


def library_versions() -> dict[str, str]:
    """Installed versions of the libraries the saved model depends on."""
    return {name: metadata.version(name) for name in LIBRARIES}


def alarm_settings(
    model: str = lockbox.MODEL, alarms_path: Path = paths.RESULTS / "04_alarms.csv"
) -> dict[str, float]:
    """Median of the per-fold chosen `min_duration_s` and `min_probability` for `model`."""
    table = pd.read_csv(alarms_path)
    chosen = table[table["model"] == model].drop_duplicates(subset="fold")
    return {
        "min_duration_s": float(chosen["min_duration_s"].median()),
        "min_probability": float(chosen["min_probability"].median()),
    }


@dataclass
class KeyframeModel:
    """A fitted XGBoost classifier with its feature recipe, alarm settings and metadata."""

    classifier: Any
    columns: list[str]
    classes: list[str]
    feature_settings: dict[str, Any]
    alarm: dict[str, float]
    sensor_groups: dict[str, str]
    versions: dict[str, str] = field(default_factory=library_versions)
    git_commit: str = ""
    _explainer: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def fit(
        cls,
        table: pd.DataFrame,
        params: dict,
        alarm: dict[str, float],
        *,
        columns: list[str] | None = None,
        git_commit: str | None = None,
    ) -> KeyframeModel:
        """Fit on every row of a feature table (all loads) with the given XGBoost params."""
        columns = columns or features.FEATURE_SETS[experiments.MODELLING_FEATURE_SET].columns(table)
        wrapper: Any = tuning.MODEL_BUILDERS[lockbox.MODEL](params)
        wrapper.fit(table[columns], table["label"])
        return cls(
            classifier=wrapper.model_,
            columns=list(columns),
            classes=[str(c) for c in wrapper.classes_],
            feature_settings={
                "feature_set": experiments.MODELLING_FEATURE_SET,
                "windows_s": [60, 300, 900],
                "stats": ["mean", "std", "slope"],
                "physics_features": [
                    c for c in columns if c.startswith("phys_") and "_roll_" not in c
                ],
                "params": params,
            },
            alarm=alarm,
            sensor_groups={c: explain.group_of(c) for c in columns},
            git_commit=git_commit if git_commit is not None else evaluate.git_commit(),
        )

    @classmethod
    def train_all_loads(cls) -> KeyframeModel:
        """The lockbox fit: median per-fold tuned params, all rows of the clean feature table."""
        return cls.fit(experiments.load_feature_table(), lockbox.median_params(), alarm_settings())

    def save(self, directory: Path = paths.MODELS) -> Path:
        """Write the joblib bundle and a human-readable `model_meta.json`; return the bundle path."""
        directory.mkdir(parents=True, exist_ok=True)
        payload = {k: v for k, v in self.__dict__.items() if k != "_explainer"}
        bundle = directory / MODEL_FILE
        joblib.dump(payload, bundle)
        meta = {k: v for k, v in payload.items() if k != "classifier"}
        meta["n_features"] = len(self.columns)
        (directory / META_FILE).write_text(json.dumps(meta, indent=2, default=str))
        return bundle

    @classmethod
    def load(cls, directory: Path = paths.MODELS) -> KeyframeModel:
        """Restore a saved model; warn when installed library versions differ from training."""
        model = cls(**joblib.load(directory / MODEL_FILE))
        now = library_versions()
        changed = {n: (v, now.get(n)) for n, v in model.versions.items() if now.get(n) != v}
        if changed:
            warnings.warn(
                f"library versions differ from training (saved, now): {changed}", stacklevel=2
            )
        return model

    def features(self, run_df: pd.DataFrame) -> pd.DataFrame:
        """Model feature frame for one run of raw readings (clean-table columns, time in `t`).

        Uses the training functions (physics, then causal trailing rolling stats)."""
        run = run_df if "run" in run_df.columns else run_df.assign(run="run")
        return features.build_feature_table(run)[self.columns]

    def predict_proba(self, run_df: pd.DataFrame) -> pd.DataFrame:
        """Class probabilities per row, columns in `classes` order."""
        frame = self.features(run_df)
        return pd.DataFrame(
            self.classifier.predict_proba(frame), index=run_df.index, columns=self.classes
        )

    @property
    def explainer(self) -> Any:
        """`shap.TreeExplainer` on the booster, built on first use (never pickled)."""
        if self._explainer is None:
            self._explainer = shap.TreeExplainer(self.classifier.get_booster())
        return self._explainer

    def explain(self, run_df: pd.DataFrame, row: int) -> dict[str, Any]:
        """Grouped and per-feature SHAP for the row at position `row` of `run_df`.

        `groups` are the five sensor groups' summed SHAP for the predicted class,
        `warmup` the window warm-up flags' share, so groups + warmup + base_value equal the
        raw margin of the predicted class. `groups_all_classes` has the same per class."""
        frame = self.features(run_df).iloc[[row]]
        values = np.asarray(self.explainer.shap_values(frame))
        # (1, features, classes) or (classes, 1, features)
        per_class = values[0].T if values.shape[0] == 1 else values[:, 0, :]
        base = np.atleast_1d(np.asarray(self.explainer.expected_value, dtype=float))
        margin = self.classifier.get_booster().inplace_predict(frame, predict_type="margin")
        proba = self.classifier.predict_proba(frame)[0]
        k = int(np.argmax(proba))

        def grouped(shap_row: np.ndarray) -> dict[str, float]:
            series = (
                pd.Series(shap_row, index=self.columns)
                .groupby([explain.group_of(c) for c in self.columns])
                .sum()
            )
            return {str(g): float(v) for g, v in series.items()}

        all_groups = {c: grouped(per_class[i]) for i, c in enumerate(self.classes)}
        groups = dict(all_groups[self.classes[k]])
        warmup = groups.pop(explain.WARMUP_LABEL, 0.0)
        for by_class in all_groups.values():
            by_class.pop(explain.WARMUP_LABEL, None)
        top = pd.Series(per_class[k], index=self.columns).sort_values(
            key=lambda s: s.abs(), ascending=False
        )[:TOP_FEATURES]
        return {
            "predicted_class": self.classes[k],
            "probabilities": dict(zip(self.classes, map(float, proba), strict=True)),
            "base_value": float(base[k]),
            "margin": float(np.asarray(margin)[0][k]),
            "groups": groups,
            "warmup": warmup,
            "groups_all_classes": all_groups,
            "top_features": [
                {"feature": f, "value": float(frame.iloc[0][str(f)]), "shap": float(v)}
                for f, v in top.items()
            ],
        }
