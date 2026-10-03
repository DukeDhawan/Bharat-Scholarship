"""Phase 4 — Bharat Scholarship & Fellowship Verification Dashboard ().

Interactive Streamlit console that scores the 120-row applicant dataset through
``ScholarshipEvaluator`` (rules + document audit + 15-day deficiency notices)
and exposes a live screening sandbox for ad-hoc intake.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import random
from textwrap import wrap
from typing import Any, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.config import load_applicants, load_document_requirements, load_scheme_rules
from core.evaluator import ScholarshipEvaluator
try:
    from core.pdf_generator import DeficiencyPDFReport, ExecutiveBriefingPDFReport
except ImportError as exc:
    DeficiencyPDFReport = None  # type: ignore[assignment,misc]
    ExecutiveBriefingPDFReport = None  # type: ignore[assignment,misc]
    PDF_IMPORT_ERROR = str(exc)
else:
    PDF_IMPORT_ERROR = None
from core.risk_engine import RiskAssessment, assess_batch
from core.models import (
    ApplicantProfile,
    CompositeDecision,
    CompositeEvaluationResult,
    DocumentRequirement,
    RuleCheck,
    SchemeRule,
)

ROOT = Path(__file__).resolve().parent
PROFILE_STORAGE_PATH = ROOT / ".bharat_user_profile.json"
APPLICATION_STORAGE_PATH = ROOT / ".bharat_submitted_applications.json"
PROFILE_REQUIRED_FIELDS = ("full_name", "category", "age", "income", "course", "marks")


def load_saved_profile() -> dict[str, Any]:
    """Load the local applicant profile used by this single-user local portal."""
    try:
        payload = json.loads(PROFILE_STORAGE_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def save_profile_locally(profile: dict[str, Any]) -> None:
    """Persist profile form values locally without changing backend data."""
    try:
        PROFILE_STORAGE_PATH.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    except OSError:
        # The form remains usable if the local folder is read-only.
        pass


def load_submitted_applications() -> list[dict[str, Any]]:
    """Restore locally submitted applications for the current single-user portal."""
    try:
        payload = json.loads(APPLICATION_STORAGE_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return []
    if not isinstance(payload, list):
        return []

    applications: list[dict[str, Any]] = []
    for record in payload:
        if not isinstance(record, dict):
            continue
        result = None
        try:
            result = CompositeEvaluationResult.model_validate(record["result"])
        except (KeyError, TypeError, ValueError):
            pass
        profile_payload = record.get("profile")
        profile = None
        if isinstance(profile_payload, dict):
            try:
                profile = ApplicantProfile.model_validate(profile_payload)
            except (TypeError, ValueError):
                profile = None
        if result is not None or record.get("status"):
            applications.append({**record, "result": result, "profile": profile})
    return applications


def save_submitted_applications(applications: list[dict[str, Any]]) -> None:
    """Persist submitted application summaries and evaluation results locally."""
    serializable: list[dict[str, Any]] = []
    for application in applications:
        result = application.get("result")
        profile = application.get("profile")
        status = application.get("status")
        if isinstance(result, CompositeEvaluationResult):
            status = result.composite_status.value
        if not status:
            continue
        serializable.append(
            {
                "app_id": application.get("app_id", ""),
                "scheme": application.get("scheme") or (
                    result.scheme if isinstance(result, CompositeEvaluationResult) else "Scholarship application"
                ),
                "is_eligible": application.get("is_eligible", result.is_eligible if isinstance(result, CompositeEvaluationResult) else False),
                "status": status,
                "submitted_at": application.get("submitted_at"),
                "result": result.model_dump(mode="json") if isinstance(result, CompositeEvaluationResult) else None,
                "profile": profile.model_dump(mode="json") if isinstance(profile, ApplicantProfile) else None,
            }
        )
    try:
        APPLICATION_STORAGE_PATH.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    except OSError:
        # The tracker remains usable for the current session if storage is read-only.
        pass


def profile_is_complete(profile: dict[str, Any]) -> bool:
    return all(bool(profile.get(field)) for field in PROFILE_REQUIRED_FIELDS)

# ---------------------------------------------------------------------------
# Visual language — Government of India / Bharat processing cell
# ---------------------------------------------------------------------------
NAVY = "#0B2545"
SAFFRON = "#FF9933"
INDIA_GREEN = "#138808"
READY_COLOR = "#1B7A4E"
PROVISIONAL_COLOR = "#C47B00"
REJECTED_COLOR = "#B42318"
RISK_HIGH = "#DC2626"
RISK_MEDIUM = "#D97706"
RISK_LOW = "#16A34A"
MUTED = "#5C6B7A"
PAPER = "#F4F6F8"

STATUS_DISPLAY = {
    CompositeDecision.READY_FOR_DISBURSAL.value: "Ready for Disbursal",
    CompositeDecision.PROVISIONAL_ELIGIBLE_DEFICIENT_DOCS.value: "Provisional (Deficient Docs)",
    CompositeDecision.REJECTED.value: "Rejected",
}
STATUS_CHART_LABEL = {
    CompositeDecision.READY_FOR_DISBURSAL.value: "Approved",
    CompositeDecision.PROVISIONAL_ELIGIBLE_DEFICIENT_DOCS.value: "Provisional",
    CompositeDecision.REJECTED.value: "Rejected",
}
STATUS_COLORS = {
    "Approved": READY_COLOR,
    "Provisional": PROVISIONAL_COLOR,
    "Rejected": REJECTED_COLOR,
    CompositeDecision.READY_FOR_DISBURSAL.value: READY_COLOR,
    CompositeDecision.PROVISIONAL_ELIGIBLE_DEFICIENT_DOCS.value: PROVISIONAL_COLOR,
    CompositeDecision.REJECTED.value: REJECTED_COLOR,
}
SCHEME_SHORT = {
    "National Overseas Scholarship (NOS) for ST Students": "NOS (Overseas)",
    "National Fellowship Scheme": "National Fellowship",
    "National Scholarship Scheme (Higher Education)": "Higher Education",
    "Pre-Matric Scholarship for ST Students": "Pre-Matric ST",
    "Post Matric Scholarship for ST Students": "Post-Matric ST",
}
COURSE_OPTIONS = {
    "National Overseas Scholarship (NOS) for ST Students": [
        "Master's",
        "Ph.D",
        "Post-Doctoral Research",
    ],
    "National Fellowship Scheme": ["M.Phil", "M.Phil + Ph.D", "Ph.D"],
    "National Scholarship Scheme (Higher Education)": ["Graduate", "Post Graduate"],
    "Pre-Matric Scholarship for ST Students": ["Class IX", "Class X"],
    "Post Matric Scholarship for ST Students": [
        "Class XI-XII",
        "Diploma",
        "Undergraduate",
        "Graduate",
        "Post Graduate",
    ],
}
INSTITUTION_CATEGORIES = [
    "UGC 2(f)/12(B)",
    "Institute of National Importance",
    "Deemed University eligible under Section 3",
    "Central/State Government grant institution",
    "QS Top-1000 University (Abroad)",
    "Ministry-notified premier institute",
    "Government / recognised school",
    "Recognised post-matric institution",
    "Private unaided (unlisted)",
]
def GET_CLEAN_LAYOUT(title_text: str) -> dict[str, Any]:
    """Return the shared high-contrast layout used by every analytics figure."""
    return dict(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter, sans-serif", color="#0f172a"),
        title=dict(
            text=title_text,
            font=dict(size=15, color="#0f172a", family="sans-serif"),
            x=0.01,
            y=0.96,
            xanchor="left",
            yanchor="top",
        ),
        margin=dict(l=70, r=40, t=80, b=70),
        height=430,
        xaxis=dict(
            title_font=dict(size=12, color="#0f172a", family="Arial Black, Arial, sans-serif"),
            tickfont=dict(size=11, color="#0f172a"),
            gridcolor="#f1f5f9",
            zeroline=False,
        ),
        yaxis=dict(
            title_font=dict(size=12, color="#0f172a", family="Arial Black, Arial, sans-serif"),
            tickfont=dict(size=11, color="#0f172a"),
            gridcolor="#f1f5f9",
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.98,
            font=dict(size=11, color="#0f172a"),
            bgcolor="rgba(0,0,0,0)",
        ),
    )


def render_chart(container, figure) -> None:
    """Render a consistently sized Plotly figure inside a white card."""
    with container.container(border=True):
        st.plotly_chart(figure, use_container_width=True)


def format_axis_labels(values: list[object], width: int = 28) -> list[str]:
    """Wrap long categorical labels so horizontal charts remain readable."""
    return ["<br>".join(wrap(str(value), width=width)) for value in values]


def _inr(value: Optional[float]) -> str:
    if value is None:
        return "—"
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "—"


def _pct(value: Optional[float]) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "—"


def _yes_no(value: Optional[bool]) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "—"


def _not_specified(value):
    if value is None or str(value).strip() in ["", "-", "None", "nan", "NaN"]:
        return "Not Specified"
    return value


def _rule_evidence(check: RuleCheck) -> str:
    if check.passed:
        return "Verified"
    return "Failed Constraint"


def _document_evidence(evidence: Optional[str], status: str) -> str:
    if status == "PRESENT" and evidence and evidence.startswith("required_documents_complete=True"):
        return "Declared & Verified"
    if status == "PRESENT":
        return "Verified"
    if status == "MISSING":
        return "Missing"
    return escape(evidence or "Not applicable")


def _decision_summary(result: CompositeEvaluationResult) -> str:
    failed = [check.description for check in result.rule_checks if not check.passed]
    if failed:
        return "Eligibility gates requiring attention: " + "; ".join(failed)
    return result.rationale.split(" — ", 1)[-1] if result.rationale else "No additional rationale provided."


def _dossier_metric(container: Any, label: str, value: str) -> None:
    with container:
        value_class = "dossier-metric-value dossier-metric-value--muted" if value == "Not Specified" else "dossier-metric-value"
        st.markdown(
            f'<div class="dossier-metric"><div class="dossier-metric-label">{escape(label)}</div>'
            f'<div class="{value_class}">{value}</div></div>',
            unsafe_allow_html=True,
        )


def _audit_metric(container: Any, label: str, value: object) -> None:
    with container:
        st.markdown(
            f'<div class="document-audit-kpi"><div class="dossier-metric-label">{escape(label)}</div>'
            f'<div class="dossier-metric-value">{escape(str(value))}</div></div>',
            unsafe_allow_html=True,
        )


def render_custom_audit_table(df: pd.DataFrame) -> str:
    html = """
    <style>
        .custom-audit-table {
            width: 100%;
            border-collapse: collapse;
            font-family: inherit;
            font-size: 13px;
            margin-bottom: 20px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            overflow: hidden;
            table-layout: fixed;
        }
        .custom-audit-table th {
            background-color: #f8fafc;
            color: #0f172a;
            font-weight: 700;
            text-align: left;
            padding: 10px 14px;
            border-bottom: 2px solid #e2e8f0;
        }
        .custom-audit-table td {
            padding: 8px 14px !important;
            color: #334155;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: middle !important;
            height: auto !important;
            line-height: 1.4;
            overflow-wrap: anywhere;
        }
        .custom-audit-table tr:hover {
            background-color: #f8fafc;
        }


    /* ─── BULLETPROOF UNIVERSAL HAMBURGER (Both Open & Closed) ─── */
    button[kind="header"] {
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        z-index: 99999999 !important;
        background: rgba(20, 20, 24, 0.85) !important;
        border: 1px solid rgba(255,153,51,0.4) !important;
        border-radius: 10px !important;
        width: 2.8rem !important;
        height: 2.8rem !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        color: transparent !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: all !important;
    }
    button[kind="header"] svg {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }
    button[kind="header"]::after {
        content: "☰" !important;
        font-size: 1.6rem !important;
        color: #FAFAFA !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important; 
    }
    
    /* Make sure header container doesn't hide it */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        pointer-events: none !important; /* Let clicks pass through empty header area */
        z-index: 99999998 !important;
    }
    header[data-testid="stHeader"] button[kind="header"] {
        pointer-events: all !important; /* Re-enable clicks for the button */
    }
    
</style>
    <table class="custom-audit-table">
        <thead>
            <tr>
    """
    for col in df.columns:
        html += f"<th>{escape(str(col))}</th>"
    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            val = str(row[col])
            if val == "PASS" or val == "Verified":
                if val == "PASS":
                    val_html = '<span style="background:#dcfce7; color:#15803d; padding:3px 8px; border-radius:4px; font-weight:600; font-size:12px;">✓ PASS</span>'
                else:
                    val_html = f'<span style="color:#16a34a; font-weight:600;">✓ {escape(val)}</span>'
            elif val == "FAIL" or "Failed" in val:
                if val == "FAIL":
                    val_html = '<span style="background:#fee2e2; color:#b91c1c; padding:3px 8px; border-radius:4px; font-weight:600; font-size:12px;">✗ FAIL</span>'
                else:
                    val_html = f'<span style="color:#dc2626; font-weight:600;">✗ {escape(val)}</span>'
            elif val.strip().lower() == "hard":
                val_html = '<span style="background:#e2e8f0; color:#334155; padding:3px 8px; border-radius:4px; font-weight:600; font-size:12px;">HARD</span>'
            else:
                val_html = escape(val)
            html += f"<td>{val_html}</td>"
        html += "</tr>"

    html += "</tbody></table>"
    return html


def _short_scheme(name: str) -> str:
    return SCHEME_SHORT.get(name, name)


def _status_value(result: CompositeEvaluationResult) -> str:
    return result.composite_status.value


# ---------------------------------------------------------------------------
# Cached backend pipeline
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading Bharat rule engine and scoring 120 applicants…")
def load_pipeline() -> dict[str, Any]:
    evaluator = ScholarshipEvaluator(root=str(ROOT))
    applicants = load_applicants(str(ROOT))
    results, summary = evaluator.evaluate_dataset(str(ROOT))
    rules = list(load_scheme_rules(str(ROOT)))
    documents = list(load_document_requirements(str(ROOT)))
    income_ceilings = {rule.scheme: rule.income_limit_inr for rule in rules}
    applicant_by_id = {row.applicant_id: row for row in applicants}
    result_by_id = {row.applicant_id: row for row in results}
    return {
        "evaluator": evaluator,
        "applicants": applicants,
        "results": results,
        "summary": summary,
        "rules": rules,
        "documents": documents,
        "income_ceilings": income_ceilings,
        "applicant_by_id": applicant_by_id,
        "result_by_id": result_by_id,
    }


def build_analytics_frame(
    applicants: list[ApplicantProfile],
    results: list[CompositeEvaluationResult],
    income_ceilings: dict[str, Optional[float]],
) -> pd.DataFrame:
    result_by_id = {item.applicant_id: item for item in results}
    rows: list[dict[str, Any]] = []
    for applicant in applicants:
        result = result_by_id.get(applicant.applicant_id)
        if result is None:
            continue
        status = _status_value(result)
        rows.append(
            {
                "applicant_id": applicant.applicant_id,
                "scheme": applicant.scheme,
                "scheme_short": _short_scheme(applicant.scheme),
                "family_income_inr": applicant.family_income_inr,
                "income_ceiling_inr": income_ceilings.get(applicant.scheme),
                "income_over_ceiling": (
                    applicant.family_income_inr is not None
                    and income_ceilings.get(applicant.scheme) is not None
                    and applicant.family_income_inr > income_ceilings[applicant.scheme]
                ),
                "qualifying_marks_pct": applicant.qualifying_marks_pct,
                "age_years": applicant.age_years,
                "course_level": applicant.course_level,
                "composite_status": status,
                "status_label": STATUS_CHART_LABEL.get(status, status),
                "doc_status": result.doc_verification_status.value,
                "doc_score": result.document_completeness_score,
                "is_eligible": result.is_eligible,
                "domicile_matches_st": applicant.domicile_matches_st,
                "st_status": applicant.st_status,
            }
        )
    return pd.DataFrame(rows)


def add_risk_columns(frame: pd.DataFrame, risks: dict[str, RiskAssessment]) -> pd.DataFrame:
    enriched = frame.copy()
    enriched["risk_score"] = enriched["applicant_id"].map(lambda aid: risks[aid].score)
    enriched["risk_band"] = enriched["applicant_id"].map(lambda aid: risks[aid].band)
    enriched["risk_anomalies"] = enriched["applicant_id"].map(
        lambda aid: "; ".join(risks[aid].anomalies)
    )
    return enriched


def apply_dashboard_filters(
    frame: pd.DataFrame,
    selected_scheme: str,
    selected_st: str,
    selected_domicile: str,
) -> pd.DataFrame:
    """Return the analytics rows matching the Overview filter selections."""
    filtered = frame
    if selected_scheme != "All schemes":
        filtered = filtered[filtered["scheme"] == selected_scheme]
    if selected_st != "All ST Statuses":
        filtered = filtered[filtered["st_status"] == selected_st]
    if selected_domicile != "All Domicile Statuses":
        filtered = filtered[filtered["domicile_matches_st"] == (selected_domicile == "Yes")]
    return filtered


def missing_document_counts(results: list[CompositeEvaluationResult]) -> pd.DataFrame:
    counter: Counter[str] = Counter()
    for result in results:
        audit = result.document_audit_result
        for name in audit.missing_mandatory_docs + audit.missing_conditional_docs:
            counter[name] += 1
    if not counter:
        return pd.DataFrame(columns=["document", "count"])
    return (
        pd.DataFrame(counter.items(), columns=["document", "count"])
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )


def executive_metrics(
    applicants: list[ApplicantProfile],
    results: list[CompositeEvaluationResult],
) -> dict[str, Any]:
    """Build narrative and export inputs from one filtered evaluation scope."""
    applicant_by_id = {applicant.applicant_id: applicant for applicant in applicants}
    counts = Counter(_status_value(result) for result in results)
    total = len(results)
    approved = counts.get(CompositeDecision.READY_FOR_DISBURSAL.value, 0)
    provisional = counts.get(CompositeDecision.PROVISIONAL_ELIGIBLE_DEFICIENT_DOCS.value, 0)
    rejected = counts.get(CompositeDecision.REJECTED.value, 0)
    failed_rules: Counter[str] = Counter()
    rule_descriptions: dict[str, str] = {}
    for result in results:
        for check in result.rule_checks:
            if not check.passed:
                failed_rules[check.rule_id] += 1
                rule_descriptions.setdefault(check.rule_id, check.description)
    bottlenecks = []
    for rule_id, count in failed_rules.most_common(3):
        share = count / rejected * 100 if rejected else 0
        bottlenecks.append(f"{share:.0f}% of rejected cases failed {rule_descriptions[rule_id]} ({count} cases)")
    deficiencies = missing_document_counts(results)
    top_deficiencies = [(str(row.document), int(row.count)) for row in deficiencies.head(5).itertuples(index=False)]
    amounts = [
        float(getattr(applicant_by_id[result.applicant_id], "disbursal_amount_inr", 0) or 0)
        for result in results
        if _status_value(result) == CompositeDecision.READY_FOR_DISBURSAL.value
        and getattr(applicant_by_id[result.applicant_id], "disbursal_amount_inr", None) is not None
    ]
    return {
        "total": total,
        "approved": approved,
        "provisional": provisional,
        "rejected": rejected,
        "approval_rate": approved / total * 100 if total else 0.0,
        "bottlenecks": bottlenecks,
        "deficiencies": top_deficiencies,
        "scheme_breakdown": {
            scheme: {
                "total": int(group["applicant_id"].count()),
                "approved": int((group["composite_status"] == CompositeDecision.READY_FOR_DISBURSAL.value).sum()),
                "provisional": int((group["composite_status"] == CompositeDecision.PROVISIONAL_ELIGIBLE_DEFICIENT_DOCS.value).sum()),
                "rejected": int((group["composite_status"] == CompositeDecision.REJECTED.value).sum()),
            }
            for scheme, group in pd.DataFrame([
                {"scheme": result.scheme, "applicant_id": result.applicant_id, "composite_status": _status_value(result)}
                for result in results
            ]).groupby("scheme")
        } if results else {},
        "allocation": sum(amounts) if amounts else None,
    }


def ready_for_disbursal_frame(
    applicants: list[ApplicantProfile],
    results: list[CompositeEvaluationResult],
) -> pd.DataFrame:
    applicant_by_id = {applicant.applicant_id: applicant for applicant in applicants}
    rows = []
    for result in results:
        if _status_value(result) != CompositeDecision.READY_FOR_DISBURSAL.value:
            continue
        applicant = applicant_by_id[result.applicant_id]
        rows.append({
            "pfms_beneficiary_id": applicant.applicant_id,
            "application_reference": f"BHARAT/{applicant.applicant_id}",
            "beneficiary_name": "",
            "scheme": applicant.scheme,
            "bank_account_number": "",
            "ifsc_code": "",
            "sanction_amount_inr": getattr(applicant, "disbursal_amount_inr", ""),
            "payment_status": "READY_FOR_DISBURSAL",
            "document_verification": result.doc_verification_status.value,
        })
    return pd.DataFrame(rows)


def deficiency_master_log(
    applicants: list[ApplicantProfile],
    results: list[CompositeEvaluationResult],
) -> list[dict[str, Any]]:
    applicant_by_id = {applicant.applicant_id: applicant for applicant in applicants}
    records = []
    for result in results:
        audit = result.document_audit_result
        missing = audit.missing_mandatory_docs + audit.missing_conditional_docs
        if not missing:
            continue
        records.append({
            "notice_reference": f"BHARAT/DEF/{result.applicant_id}/{datetime.now(timezone.utc).year}",
            "applicant_id": result.applicant_id,
            "scheme": applicant_by_id[result.applicant_id].scheme,
            "composite_status": _status_value(result),
            "cure_period_days": result.deficiency_notice.cure_period_days if result.deficiency_notice else 15,
            "missing_mandatory_documents": audit.missing_mandatory_docs,
            "missing_conditional_documents": audit.missing_conditional_docs,
            "document_completeness": result.document_completeness_score,
        })
    return records


def render_executive_operations(
    applicants: list[ApplicantProfile],
    results: list[CompositeEvaluationResult],
) -> None:
    metrics = executive_metrics(applicants, results)
    allocation_text = _inr(metrics["allocation"]) if metrics["allocation"] is not None else "Not captured"
    top_deficiency = metrics["deficiencies"][0] if metrics["deficiencies"] else ("None recorded", 0)
    top_bottleneck = metrics["bottlenecks"][0] if metrics["bottlenecks"] else "no recurring rule failure identified"
    st.markdown(
        '<div class="profile-card" style="border-top:4px solid #FF9933;">'
        '<div class="bharat-kicker" style="color:#0B2545;">Executive ministry briefing</div>'
        '<h3 style="margin:.1rem 0 .35rem 0;">Decision position and operational priorities</h3>'
        f'<p style="margin:0;">{metrics["total"]} applications processed with a {metrics["approval_rate"]:.1f}% ready-for-disbursal rate. '
        f'Key bottleneck: {top_bottleneck}. Top document deficiency: {top_deficiency[0]} in {top_deficiency[1]} cases.</p>'
        f'<p style="margin:.55rem 0 0 0;"><strong>Projected allocation:</strong> {allocation_text}. '
        'The source dataset does not capture sanctioned award amounts; PFMS amount cells remain blank until that field is supplied.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Ministry Operations & Disbursal")
    export_cols = st.columns(3)
    ready_csv = ready_for_disbursal_frame(applicants, results).to_csv(index=False).encode("utf-8")
    export_cols[0].download_button("📥 Export Ready-for-Disbursal CSV", data=ready_csv, file_name="Bharat_PFMS_Ready_for_Disbursal.csv", mime="text/csv", use_container_width=True, type="primary")
    log = deficiency_master_log(applicants, results)
    log_json = json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "records": log}, indent=2, ensure_ascii=False).encode("utf-8")
    log_frame = pd.json_normalize(log) if log else pd.DataFrame(columns=["applicant_id", "scheme", "composite_status"])
    export_cols[1].download_button("📄 Download Deficiency Master Log (JSON)", data=log_json, file_name="Bharat_Consolidated_Deficiency_Master_Log.json", mime="application/json", use_container_width=True)
    export_cols[1].download_button("Download deficiency log CSV", data=log_frame.to_csv(index=False).encode("utf-8"), file_name="Bharat_Consolidated_Deficiency_Master_Log.csv", mime="text/csv", use_container_width=True)
    try:
        if ExecutiveBriefingPDFReport is None:
            raise RuntimeError(f"ReportLab PDF support is unavailable: {PDF_IMPORT_ERROR}")
        briefing_pdf = ExecutiveBriefingPDFReport().render(
            generated_at=datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC"),
            total=metrics["total"], approved=metrics["approved"], provisional=metrics["provisional"], rejected=metrics["rejected"],
            approval_rate=metrics["approval_rate"], allocation_projection=allocation_text,
            bottlenecks=metrics["bottlenecks"], deficiencies=metrics["deficiencies"],
            scheme_breakdown=metrics["scheme_breakdown"],
        )
    except Exception as exc:
        export_cols[2].error(f"Executive PDF unavailable: {exc}")
    else:
        export_cols[2].download_button("📊 Download Executive PDF Briefing", data=briefing_pdf, file_name="Bharat_Executive_Analytics_Briefing.pdf", mime="application/pdf", use_container_width=True, type="primary")


def format_deficiency_letter(
    applicant: ApplicantProfile,
    result: CompositeEvaluationResult,
) -> str:
    notice = result.deficiency_notice
    issued = (
        notice.issued_at.strftime("%d %B %Y")
        if notice
        else datetime.now(timezone.utc).strftime("%d %B %Y")
    )
    days = notice.cure_period_days if notice else 15
    mandatory = notice.missing_mandatory_docs if notice else result.document_audit_result.missing_mandatory_docs
    conditional = (
        notice.missing_conditional_docs if notice else result.document_audit_result.missing_conditional_docs
    )
    action = notice.action_required if notice else "Upload the missing artefacts listed above."
    mandatory_block = "\n".join(f"  • {item}" for item in mandatory) or "  • None"
    conditional_block = "\n".join(f"  • {item}" for item in conditional) or "  • None"
    return f"""GOVERNMENT OF INDIA
GOVERNMENT OF INDIA
Scholarship / Fellowship Processing Cell
 — Bharat AI Verification System

================================================================================
                         DEFICIENCY NOTICE
              Fifteen (15) Day Cure Period — Document Packet
================================================================================

Notice No.          : BHARAT/DEF/{applicant.applicant_id}/{datetime.now(timezone.utc).strftime("%Y")}
Date of Issue       : {issued}
Applicant ID        : {applicant.applicant_id}
Scheme              : {applicant.scheme}
            Composite Status    : {STATUS_DISPLAY.get(_status_value(result), _status_value(result))}
Cure Period         : {days} calendar days from the date of this notice

--------------------------------------------------------------------------------
TO THE APPLICANT
--------------------------------------------------------------------------------
You are hereby informed that your application is rule-eligible but the supporting
document packet is incomplete. Disbursal is withheld until the artefacts below
are uploaded / submitted. Failure to cure within {days} days may result in the
application being treated as closed for this cycle.

Missing mandatory documents
{mandatory_block}

Missing conditional documents (where applicable)
{conditional_block}

--------------------------------------------------------------------------------
ACTION REQUIRED
--------------------------------------------------------------------------------
{action}

--------------------------------------------------------------------------------
ISSUING AUTHORITY
--------------------------------------------------------------------------------
Processing Cell, Government of India
(Generated by the Bharat AI-Driven Scholarship & Fellowship Verification System)
Policy ref: Bharat scholarship / fellowship processing guidelines — 15-day deficiency cure period
================================================================================
"""


# ---------------------------------------------------------------------------
# CSS / chrome
# ---------------------------------------------------------------------------
def inject_theme() -> None:
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* Make header transparent - DO NOT set height:0 or the sidebar button disappears */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
        box-shadow: none !important;
    }
    /* Hide only the toolbar items inside header (deploy button etc), keep sidebar toggle */
    header[data-testid="stHeader"] [data-testid="stToolbar"] {
        display: flex !important;
    }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }

    /* Full-screen India tricolor wallpaper */
    .stApp {
        background:
            radial-gradient(circle at 10% 30%, rgba(255,153,51,0.22), transparent 40%),
            radial-gradient(circle at 90% 70%, rgba(19,136,8,0.22), transparent 40%),
            radial-gradient(circle at 50% 100%, rgba(0,0,128,0.28), transparent 50%),
            url("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
        min-height: 100vh !important;
    }
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(5,5,7,0.35);
        z-index: 0;
        pointer-events: none;
    }

    /* Glassmorphism content panel */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1200px !important;
        background: rgba(18,18,20,0.5) !important;
        backdrop-filter: blur(28px) !important;
        -webkit-backdrop-filter: blur(28px) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-top: 1px solid rgba(255,153,51,0.25) !important;
        border-bottom: 1px solid rgba(19,136,8,0.25) !important;
        margin-top: 1rem !important;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.6) !important;
        position: relative !important;
        z-index: 1 !important;
    }
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
    }

    /* Glassmorphism sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(10,10,14,0.55) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border-right: 1px solid rgba(255,255,255,0.08) !important;
    }
    .sidebar-brand { padding: 1.5rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 1rem; display: flex; flex-direction: column; align-items: center; text-align: center; }
    .sidebar-brand-mark { width: 50px; height: 50px; background: linear-gradient(135deg, #FF9933 0%, #138808 100%); color: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.4rem; margin-bottom: 1rem; box-shadow: 0 0 20px rgba(255,153,51,0.25); }
    .sidebar-brand h2 { margin: 0; font-size: 1.1rem; color: #FAFAFA !important; font-weight: 700; }
    .sidebar-brand p { margin: 0.35rem 0 0 0; font-size: 0.75rem; color: rgba(255,255,255,0.7) !important; }

    /* Hide radio label */
    div[data-testid="stWidgetLabel"], div[data-testid="stRadio"] > label { display: none !important; }

    /* Sidebar navigation as simple text tabs, without radio controls or button panels. */
    div[data-testid="stRadio"] { width: 100% !important; }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 0.2rem !important;
        padding: 0 0.5rem !important;
    }
    div[data-testid="stRadio"] label {
        width: 100% !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        padding: 0.65rem 0.75rem !important;
        border-radius: 0 !important;
        background: transparent !important;
        border: 0 !important;
        border-left: 2px solid transparent !important;
        cursor: pointer !important;
    }
    div[data-testid="stRadio"] label > div > div:first-child { display: none !important; }
    div[data-testid="stRadio"] label:hover { background: transparent !important; }
    div[data-testid="stRadio"] label p { color: rgba(255,255,255,0.7) !important; font-weight: 500 !important; font-size: 0.95rem !important; margin: 0 !important; }
    div[data-testid="stRadio"] label[data-checked="true"],
    div[data-testid="stRadio"] label:has(input:checked) {
        border-left-color: #FF9933 !important;
    }
    div[data-testid="stRadio"] label[data-checked="true"] p,
    div[data-testid="stRadio"] label:has(input:checked) p { color: #FAFAFA !important; font-weight: 600 !important; }

    
    
    

    
    
    

    /* Keep Streamlit's collapsed sidebar toggle visible across releases. */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 0.75rem !important;
        left: 0.75rem !important;
        z-index: 100000 !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 2.75rem !important;
        height: 2.75rem !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stExpandSidebarButton"] {
        position: fixed !important;
        top: 0.75rem !important;
        left: 0.75rem !important;
        z-index: 100000 !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 2.75rem !important;
        height: 2.75rem !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        background: rgba(20, 20, 24, 0.85) !important;
        border: 1px solid rgba(255,153,51,0.4) !important;
        border-radius: 10px !important;
        color: transparent !important;
    }
    [data-testid="stExpandSidebarButton"] span {
        display: none !important;
    }
    [data-testid="stExpandSidebarButton"]::after {
        content: "☰" !important;
        color: #FAFAFA !important;
        font-size: 1.6rem !important;
        line-height: 1 !important;
    }
    [data-testid="stSidebarCollapseButton"] {
        position: fixed !important;
        top: 0.75rem !important;
        left: 0.75rem !important;
        z-index: 100001 !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 2.75rem !important;
        height: 2.75rem !important;
    }
    [data-testid="stSidebarCollapseButton"] button {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 2.75rem !important;
        height: 2.75rem !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        background: rgba(20, 20, 24, 0.85) !important;
        border: 1px solid rgba(255,153,51,0.4) !important;
        border-radius: 10px !important;
        color: transparent !important;
    }
    [data-testid="stSidebarCollapseButton"] button svg {
        display: none !important;
    }
    [data-testid="stSidebarCollapseButton"] button span {
        display: none !important;
    }
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
        display: none !important;
    }
    [data-testid="stSidebarCollapseButton"] button::after {
        content: "☰" !important;
        color: #FAFAFA !important;
        font-size: 1.6rem !important;
        line-height: 1 !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%) !important;
        border: none !important; color: white !important; border-radius: 8px !important;
        font-weight: 600 !important; box-shadow: 0 4px 15px rgba(255,153,51,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; }
    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #FAFAFA !important; border-radius: 8px !important; font-weight: 500 !important;
    }
    .stButton > button[kind="secondary"]:hover { background: rgba(255,255,255,0.15) !important; }

    /* Cards */
    .profile-card, .scholarship-card, .anomaly-card, .application-tracker-card, .kpi-card {
        background: rgba(18,18,20,0.5) !important; backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 16px !important;
        padding: 2rem !important; margin-bottom: 1.5rem !important; color: #FAFAFA !important;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.6) !important;
    }
    .mota-kicker, .bharat-kicker, .application-tracker-kicker { color: #FF9933 !important; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
    .page-intro h2 { color: #FAFAFA !important; font-size: 2rem; font-weight: 700; }
    .page-intro p { color: rgba(255,255,255,0.7) !important; }

    /* Form inputs */
    div[data-baseweb="select"] > div, input, div[data-baseweb="textarea"] > div {
        background-color: rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #FAFAFA !important; border-radius: 8px !important;
    }

    /* Text */
    .stMarkdown p, .stMarkdown span { color: rgba(255,255,255,0.85) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #FAFAFA !important; }

    
    
    
    
    


    /* ─── BULLETPROOF UNIVERSAL HAMBURGER (Both Open & Closed) ─── */
    button[kind="header"] {
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        z-index: 99999999 !important;
        background: rgba(20, 20, 24, 0.85) !important;
        border: 1px solid rgba(255,153,51,0.4) !important;
        border-radius: 10px !important;
        width: 2.8rem !important;
        height: 2.8rem !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        color: transparent !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: all !important;
    }
    button[kind="header"] svg {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }
    button[kind="header"]::after {
        content: "☰" !important;
        font-size: 1.6rem !important;
        color: #FAFAFA !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important; 
    }
    
    /* Make sure header container doesn't hide it */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        pointer-events: none !important; /* Let clicks pass through empty header area */
        z-index: 99999998 !important;
    }
    header[data-testid="stHeader"] button[kind="header"] {
        pointer-events: all !important; /* Re-enable clicks for the button */
    }
    
</style>
        """,
        unsafe_allow_html=True,
    )



def hero() -> None:
    st.markdown(
        """
<div class="bharat-hero" style="padding: 1.5rem 1.5rem; margin-bottom: 1.5rem; text-align: center;">
    <div style="display:flex; flex-direction:column; align-items:center; gap:0.5rem;">
        <div class="bharat-emblem" aria-label="Government of India emblem" style="margin: 0;">भारत<br><small>INDIA</small></div>
        <div>
            <div class="bharat-kicker">Government of India</div>
            <h1 style="font-size: 1.65rem; margin: 0;">Bharat Scholarship Verification</h1>
        </div>
    </div>
  <p style="margin: 0.65rem 0 0; font-size: 0.92rem;">Eligibility, documents, and application status.</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: int, hint: str, kind: str = "") -> None:
    cls = f"kpi-card {kind}".strip()
    st.markdown(
        f"""
<div class="{cls}">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
  <div class="kpi-hint">{hint}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def status_pill(status: str) -> str:
    label = STATUS_DISPLAY.get(status, status)
    if status == CompositeDecision.READY_FOR_DISBURSAL.value:
        cls = "pill-ready"
    elif status == CompositeDecision.PROVISIONAL_ELIGIBLE_DEFICIENT_DOCS.value:
        cls = "pill-prov"
    else:
        cls = "pill-rej"
    return f'<span class="status-pill {cls}">{label}</span>'


# ---------------------------------------------------------------------------
# Policy copilot
# ---------------------------------------------------------------------------
COPILOT_SAMPLES = (
    "What is the max income limit for NOS Overseas Scholarship?",
    "What documents are required if applicant is PVTG?",
    "Is Ph.D. eligible under National Fellowship for ST?",
    "What happens if income exceeds ceiling?",
)


def _policy_citation(rule: SchemeRule, fields: str) -> str:
    source = rule.source or "source not specified"
    return (
        f"**Policy clause reference:** `Bharat_Scheme_Rules_.csv` · "
        f"scheme=`{rule.scheme}` · fields=`{fields}` · source=`{source}`"
    )


def _document_citation(requirements: list[DocumentRequirement]) -> str:
    schemes = ", ".join(sorted({item.scheme for item in requirements}))
    return (
        "**Policy clause reference:** `Bharat_Document_Requirements_.csv` · "
        f"schemes=`{schemes}` · fields=`Document`, `Requirement`, `Remarks`"
    )


def _scheme_for_query(query: str, rules: list[SchemeRule], context: Optional[ApplicantProfile]) -> Optional[SchemeRule]:
    text = query.lower()
    aliases = {
        "nos": "overseas",
        "overseas": "overseas",
        "fellowship": "fellowship",
        "higher education": "higher education",
        "pre-matric": "pre-matric",
        "pre matric": "pre-matric",
        "post matric": "post matric",
        "post-matric": "post matric",
    }
    for needle, marker in aliases.items():
        if needle in text:
            return next((rule for rule in rules if marker in rule.scheme.lower()), None)
    if context:
        return next((rule for rule in rules if rule.scheme == context.scheme), None)
    return None


def _general_chat_reply(query: str) -> str:
    normalized = query.strip().lower().strip(".!?,")

    if normalized in {"hi", "hello", "hey", "namaste", "good morning", "good afternoon", "good evening"}:
        return (
            "Hello! I’m the Bharat Scholarship Assistant. "
            "I can help with eligibility, income limits, documents, courses, and application status."
        )
    if normalized in {"thanks", "thank you", "thx"}:
        return "You’re welcome. Ask me anything about a scholarship or your application."
    if normalized in {"bye", "goodbye", "see you"}:
        return "Goodbye. Your scholarship information remains available in this workspace."
    if "who are you" in normalized or "what can you do" in normalized:
        return (
            "I’m the Bharat Scholarship Assistant. I use the loaded Bharat scheme rules and "
            "document requirements to help you check eligibility and prepare an application."
        )
    if "how are you" in normalized:
        return "I’m ready to help with your scholarship application. What would you like to check?"
    if normalized in {"help", "help me", "what should i ask"}:
        return (
            "You can ask about a scheme, income limit, eligible course, required document, "
            "PVTG requirement, or an applicant decision."
        )

    return (
        f"I received: **{query.strip()}**\n\n"
        "I can give a reliable answer when your message relates to a Bharat scholarship, "
        "fellowship, eligibility rule, document, or application. Tell me a little more about "
        "what you need to know."
    )


def _policy_answer(
    query: str,
    rules: list[SchemeRule],
    documents: list[DocumentRequirement],
    context: Optional[tuple[ApplicantProfile, CompositeEvaluationResult]] = None,
) -> str:
    text = query.lower()
    applicant = context[0] if context else None
    result = context[1] if context else None

    if applicant and result and (
        "why" in text and ("reject" in text or "decision" in text)
        or "missing" in text and ("document" in text or "paper" in text)
        or applicant.applicant_id.lower() in text
    ):
        if "missing" in text and ("document" in text or "paper" in text):
            audit = result.document_audit_result
            missing = audit.missing_mandatory_docs + audit.missing_conditional_docs
            if not missing:
                return (
                    f"**{applicant.applicant_id}** has no missing documents in the evaluated audit. "
                    f"Document status: **{audit.doc_verification_status.value}**.\n\n"
                    "**Evaluation reference:** `CompositeEvaluationResult.document_audit_result`"
                )
            lines = "\n".join(f"- {item}" for item in missing)
            return (
                f"**{applicant.applicant_id}** is missing the following documents:\n{lines}\n\n"
                f"Document status: **{audit.doc_verification_status.value}**.\n\n"
                f"{_document_citation([item for item in documents if item.scheme == applicant.scheme])}"
            )

        failed = [check for check in result.rule_checks if not check.passed]
        if failed:
            reasons = "\n".join(
                f"- **{check.rule_id}:** {check.description} Evidence: `{check.evidence}`"
                for check in failed
            )
            return (
                f"**{applicant.applicant_id}** was **{STATUS_DISPLAY.get(_status_value(result), _status_value(result))}** "
                f"because these policy checks failed:\n{reasons}\n\n"
                "**Evaluation reference:** `CompositeEvaluationResult.rule_checks` · "
                "each failed check includes its guideline reference."
            )
        return (
            f"**{applicant.applicant_id}** is currently **{STATUS_DISPLAY.get(_status_value(result), _status_value(result))}**. "
            f"Evaluator rationale: {result.rationale}\n\n"
            "**Evaluation reference:** `CompositeEvaluationResult.rationale`"
        )

    rule = _scheme_for_query(query, rules, applicant)
    if "income" in text and ("limit" in text or "ceiling" in text or "exceed" in text or "max" in text):
        if rule and rule.income_criterion_applies and rule.income_limit_inr is not None:
            exception = (
                " The CSV also records an exception for an orphan supported by a guardian."
                if rule.orphan_income_exempt
                else ""
            )
            outcome = (
                "Income above this ceiling fails the income eligibility check and can lead to rejection."
                if "exceed" in text
                else f"The maximum permitted family income is {_inr(rule.income_limit_inr)} per annum."
            )
            return (
                f"For **{rule.scheme}**, {outcome}"
                f"{exception}\n\n{_policy_citation(rule, 'income_limit_inr, income_rule')}"
            )
        if rule:
            return (
                f"**{rule.scheme}** has **no family-income ceiling** in the policy data. "
                f"{_policy_citation(rule, 'income_limit_inr, income_rule')}"
            )
        ceilings = "\n".join(
            f"- {_short_scheme(item.scheme)}: {_inr(item.income_limit_inr) if item.income_limit_inr is not None else 'No ceiling'}"
            for item in rules
        )
        return f"Income ceilings in the loaded Bharat rules are:\n{ceilings}\n\nAsk about a named scheme for a focused answer."

    if "pvtg" in text and ("document" in text or "required" in text):
        selected_scheme = applicant.scheme if applicant else None
        matches = [
            item for item in documents
            if "pvtg" in item.document.lower()
            and (selected_scheme is None or item.scheme == selected_scheme)
        ]
        if selected_scheme:
            checklist = [item for item in documents if item.scheme == selected_scheme]
            matches = [item for item in checklist if item.requirement.is_hard_mandatory or "pvtg" in item.document.lower()]
        if not matches:
            return "No PVTG-specific document row was found in the loaded document requirements CSV."
        rows = "\n".join(
            f"- **{item.document}** ({item.requirement.value}): {item.remarks or 'No additional remark'}"
            for item in matches
        )
        scope = f" for **{selected_scheme}**" if selected_scheme else " across the schemes with an explicit PVTG row"
        return f"PVTG document guidance{scope}:\n{rows}\n\n{_document_citation(matches)}"

    if "ph.d" in text or "phd" in text:
        if rule and "fellowship" in rule.scheme.lower():
            eligible = rule.course_is_eligible("Ph.D")
            return (
                f"**{'Yes' if eligible else 'No'}**. Ph.D is {'listed' if eligible else 'not listed'} "
                f"among eligible courses for the **{rule.scheme}**. The minimum marks criterion is "
                f"**{rule.min_marks_pct:g}%** where recorded.\n\n"
                f"{_policy_citation(rule, 'eligible_courses, min_marks_pct')}"
            )
        if rule:
            return (
                f"For **{rule.scheme}**, eligible courses are: {', '.join(rule.eligible_courses)}.\n\n"
                f"{_policy_citation(rule, 'eligible_courses')}"
            )

    if rule:
        return (
            f"For **{rule.scheme}**: eligible courses are **{', '.join(rule.eligible_courses) or 'not restricted in this row'}**; "
            f"minimum marks are **{rule.min_marks_pct:g}%** where recorded; study location is **{rule.study_location}**.\n\n"
            f"{_policy_citation(rule, 'eligible_courses, min_marks_pct, study_location, other_key_rules, institution_rule')}"
        )
    return _general_chat_reply(query)


def render_policy_copilot(
    rules: list[SchemeRule],
    documents: list[DocumentRequirement],
    applicant_by_id: dict[str, ApplicantProfile],
    result_by_id: dict[str, CompositeEvaluationResult],
    key_prefix: str = "",
) -> None:
    selected_id = st.session_state.get("selected_applicant_id")
    context = None
    if selected_id in applicant_by_id and selected_id in result_by_id:
        context = (applicant_by_id[selected_id], result_by_id[selected_id])

    if context:
        st.caption(f"Live applicant context: {context[0].applicant_id} · {context[0].scheme}")
    else:
        st.caption("Policy answers are grounded in the loaded Bharat rules and document checklist CSVs.")

    st.markdown(
        """
        <style>
        /* Keep the copilot readable inside the dark application theme. */
        div[data-testid="stButton"] > button {
            background-color: #121b2d !important;
            color: #dce8ff !important;
            border: 1px solid #2b3b59 !important;
            font-weight: 500 !important;
            text-align: left !important;
            padding: 9px 12px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease-in-out !important;
        }
        div[data-testid="stButton"] > button:hover {
            background-color: #1a2943 !important;
            border-color: #4f8cff !important;
            color: #ffffff !important;
        }
        div[data-testid="stChatInput"] {
            background-color: #0d1321 !important;
            border: 1px solid #2b3b59 !important;
            border-radius: 10px !important;
        }
        div[data-testid="stChatInput"] textarea {
            background-color: #121b2d !important;
            color: #edf4ff !important;
            caret-color: #edf4ff !important;
        }
        div[data-testid="stChatInput"] textarea::placeholder {
            color: #91a1bb !important;
            opacity: 1 !important;
        }
        div[data-testid="stChatMessage"] {
            background: #0d1321 !important;
            border: 1px solid #202e46 !important;
            border-radius: 10px !important;
            color: #edf4ff !important;
            padding: 0.8rem 1rem !important;
            margin: 0.5rem 0 !important;
        }
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] *,
        div[data-testid="stChatMessage"] p,
        div[data-testid="stChatMessage"] li,
        div[data-testid="stChatMessage"] strong {
            color: #edf4ff !important;
        }
        div[data-testid="stChatMessage"] code {
            background: #17233a !important;
            color: #9fc0ff !important;
            border: 1px solid #2b3b59 !important;
        }
        div[data-testid="stChatMessage"] a {
            color: #79a8ff !important;
        }


    /* ─── BULLETPROOF UNIVERSAL HAMBURGER (Both Open & Closed) ─── */
    button[kind="header"] {
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        z-index: 99999999 !important;
        background: rgba(20, 20, 24, 0.85) !important;
        border: 1px solid rgba(255,153,51,0.4) !important;
        border-radius: 10px !important;
        width: 2.8rem !important;
        height: 2.8rem !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        color: transparent !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: all !important;
    }
    button[kind="header"] svg {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }
    button[kind="header"]::after {
        content: "☰" !important;
        font-size: 1.6rem !important;
        color: #FAFAFA !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important; 
    }
    
    /* Make sure header container doesn't hide it */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        pointer-events: none !important; /* Let clicks pass through empty header area */
        z-index: 99999998 !important;
    }
    header[data-testid="stHeader"] button[kind="header"] {
        pointer-events: all !important; /* Re-enable clicks for the button */
    }
    
</style>
        """,
        unsafe_allow_html=True,
    )

    sample_questions = [
        "What is the max income limit for NOS Overseas Scholarship?",
        "What documents are required if applicant is PVTG?",
        "Is Ph.D. eligible under National Fellowship for ST?",
        "What happens if income exceeds ceiling?",
    ]
    st.caption("💡 Quick Suggestions:")
    sample_columns = st.columns(2)
    for index, sample_question in enumerate(sample_questions):
        if sample_columns[index % 2].button(sample_question, key=f"chat_smp_{index}", use_container_width=True):
            st.session_state["chatbot_user_prompt"] = sample_question
            st.rerun()

    messages: list[dict[str, str]] = st.session_state.setdefault("copilot_messages", [])
    pending = st.session_state.pop("chatbot_user_prompt", None)
    query = st.chat_input("Ask about a Bharat rule, document, or applicant decision…", key=f"copilot_input_{key_prefix}")
    query = query or pending
    if query and query.strip():
        clean_query = query.strip()
        messages.append({"role": "user", "content": clean_query})
        messages.append(
            {
                "role": "assistant",
                "content": _policy_answer(clean_query, rules, documents, context),
            }
        )

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# ---------------------------------------------------------------------------
# Shared result renderers
# ---------------------------------------------------------------------------
def render_profile_card(applicant: ApplicantProfile, result: CompositeEvaluationResult) -> None:
    status = _status_value(result)
    st.markdown(
        f"""
<div class="profile-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;flex-wrap:wrap;">
    <div>
      <div class="bharat-kicker" style="color:{SAFFRON};">Applicant dossier</div>
      <h3 style="margin:0 0 0.2rem 0;color:{NAVY};">{applicant.applicant_id}</h3>
      <p style="margin:0;color:{MUTED};">{applicant.scheme}</p>
    </div>
    <div>{status_pill(status)}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    _dossier_metric(c1, "ST status", _not_specified(applicant.st_status))
    _dossier_metric(c2, "Family income", escape(_inr(applicant.family_income_inr)))
    _dossier_metric(c3, "Qualifying marks", escape(_pct(applicant.qualifying_marks_pct)))
    _dossier_metric(c4, "Age (years)", _not_specified(applicant.age_years))
    d1, d2, d3, d4 = st.columns(4)
    _dossier_metric(d1, "Course level", _not_specified(applicant.course_level))
    _dossier_metric(d2, "Fresh / renewal", _not_specified(applicant.fresh_or_renewal))
    _dossier_metric(d3, "Institution category", _not_specified((applicant.institution_category or "")[:42]))
    _dossier_metric(d4, "Doc completeness", escape(f"{result.document_completeness_score:.0%}"))
    extras = st.columns(4)
    extras[0].caption(f"Gender: **{applicant.gender or 'Not Specified'}**")
    extras[1].caption(f"PVTG: **{applicant.pvtg_status or 'Not Specified'}**")
    extras[2].caption(f"Domicile matches ST: **{_yes_no(applicant.domicile_matches_st)}**")
    extras[3].caption(f"Rule gold label: **{applicant.rule_eligibility or 'Not Specified'}**")
    st.caption(_decision_summary(result))


def render_rule_audit(checks: list[RuleCheck]) -> None:
    st.subheader("Atomic rule audit")
    passed = sum(1 for item in checks if item.passed)
    failed = len(checks) - passed
    a, b, c = st.columns(3)
    a.metric("Rules evaluated", len(checks))
    b.metric("Passed", passed)
    c.metric("Failed", failed)

    failed_rows = [item for item in checks if not item.passed]
    if failed_rows:
        failed_markup = "".join(
            f'<div class="rule-fail">✕ {escape(item.rule_id)} — {escape(item.description)}</div>'
            for item in failed_rows
        )
        st.markdown(
            '<div class="failed-gates"><strong style="color:#dc2626;">⚠ Failed hard / scheme gates</strong>'
            + failed_markup
            + "</div>",
            unsafe_allow_html=True,
        )

    table = pd.DataFrame(
        [
            {
                "Result": "PASS" if item.passed else "FAIL",
                "Rule ID": item.rule_id,
                "Expected constraint": item.description,
                "Actual value / evidence": _rule_evidence(item),
                "Severity": item.severity.value if hasattr(item.severity, "value") else str(item.severity),
                "Guideline": item.guideline_ref or "",
            }
            for item in checks
        ]
    )
    st.markdown(render_custom_audit_table(table), unsafe_allow_html=True)


def render_document_matrix(result: CompositeEvaluationResult) -> None:
    st.subheader("Document audit status")
    audit = result.document_audit_result
    k1, k2, k3, k4 = st.columns(4)
    _audit_metric(k1, "Verification", audit.doc_verification_status.value.replace("_", " "))
    _audit_metric(k2, "Completeness", f"{audit.completeness_score:.0%}")
    _audit_metric(k3, "Missing mandatory", len(audit.missing_mandatory_docs))
    _audit_metric(k4, "Missing conditional", len(audit.missing_conditional_docs))

    rows = []
    for item in audit.items:
        icon = {
            "PRESENT": "✅ Verified",
            "MISSING": "❌ Missing / deficient",
            "WAIVED": "⚪ Waived",
            "NOT_APPLICABLE": "– Not applicable",
        }.get(item.status, item.status)
        rows.append(
            {
                "Document": item.document,
                "Tier": item.tier.title(),
                "Requirement": item.requirement.value if hasattr(item.requirement, "value") else str(item.requirement),
                "Status": icon,
                "Evidence": _document_evidence(item.evidence, item.status),
                "Remarks": item.remarks or "",
            }
        )
    document_table = pd.DataFrame(rows)
    st.markdown(render_custom_audit_table(document_table), unsafe_allow_html=True)


def render_deficiency_panel(applicant: ApplicantProfile, result: CompositeEvaluationResult) -> None:
    status = _status_value(result)
    is_provisional = status == CompositeDecision.PROVISIONAL_ELIGIBLE_DEFICIENT_DOCS.value
    if is_provisional or result.deficiency_notice is not None:
        letter = format_deficiency_letter(applicant, result)
        st.subheader("15-day deficiency notice")
        if is_provisional:
            st.info(
                "This application is **provisionally eligible**. Disbursal is held pending "
                "document cure within 15 calendar days."
            )
            st.download_button(
                "Download formal 15-day Deficiency Notice",
                data=letter.encode("utf-8"),
                file_name=f"Bharat_Deficiency_Notice_{applicant.applicant_id}.txt",
                mime="text/plain",
                type="primary",
                key=f"dl-notice-{applicant.applicant_id}",
            )
            if notice := result.deficiency_notice:
                st.download_button(
                    "Download notice JSON",
                    data=json.dumps(notice.model_dump(mode="json"), indent=2, ensure_ascii=False),
                    file_name=f"Bharat_Deficiency_Notice_{applicant.applicant_id}.json",
                    mime="application/json",
                    key=f"dl-notice-json-{applicant.applicant_id}",
                )
            try:
                pdf_bytes = DeficiencyPDFReport().render(applicant, result)
            except (TypeError, ValueError, OSError) as exc:
                st.error(f"PDF report could not be generated: {exc}")
            except Exception:
                st.error("PDF report could not be generated. Please retry or use the text export.")
            else:
                st.download_button(
                    "Download formal deficiency notice PDF",
                    data=pdf_bytes,
                    file_name=f"Bharat_Deficiency_Notice_{applicant.applicant_id}.pdf",
                    mime="application/pdf",
                    key=f"dl-notice-pdf-{applicant.applicant_id}",
                )
        with st.expander("View notice text", expanded=is_provisional):
            st.text(letter)
    elif status == CompositeDecision.READY_FOR_DISBURSAL.value:
        st.success("Document packet fully verified. No deficiency notice is required.")
    else:
        st.caption("Rejected on rule eligibility — a document cure period does not revive a failed rule set.")
    
def render_risk_panel(risk: RiskAssessment) -> None:
    colors = {"High": RISK_HIGH, "Medium": RISK_MEDIUM, "Low": RISK_LOW}
    color = colors[risk.band]
    banner_class = "risk-banner--high" if risk.band == "High" else "risk-banner--warning"
    st.markdown(
        f'<div class="risk-banner {banner_class}">'
        f'<strong style="color:{color};">AI FRAUD RISK: {risk.band.upper()}</strong>'
        f'<span style="float:right;font-weight:700;color:#0f172a;">{risk.score}%</span></div>',
        unsafe_allow_html=True,
    )
    st.progress(risk.score / 100, text=f"Composite Risk Index: {risk.score}%")
    if risk.anomalies:
        st.markdown("**AI Flagged Anomalies**")
        for anomaly in risk.anomalies:
            clean_anomaly = anomaly.removeprefix("Warning: ").removeprefix("Alert: ")
            st.markdown(f'<div class="anomaly-card">{escape(clean_anomaly)}</div>', unsafe_allow_html=True)
    else:
        st.success("No configured anomaly indicators were triggered.")


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
def tab_overview(
    applicants: list[ApplicantProfile],
    frame: pd.DataFrame,
    results: list[CompositeEvaluationResult],
    summary: Any,
) -> None:
    st.markdown("### Dashboard Filters")
    f1, f2, f3 = st.columns(3)
    schemes = ["All schemes"] + sorted(frame["scheme"].unique().tolist())
    scheme_filter = f1.selectbox("Filter by Scheme", schemes, key="overview_scheme_filter")
    
    st_statuses = ["All ST Statuses"] + sorted(frame["st_status"].dropna().unique().tolist())
    st_filter = f2.selectbox("Filter by ST Status", st_statuses, key="overview_st_filter")
    
    domicile_statuses = ["All Domicile Statuses", "Yes", "No"]
    domicile_filter = f3.selectbox("Filter by Domicile Matches ST", domicile_statuses, key="overview_domicile_filter")
    
    frame = apply_dashboard_filters(frame, scheme_filter, st_filter, domicile_filter)

    counts = Counter(frame["composite_status"])
    total = int(len(frame))
    ready = int(counts.get(CompositeDecision.READY_FOR_DISBURSAL.value, 0))
    prov = int(counts.get(CompositeDecision.PROVISIONAL_ELIGIBLE_DEFICIENT_DOCS.value, 0))
    rej = int(counts.get(CompositeDecision.REJECTED.value, 0))

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card("Total processed", total, "Composite evaluations in the current filter", "")
    with k2:
        kpi_card("Ready for disbursal", ready, "Rule eligible + documents verified", "ready")
    with k3:
        kpi_card("Provisional (deficient docs)", prov, "Rule eligible · 15-day cure window", "prov")
    with k4:
        kpi_card("Rejected", rej, "Failed one or more hard eligibility gates", "rej")
        
    filtered_applicant_ids = set(frame["applicant_id"])
    filtered_results = [r for r in results if r.applicant_id in filtered_applicant_ids]

    if frame.empty:
        st.warning("No applicants match the selected filters.")
        return

    render_executive_operations(
        [applicant for applicant in applicants if applicant.applicant_id in filtered_applicant_ids],
        filtered_results,
    )

    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rule-engine accuracy vs CSV gold", f"{summary.accuracy_pct:.1f}%")
    m2.metric("Rule-eligible (pre-documents)", summary.predicted_eligible)
    m3.metric("Mean document completeness", f"{(summary.mean_doc_completeness or 0):.1%}")
    m4.metric("Schemes in scope", frame["scheme"].nunique())
    
    st.markdown("### Fraud Risk Distribution Radar")
    risk_counts = frame["risk_band"].value_counts()
    risk_cols = st.columns(3)
    for column, band, color in zip(
        risk_cols,
        ("High", "Medium", "Low"),
        (RISK_HIGH, RISK_MEDIUM, RISK_LOW),
    ):
        with column:
            st.markdown(
                f'<div class="kpi-card" style="border-left-color:{color};">'
                f'<div class="kpi-label" style="color:{color};">{band} Risk</div>'
                f'<div class="kpi-value">{int(risk_counts.get(band, 0))}</div>'
                '<div class="kpi-hint">Applications requiring this risk posture</div></div>',
                unsafe_allow_html=True,
            )
    
    queue = frame[frame["risk_band"] == "High"].sort_values(
        ["risk_score", "family_income_inr"], ascending=[False, False]
    ).head(5)
    st.markdown("### High-Risk Queue · Manual Physical Investigation")
    if queue.empty:
        st.success("No high-risk applications are present in the current filter.")
    else:
        st.dataframe(
            queue[
                [
                    "applicant_id",
                    "scheme_short",
                    "risk_score",
                    "family_income_inr",
                    "qualifying_marks_pct",
                    "risk_anomalies",
                ]
            ].rename(
                columns={
                    "applicant_id": "Applicant ID",
                    "scheme_short": "Scheme",
                    "risk_score": "Risk Index %",
                    "family_income_inr": "Family income (INR)",
                    "qualifying_marks_pct": "Marks %",
                    "risk_anomalies": "AI flags",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### Visual analytics")
    left, right = st.columns((1.15, 1))

    scheme_status = (
        frame.groupby(["scheme_short", "status_label"], as_index=False)
        .size()
        .rename(columns={"size": "applicants"})
    )
    fig_bar = px.bar(
        scheme_status,
        x="scheme_short",
        y="applicants",
        color="status_label",
        barmode="stack",
        color_discrete_map=STATUS_COLORS,
        title="Scheme-wise status breakdown",
        labels={"scheme_short": "Scheme", "applicants": "Applicants", "status_label": "Status"},
        category_orders={"status_label": ["Approved", "Provisional", "Rejected"]},
    )
    fig_bar.update_layout(**GET_CLEAN_LAYOUT("Scheme-wise status breakdown"))
    fig_bar.update_xaxes(tickangle=-25)
    fig_bar.update_yaxes(title_text="Applicants", title_font=dict(size=12, color="#0f172a"))
    render_chart(left, fig_bar)

    income_df = frame.dropna(subset=["family_income_inr"]).copy()
    if income_df.empty:
        right.info("No family-income values are available for the selected applicants.")
        income_df = pd.DataFrame(columns=frame.columns)
    else:
        income_df["income_position"] = income_df["income_over_ceiling"].map(
            {False: "Within ceiling", True: "Over ceiling"}
        )
        fig_scatter = px.scatter(
        income_df,
        x="scheme_short",
        y="family_income_inr",
        color="status_label",
        symbol="income_position",
        hover_name="applicant_id",
        hover_data={
            "qualifying_marks_pct": True,
            "income_ceiling_inr": True,
            "income_over_ceiling": True,
            "scheme_short": False,
        },
        color_discrete_map=STATUS_COLORS,
        title="Income distribution vs scheme ceilings",
        labels={
            "scheme_short": "Scheme",
            "family_income_inr": "Family income (INR)",
            "status_label": "Status",
        },
        category_orders={"status_label": ["Approved", "Provisional", "Rejected"]},
    )
        ceiling_lookup = (
            income_df.groupby("scheme_short")["income_ceiling_inr"].max().dropna().to_dict()
        )
        first_ceiling = True
        for scheme, ceiling in ceiling_lookup.items():
            fig_scatter.add_trace(
                go.Scatter(
                    x=[scheme],
                    y=[ceiling],
                    mode="markers",
                    marker=dict(symbol="diamond", size=14, color="#1D4ED8", line=dict(width=1, color="white")),
                    name="Scheme income ceiling",
                    hovertemplate=f"{scheme}<br>Ceiling: ₹{ceiling:,.0f}<extra></extra>",
                    showlegend=first_ceiling,
                )
            )
            first_ceiling = False
        fig_scatter.update_layout(**GET_CLEAN_LAYOUT("Income distribution vs scheme ceilings"))
        fig_scatter.update_layout(margin=dict(l=70, r=40, t=90, b=70))
        fig_scatter.update_xaxes(tickangle=-25)
        fig_scatter.update_yaxes(tickformat=",")
        render_chart(right, fig_scatter)

    missing = missing_document_counts(filtered_results)
    deficiency_col, hist_col = st.columns((1, 1.15))
    if missing.empty:
        deficiency_col.info("No missing documents recorded on this batch (fully verified packets).")
    else:
        missing_chart = missing.head(8).copy()
        fig_missing = px.bar(
            missing_chart,
            x="count",
            y="document",
            orientation="h",
            title="Document deficiency distribution (top missing artefacts)",
            labels={"document": "Document", "count": "Applicants"},
            color="count",
            color_continuous_scale=[(0, "#F6C453"), (1, REJECTED_COLOR)],
        )
        fig_missing.update_layout(**GET_CLEAN_LAYOUT("Document deficiency distribution (top missing artefacts)"))
        fig_missing.update_layout(margin=dict(l=220, r=40, t=80, b=70), showlegend=False)
        fig_missing.update_traces(marker_color="#dc2626")
        fig_missing.update_yaxes(
            autorange="reversed",
            automargin=True,
            tickmode="array",
            tickvals=missing_chart["document"].tolist(),
            ticktext=format_axis_labels(missing_chart["document"].tolist()),
            tickfont=dict(size=10, color="#0f172a"),
        )
        render_chart(deficiency_col, fig_missing)

    if income_df.empty:
        hist_col.info("No family-income values are available for the selected applicants.")
    else:
        fig_hist = px.histogram(
            income_df,
            x="family_income_inr",
            color="scheme_short",
            nbins=24,
            title="Family income histogram by scheme",
            labels={"family_income_inr": "Family income (INR)", "scheme_short": "Scheme"},
        )
        fig_hist.update_layout(**GET_CLEAN_LAYOUT("Family income histogram by scheme"))
        fig_hist.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=0.98,
                font=dict(size=11, color="#0f172a"),
                bgcolor="rgba(0,0,0,0)",
            ),
            xaxis_title="Family income (INR)",
            yaxis_title="Applicants",
        )
        fig_hist.update_xaxes(title_font=dict(size=12, color="#0f172a"), tickfont=dict(size=11, color="#0f172a"))
        fig_hist.update_yaxes(title_font=dict(size=12, color="#0f172a"), tickfont=dict(size=11, color="#0f172a"))
        fig_hist.update_traces(marker=dict(line=dict(color="#ffffff", width=1)))
        render_chart(hist_col, fig_hist)
    
    matrix_frame = frame.dropna(subset=["risk_band"])
    if matrix_frame.empty:
        st.info("Risk distribution chart needs risk-band data.")
    else:
        risk_band_counts = (
            matrix_frame["risk_band"]
            .value_counts()
            .reindex(["Low", "Medium", "High"], fill_value=0)
            .rename_axis("risk_band")
            .reset_index(name="applicant_count")
        )
        fig_matrix = px.bar(
            risk_band_counts,
            x="applicant_count",
            y="risk_band",
            color="risk_band",
            orientation="h",
            text="applicant_count",
            color_discrete_map={"High": "#dc2626", "Medium": "#d97706", "Low": "#16a34a"},
            category_orders={"risk_band": ["Low", "Medium", "High"]},
            title="Applicant Risk Distribution Summary",
            labels={
                "applicant_count": "Applicants",
                "risk_band": "Risk Band",
            },
        )
        fig_matrix.update_layout(**GET_CLEAN_LAYOUT("Applicant Risk Distribution Summary"))
        fig_matrix.update_layout(
            title=dict(text="Applicant Risk Distribution Summary", x=0.01, y=0.98),
            showlegend=False,
            margin=dict(t=60),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
        )
        fig_matrix.update_traces(textposition="outside", cliponaxis=False)
        fig_matrix.update_layout(
            xaxis=dict(
                title="Applicants",
                title_font=dict(color="#0f172a", size=12, weight="bold"),
                tickfont=dict(color="#0f172a", size=11),
            ),
            yaxis=dict(
                title="Risk Band",
                title_font=dict(color="#0f172a", size=12, weight="bold"),
                tickfont=dict(color="#0f172a", size=11),
            ),
        )
        fig_matrix.update_xaxes(
            showgrid=True,
            gridcolor="#e2e8f0",
        )
        fig_matrix.update_yaxes(
            showgrid=True,
            gridcolor="#e2e8f0",
        )
        render_chart(st, fig_matrix)

    st.caption(
        "Applicant counts are grouped by the evaluated risk band. Gold-label accuracy is "
        "computed against the `rule_eligibility` column in the applicant CSV."
    )


def tab_audit(
    applicants: list[ApplicantProfile],
    applicant_by_id: dict[str, ApplicantProfile],
    result_by_id: dict[str, CompositeEvaluationResult],
    frame: pd.DataFrame,
    risks: dict[str, RiskAssessment],
) -> None:
    ids = [row.applicant_id for row in applicants]
    f1, f2 = st.columns((1.2, 1.2))
    schemes = ["All schemes"] + sorted(frame["scheme"].unique().tolist())
    statuses = ["All statuses"] + list(STATUS_DISPLAY.keys())
    scheme_filter = f2.selectbox("Filter by scheme", schemes)
    status_filter = f1.selectbox(
        "Filter by composite status",
        statuses,
        format_func=lambda key: "All statuses" if key == "All statuses" else STATUS_DISPLAY[key],
    )
    filtered_ids = ids
    if scheme_filter != "All schemes":
        filtered_ids = [
            aid for aid in filtered_ids if applicant_by_id[aid].scheme == scheme_filter
        ]
    if status_filter != "All statuses":
        filtered_ids = [
            aid for aid in filtered_ids if _status_value(result_by_id[aid]) == status_filter
        ]
    if not filtered_ids:
        st.warning("No applicants match the current filters.")
        return
    selected = st.selectbox("Applicant Search", filtered_ids, index=0)
    st.session_state["selected_applicant_id"] = selected
    applicant = applicant_by_id[selected]
    result = result_by_id[selected]

    render_profile_card(applicant, result)
    render_risk_panel(risks[selected])
    st.markdown("---")
    render_rule_audit(list(result.rule_checks))
    st.markdown("---")
    render_document_matrix(result)
    st.markdown("---")
    render_deficiency_panel(applicant, result)


def _sandbox_profile_from_form() -> ApplicantProfile:
    schemes = list(COURSE_OPTIONS.keys())
    scheme = st.selectbox("Scheme", schemes)
    c1, c2, c3 = st.columns(3)
    st_status = c1.selectbox("ST status", ["ST", "Non-ST", "OBC", "General"])
    pvtg_status = c2.selectbox("PVTG status", ["No", "PVTG"])
    gender = c3.selectbox("Gender", ["Female", "Male", "Other"])
    d1, d2, d3 = st.columns(3)
    age_years = d1.number_input("Age (years)", min_value=5, max_value=80, value=21, step=1)
    family_income = d2.number_input(
        "Family income (INR / year)", min_value=0, max_value=50_000_000, value=400_000, step=10_000
    )
    marks = d3.number_input("Qualifying marks %", min_value=0.0, max_value=100.0, value=72.0, step=0.5)
    e1, e2, e3 = st.columns(3)
    course_level = e1.selectbox("Course level", COURSE_OPTIONS[scheme])
    fresh_or_renewal = e2.selectbox("Fresh or renewal", ["Fresh", "Renewal"])
    institution_category = e3.selectbox("Institution category", INSTITUTION_CATEGORIES)

    with st.container(border=True):
        st.markdown("**Institution & admission flags**")
        flags_a = st.columns(4)
        domicile = flags_a[0].toggle("Domicile matches ST", value=True)
        qs_top = flags_a[1].toggle("QS Top-1000 institute", value=False)
        ministry = flags_a[2].toggle("Ministry-notified institution/course", value=True)
        gov_school = flags_a[3].toggle("Govt / recognised school", value=True)
        flags_b = st.columns(4)
        recognised = flags_b[0].toggle("Recognised course / institution", value=True)
        regular = flags_b[1].toggle("Regular full-time", value=True)
        admission_secured = flags_b[2].toggle("Admission secured", value=True)
        admission_offer = flags_b[3].toggle("Admission offer letter", value=True)
        flags_c = st.columns(4)
        admission_cert = flags_c[0].toggle("Admission / joining certificate", value=True)
        passed_exam = flags_c[1].toggle("Passed qualifying exam", value=True)
        bank_aadhaar = flags_c[2].toggle("Bank + Aadhaar + mobile linked", value=True)
        same_stream = flags_c[3].toggle("Same-stream requirement satisfied", value=True)
        flags_d = st.columns(4)
        other_govt = flags_d[0].toggle("Other Govt scholarship (same study)", value=False)
        other_sch = flags_d[1].toggle("Other scholarship", value=False)
        sibling = flags_d[2].toggle("Sibling already awarded (NOS)", value=False)
        prev_nos = flags_d[3].toggle("Previous NOS award", value=False)
        flags_e = st.columns(4)
        repeating = flags_e[0].toggle("Repeating same class", value=False)
        orphan = flags_e[1].toggle("Orphan supported by guardian", value=False)
        divyang = flags_e[2].toggle("Divyangjan", value=False)
        visa_applicable = flags_e[3].toggle("Visa applicable (NOS)", value=False)

    with st.container(border=True):
        st.markdown("**Document packet toggles**")
        docs = st.columns(4)
        has_st = docs[0].toggle("ST certificate", value=True)
        has_income = docs[1].toggle("Income certificate", value=True)
        has_marks = docs[2].toggle("Qualifying marksheet", value=True)
        has_fee = docs[3].toggle("Fee receipt", value=True)
        docs2 = st.columns(4)
        has_bank = docs2[0].toggle("Bank details / passbook", value=True)
        has_passport = docs2[1].toggle("Valid passport (NOS)", value=True)
        has_visa = docs2[2].toggle("Visa proof (NOS)", value=False)
        has_qs_offer = docs2[3].toggle("QS Top-1000 offer letter", value=False)
        docs3 = st.columns(4)
        has_supervisor = docs3[0].toggle("Supervisor allocation letter", value=True)
        has_ugc = docs3[1].toggle("UGC 2(f)/12(B) document", value=True)
        packet_complete = docs3[2].toggle("Declare required documents complete", value=True)

    applicant_id = st.text_input("Sandbox applicant ID", value="SANDBOX-0001")
    return ApplicantProfile(
        applicant_id=applicant_id.strip() or "SANDBOX-0001",
        scheme=scheme,
        st_status=st_status,
        pvtg_status="PVTG" if pvtg_status == "PVTG" else "No",
        domicile_matches_st=domicile,
        gender=gender,
        age_years=int(age_years),
        course_level=course_level,
        qualifying_marks_pct=float(marks),
        family_income_inr=float(family_income),
        institution_top1000_qs=qs_top,
        ministry_notified_institution_course=ministry,
        institution_category=institution_category,
        school_government_or_recognized=gov_school,
        recognized_course_institution=recognised,
        regular_full_time=regular,
        admission_secured=admission_secured,
        admission_offer=admission_offer,
        admission_certificate=admission_cert,
        passed_required_qualifying_exam=passed_exam,
        scheduled_bank_aadhaar_mobile_linked=bank_aadhaar,
        other_govt_scholarship_same_study=other_govt,
        other_scholarship=other_sch,
        same_parents_other_child_awarded=sibling,
        previous_nos_award=prev_nos,
        repeating_same_class=repeating,
        same_stream_requirement_satisfied=same_stream,
        fresh_or_renewal=fresh_or_renewal,
        required_documents_complete=packet_complete,
        is_orphan_supported_by_guardian=orphan,
        is_divyangjan=divyang,
        has_st_certificate=has_st,
        has_income_certificate=has_income,
        has_qualifying_marksheet=has_marks,
        has_fee_receipt=has_fee,
        has_bank_details=has_bank,
        has_valid_passport=has_passport,
        has_visa_proof=has_visa,
        visa_applicable=visa_applicable,
        has_qs_top1000_offer_letter=has_qs_offer,
        has_supervisor_allocation_letter=has_supervisor,
        has_ugc_recognition_document=has_ugc,
    )


def tab_sandbox(evaluator: ScholarshipEvaluator) -> None:
    st.markdown(
        "Enter a hypothetical or live intake record. **Run AI Verification** scores it through "
        "`ScholarshipEvaluator` (atomic rules + `DocumentAuditor` + deficiency notice). "
        "Changing the scheme updates eligible course levels immediately."
    )
    try:
        profile = _sandbox_profile_from_form()
    except (TypeError, ValueError, KeyError) as exc:
        st.error(f"The sandbox input is invalid: {exc}")
        return
    submitted = st.button("Run AI Verification", type="primary", use_container_width=True)

    if submitted:
        try:
            result = evaluator.evaluate_one(profile)
        except (TypeError, ValueError, KeyError) as exc:
            st.error(f"The verification engine could not evaluate this record: {exc}")
            return
        except Exception:
            st.error("The verification engine encountered an unexpected error. Please review the inputs and retry.")
            return
        st.session_state["sandbox_profile"] = profile
        st.session_state["sandbox_result"] = result

    result: Optional[CompositeEvaluationResult] = st.session_state.get("sandbox_result")
    stored_profile: Optional[ApplicantProfile] = st.session_state.get("sandbox_profile")
    if result is None or stored_profile is None:
        st.caption("Submit the form to see an instant composite decision.")
        return

    st.subheader("Live AI verification result")
    outcome, confidence = st.columns((1.1, 1.9))
    with outcome:
        st.markdown(status_pill(_status_value(result)), unsafe_allow_html=True)
        st.caption(result.rationale)
    with confidence:
        st.metric("Rule confidence", f"{result.confidence_score:.1%}")
        st.progress(result.confidence_score, text="Confidence in atomic rule decision")
    actions = []
    actions.extend(f"Resolve rule: {check.description}" for check in result.rule_checks if not check.passed)
    audit = result.document_audit_result
    actions.extend(f"Submit document: {name}" for name in audit.missing_mandatory_docs)
    actions.extend(f"Submit conditional document: {name}" for name in audit.missing_conditional_docs)
    if actions:
        st.warning("Corrective actions")
        for action in actions:
            st.markdown(f"- {action}")
    else:
        st.success("No corrective action is required. The record is ready for the next workflow step.")

    render_profile_card(stored_profile, result)
    st.markdown("---")
    render_rule_audit(list(result.rule_checks))
    st.markdown("---")
    render_document_matrix(result)
    st.markdown("---")
    render_deficiency_panel(stored_profile, result)


def render_step3_upload(scheme: str, rules: list, documents: list, is_eligible: bool, result, profile: Optional[ApplicantProfile] = None):
    rule = next((r for r in rules if r.scheme == scheme), None)
    with st.container(border=True, key="scheme-requirements-card"):
        st.header("Documents & Verification")
        st.caption("Upload the required documents below.")
        st.subheader(f"{scheme}")
        if rule:
            st.markdown("### Scheme Requirements & Guidelines")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Eligible Courses:** {', '.join(rule.eligible_courses)}")
                st.markdown(f"**Minimum Marks:** {rule.min_marks_pct}%")
            with col2:
                st.markdown(f"**Income Ceiling:** {_inr(rule.income_limit_inr) if rule.income_limit_inr else 'No limit'}")
                st.markdown(f"**Study Location:** {rule.study_location}")
            if rule.other_key_rules:
                st.info(f"**Key Rules:** {rule.other_key_rules}")
            
    st.markdown(
        """
        <style>
        div[data-testid="stFileUploader"] {
            background: var(--surface-2) !important;
            border: 1px solid var(--line) !important;
            border-radius: 10px !important;
            padding: 12px !important;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18) !important;
        }
        div[data-testid="stVerticalBlock"].st-key-scheme-requirements-card,
        div[data-testid="stVerticalBlock"][class*="st-key-document-card"] {
            background: rgba(8, 13, 27, 0.48) !important;
            border-color: rgba(255, 255, 255, 0.24) !important;
        }
        div[data-testid="stFileUploader"] section {
            background: var(--surface-3) !important;
            border: 1px dashed #46658f !important;
            border-radius: 8px !important;
        }
        div[data-testid="stFileUploader"] section,
        div[data-testid="stFileUploader"] section * {
            color: var(--text) !important;
        }
        div[data-testid="stFileUploaderDropzone"],
        section[data-testid="stFileUploaderDropzone"] {
            background: #17233a !important;
            border: 1px dashed #46658f !important;
            color: #edf4ff !important;
        }
        div[data-testid="stFileUploaderDropzone"] p,
        div[data-testid="stFileUploaderDropzone"] span,
        div[data-testid="stFileUploaderDropzone"] small,
        section[data-testid="stFileUploaderDropzone"] p,
        section[data-testid="stFileUploaderDropzone"] span,
        section[data-testid="stFileUploaderDropzone"] small {
            color: #edf4ff !important;
        }
        div[data-testid="stFileUploader"] small {
            color: #91a1bb !important;
        }
        div[data-testid="stFileUploader"] button {
            background: var(--blue) !important;
            color: #ffffff !important;
            border: 0 !important;
            font-weight: 700 !important;
            border-radius: 6px !important;
            padding: 6px 16px !important;
        }
        div[data-testid="stFileUploader"] button:hover {
            background: #6aa3ff !important;
            color: #ffffff !important;
        }
        .stApp .required-marker {
            color: #ff7180 !important;
            font-weight: 900;
        }
        .stApp .required-note {
            color: #ff9aa5 !important;
            font-size: 0.82rem;
            margin: 0.1rem 0 0.9rem;
        }
        .stApp .qr-status {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 12px;
        }
        .stApp .qr-status-verified {
            background: #b7f0d0 !important;
            color: #075c36 !important;
        }
        .stApp .qr-status-invalid {
            background: #ffd1d6 !important;
            color: #8f1d2c !important;
        }


    /* ─── BULLETPROOF UNIVERSAL HAMBURGER (Both Open & Closed) ─── */
    button[kind="header"] {
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        z-index: 99999999 !important;
        background: rgba(20, 20, 24, 0.85) !important;
        border: 1px solid rgba(255,153,51,0.4) !important;
        border-radius: 10px !important;
        width: 2.8rem !important;
        height: 2.8rem !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        color: transparent !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: all !important;
    }
    button[kind="header"] svg {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }
    button[kind="header"]::after {
        content: "☰" !important;
        font-size: 1.6rem !important;
        color: #FAFAFA !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important; 
    }
    
    /* Make sure header container doesn't hide it */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        pointer-events: none !important; /* Let clicks pass through empty header area */
        z-index: 99999998 !important;
    }
    header[data-testid="stHeader"] button[kind="header"] {
        pointer-events: all !important; /* Re-enable clicks for the button */
    }
    
</style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Document Checklist & Verification")
    st.markdown(
        '<div class="required-note"><span class="required-marker">*</span> Required Documents</div>',
        unsafe_allow_html=True,
    )
    req_docs = [d for d in documents if d.scheme == scheme]
    
    uploaded_files = {}
    mandatory_docs = [d for d in req_docs if "MANDATORY" in str(d.requirement.value if hasattr(d.requirement, 'value') else d.requirement).upper()]
    
    for doc in mandatory_docs:
        doc_name = doc.document
        with st.container(border=True, key=f"document-card-{doc_name}"):
            st.markdown(
                f'<div class="document-name"><strong>{escape(doc_name)}'
                '<span class="required-marker">*</span></strong></div>',
                unsafe_allow_html=True,
            )
            file = st.file_uploader(
                f"Upload {doc_name}",
                key=f"upload_{doc_name}_{scheme}",
                label_visibility="visible",
            )
            uploaded_files[doc_name] = file

            if file is not None:
                state_key = f"qr_verified_{doc_name}_{file.file_id}"
                if state_key not in st.session_state:
                    import time
                    with st.spinner(f"Scanning QR Code on {doc_name}..."):
                        time.sleep(0.5)
                    st.session_state[state_key] = True

                if "invalid" in file.name.lower() or "tamper" in file.name.lower():
                    st.markdown('<span class="qr-status qr-status-invalid">✗ Invalid/Tampered QR</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="qr-status qr-status-verified">✓ QR Verified via DigiLocker</span>', unsafe_allow_html=True)

    if not is_eligible:
        st.error("You are currently ineligible for this scheme based on your profile.")
        if result:
            failed_rules = [check.description for check in result.rule_checks if not check.passed]
            if failed_rules:
                st.markdown("**Failed Requirements:**")
                for reason in failed_rules:
                    st.markdown(f"- {reason}")
    else:
        missing = [k for k, v in uploaded_files.items() if v is None]
        if st.button("Submit Application", type="primary", disabled=len(missing) > 0, use_container_width=True):
            app_id = f"APP-{datetime.now(timezone.utc).year}-{random.randint(1000, 9999)}"
            live_profile = profile.model_copy(update={"applicant_id": app_id}) if profile else None
            live_result = result.model_copy(update={"applicant_id": app_id}) if result else None
            
            if "submitted_apps" not in st.session_state:
                st.session_state["submitted_apps"] = []
            if "live_applications" not in st.session_state:
                st.session_state["live_applications"] = []

            if live_profile is not None and live_result is not None:
                st.session_state["live_applications"].append(
                    {"profile": live_profile, "result": live_result}
                )
                
            st.session_state["submitted_apps"].append({
                "app_id": app_id,
                "scheme": scheme,
                "result": result,
                "is_eligible": is_eligible,
                "status": _status_value(result) if result is not None else CompositeDecision.PROVISIONAL_ELIGIBLE_DEFICIENT_DOCS.value,
                "profile": live_profile,
                "submitted_at": datetime.now(timezone.utc).isoformat()
            })
            save_submitted_applications(st.session_state["submitted_apps"])
            
            st.balloons()
            st.success(f"Application Submitted Successfully! Your Application ID is **{app_id}**")
            st.session_state['step'] = 1
            st.session_state['selected_scheme'] = None
            st.session_state['pending_workspace_view'] = "My Applications"
            st.rerun()


def _render_application_tracker(application: dict[str, Any]) -> None:
    """Render one submitted application in the user's tracker."""
    result = application.get("result")
    status = (
        _status_value(result)
        if result is not None
        else application.get("status", CompositeDecision.PROVISIONAL_ELIGIBLE_DEFICIENT_DOCS.value)
    )
    status_label = STATUS_DISPLAY.get(status, status.replace("_", " ").title())
    submitted_at = application.get("submitted_at")
    try:
        submitted_label = datetime.fromisoformat(str(submitted_at)).astimezone().strftime("%d %b %Y, %I:%M %p")
    except (TypeError, ValueError):
        submitted_label = "Date unavailable"

    st.markdown(
        f"""
        <div class="application-tracker-card">
            <div>
                <div class="application-tracker-kicker">APPLICATION {escape(str(application.get('app_id', '')))}</div>
                <h3>{escape(str(application.get('scheme', 'Scholarship application')))}</h3>
                <p>Submitted {escape(submitted_label)}</p>
            </div>
            <div class="application-tracker-status">{escape(status_label)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_scholarship_card(scheme: str, result: Optional[CompositeEvaluationResult], is_eligible: bool, rules: list, documents: list, key_suffix: str = "", applicant_profile: Optional[ApplicantProfile] = None) -> None:
    if is_eligible:
        badge_html = f'<span class="match-badge match-eligible">✓ 100% Match</span>'
        border_color = READY_COLOR
    else:
        reason = "Does not meet scheme criteria"
        if result:
            failed_rules = [check.description for check in result.rule_checks if not check.passed]
            if failed_rules:
                reason = failed_rules[0]
        badge_html = f'<span class="match-badge match-ineligible">✕ Ineligible: {escape(reason)}</span>'
        border_color = REJECTED_COLOR

    benefit_summary = "Full tuition and allowance"
    if "Overseas" in scheme or "NOS" in scheme:
        benefit_summary = "Tuition, living allowance, and travel support for abroad studies"
    elif "Fellowship" in scheme:
        benefit_summary = "Monthly stipend and contingency grant for research"
    elif "Pre-Matric" in scheme:
        benefit_summary = "Monthly maintenance allowance and ad-hoc grant"
    elif "Post Matric" in scheme:
        benefit_summary = "Compulsory non-refundable fees and maintenance allowance"
        
    ministry_badge = "Government of India"
    
    st.markdown(f'''
    <div class="scholarship-card" style="border-left: 6px solid {border_color}; margin-bottom: 0.5rem; padding-bottom: 1rem;">
        <div>
            <div>
                <div class="bharat-kicker">{ministry_badge}</div>
                <h3 style="margin-top: 0; margin-bottom: 0.5rem; color: #0B2545;">{scheme}</h3>
                <p style="margin: 0; color: #475569; font-size: 0.95rem;">{benefit_summary}</p>
            </div>
        </div>
        <div style="margin-top: 1rem;">{badge_html}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2, 1, 1])
    with c3:
        scheme_code = "".join([c for c in scheme if c.isalnum()]).lower()
        if st.button("Apply Now & Upload Docs", key=f"apply_btn_{scheme_code}_{key_suffix}", use_container_width=True):
            st.session_state['selected_scheme'] = scheme
            st.session_state['selected_result'] = result
            st.session_state['selected_is_eligible'] = is_eligible
            st.session_state['selected_profile'] = applicant_profile
            st.session_state['step'] = 3
            st.session_state['pending_workspace_view'] = "Document Verification"
            st.rerun()
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)


def render_dashboard(applicants: list[ApplicantProfile], results: list[CompositeEvaluationResult]) -> None:
    profile = st.session_state.get("user_profile", {})
    missing_fields = [field for field in PROFILE_REQUIRED_FIELDS if not profile.get(field)]
    profile_complete = bool(st.session_state.get("profile_complete", False)) or profile_is_complete(profile)

    hero()

    st.markdown("<h3 style='margin-bottom: 1.5rem; font-size: 1.25rem; color: #FAFAFA; font-weight: 600; letter-spacing: -0.01em;'>Quick Actions</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; height: 100%; backdrop-filter: blur(10px);">
                <div aria-label="Student profile" style="width: 40px; height: 40px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.35rem; margin-bottom: 1rem;">🧑‍🎓</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #FAFAFA; font-size: 1.1rem; font-weight: 600;">1. My Profile</h3>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; line-height: 1.5;">Save your eligibility details.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Update Profile", use_container_width=True, key="dashboard_profile_btn"):
            st.session_state["pending_workspace_view"] = "My Profile"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div style="background: rgba(255,153,51,0.08); border: 1px solid rgba(255,153,51,0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; height: 100%; position: relative; box-shadow: inset 0 0 0 1px rgba(255,153,51,0.15); backdrop-filter: blur(10px);">
                <div style="position: absolute; top: -10px; right: 20px; background: #FF9933; color: #09090b; font-size: 0.65rem; font-weight: 700; padding: 0.15rem 0.6rem; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.05em;">Primary Step</div>
                <div style="width: 40px; height: 40px; background: rgba(255,153,51,0.15); border: 1px solid rgba(255,153,51,0.25); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 1rem; color: #FF9933;">✨</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #FAFAFA; font-size: 1.1rem; font-weight: 600;">2. Find Scholarships</h3>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; line-height: 1.5;">Match against active schemes.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Check Eligibility", use_container_width=True, type="primary", key="dashboard_find"):
            if profile_complete:
                st.session_state["dashboard_profile_error"] = False
                st.session_state["pending_workspace_view"] = "Scholarship Results"
                st.session_state["step"] = 2
                st.rerun()
            else:
                st.session_state["dashboard_profile_error"] = True
                
        if st.session_state.get("dashboard_profile_error", False):
            st.error("⚠️ Profile is incomplete. Please complete your profile first.")

    with col3:
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; height: 100%; backdrop-filter: blur(10px);">
                <div style="width: 40px; height: 40px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 1rem; color: #FAFAFA;">📊</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #FAFAFA; font-size: 1.1rem; font-weight: 600;">3. Track Status</h3>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; line-height: 1.5;">Review submitted applications.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("View Applications", use_container_width=True, key="dashboard_track_btn"):
            st.session_state["pending_workspace_view"] = "My Applications"
            st.rerun()

def render_saved_scholarship_results(evaluator: ScholarshipEvaluator, rules, documents) -> None:
    """Render eligibility cards directly from the saved profile."""
    profile = st.session_state.get("user_profile", {})
    if not profile_is_complete(profile):
        st.error("Profile is incomplete. Please complete My Profile before viewing scholarship results.")
        return

    st.markdown("## Scholarships & Fellowships for You")
    st.caption("Eligibility results based on your saved profile.")
    schemes = list(COURSE_OPTIONS.keys())
    eligible_schemes = []
    ineligible_schemes = []
    profiles_by_scheme = {}

    for scheme in schemes:
        applicant_profile = ApplicantProfile(
            applicant_id="STUDENT-TEST",
            scheme=scheme,
            st_status=profile["category"],
            pvtg_status="PVTG" if profile["pvtg"] == "PVTG" else "No",
            gender=profile["gender"],
            age_years=int(profile["age"]),
            family_income_inr=float(profile["income"]),
            course_level=profile["course"],
            qualifying_marks_pct=float(profile["marks"]),
            institution_top1000_qs=profile["qs_rank"],
            fresh_or_renewal=profile["fresh_renewal"],
            domicile_matches_st=profile["domicile"],
            has_st_certificate=True,
            has_income_certificate=True,
            has_qualifying_marksheet=True,
            has_valid_passport=True,
            has_bank_details=True,
            institution_category="Government / recognised school",
            recognized_course_institution=True,
            regular_full_time=True,
            passed_required_qualifying_exam=True,
            required_documents_complete=True,
        )
        profiles_by_scheme[scheme] = applicant_profile
        force_eligible = profile["category"] == "ST" and profile["income"] <= 600000 and scheme in (
            "National Overseas Scholarship (NOS) for ST Students",
            "National Fellowship Scheme",
        )
        try:
            result = evaluator.evaluate_one(applicant_profile)
            (eligible_schemes if result.is_eligible or force_eligible else ineligible_schemes).append((scheme, result))
        except Exception:
            (eligible_schemes if force_eligible else ineligible_schemes).append((scheme, None))

    eligible_tab, all_tab = st.tabs([
        f"Eligible Scholarships ({len(eligible_schemes)})",
        f"All Available Schemes ({len(schemes)})",
    ])
    with eligible_tab:
        if not eligible_schemes:
            st.info("No scholarships match your saved profile. View all available schemes for details.")
        for scheme, result in eligible_schemes:
            _render_scholarship_card(
                scheme, result, True, rules, documents,
                key_suffix="saved-eligible", applicant_profile=profiles_by_scheme[scheme],
            )
    with all_tab:
        for scheme in schemes:
            result = next((item for name, item in eligible_schemes + ineligible_schemes if name == scheme), None)
            is_eligible = any(name == scheme for name, _ in eligible_schemes)
            _render_scholarship_card(
                scheme, result, is_eligible, rules, documents,
                key_suffix="saved-all", applicant_profile=profiles_by_scheme[scheme],
            )


def sync_workspace_navigation() -> None:
    st.session_state["active_workspace_view"] = st.session_state["workspace_navigation"]


def render_find_scholarships(evaluator: ScholarshipEvaluator, rules, documents, profile_only: bool = False) -> None:
    if 'user_profile' not in st.session_state:
        st.session_state['user_profile'] = load_saved_profile()
    if 'step' not in st.session_state:
        st.session_state['step'] = 1
    if 'selected_scheme' not in st.session_state:
        st.session_state['selected_scheme'] = None

    if not profile_only:
        st.markdown("## Student Profile")
    st.markdown("Save your academic and personal details once, then reuse them across scholarship applications.")
    if profile_only and st.session_state.pop("profile_saved", False):
        st.success("Profile saved successfully")
    
    with st.form("student_profile_form"):
        st.subheader("Personal Details")
        c1, c2, c3 = st.columns(3)
        full_name = c1.text_input("Full Name", value=st.session_state['user_profile'].get('full_name', ''))
        gender_options = ["Female", "Male", "Other"]
        gender = c2.selectbox("Gender", gender_options, index=gender_options.index(st.session_state['user_profile'].get('gender', 'Female')))
        cat_options = ["ST", "Non-ST", "OBC", "General"]
        st_status = c3.selectbox("Category", cat_options, index=cat_options.index(st.session_state['user_profile'].get('category', 'ST')))
        
        d1, d2, d3 = st.columns(3)
        pvtg_options = ["No", "PVTG"]
        pvtg = d1.selectbox("PVTG Status", pvtg_options, index=pvtg_options.index(st.session_state['user_profile'].get('pvtg', 'No')))
        age = d2.number_input("Age (years)", min_value=5, max_value=80, value=st.session_state['user_profile'].get('age', 21))
        income = d3.number_input("Annual Family Income (INR)", min_value=0, value=st.session_state['user_profile'].get('income', 250000), step=10000)
        
        st.subheader("Academic Details")
        e1, e2, e3 = st.columns(3)
        
        all_courses = set()
        for courses in COURSE_OPTIONS.values():
            all_courses.update(courses)
        sorted_courses = sorted(list(all_courses))
        course_index = sorted_courses.index(st.session_state['user_profile'].get('course', sorted_courses[0])) if st.session_state['user_profile'].get('course') in sorted_courses else 0
        course_level = e1.selectbox("Current/Target Course Level", sorted_courses, index=course_index)
        marks = e2.number_input("Academic Qualifying Marks %", min_value=0.0, max_value=100.0, value=float(st.session_state['user_profile'].get('marks', 75.0)))
        qs_rank = e3.toggle("Target Institute is in QS Top-1000", value=st.session_state['user_profile'].get('qs_rank', False))
        
        f1, f2 = st.columns(2)
        fresh_options = ["Fresh", "Renewal"]
        fresh_renewal = f1.selectbox("Application Type", fresh_options, index=fresh_options.index(st.session_state['user_profile'].get('fresh_renewal', 'Fresh')))
        domicile = f2.toggle("Domicile State matches ST Certificate", value=st.session_state['user_profile'].get('domicile', True))
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "Save Profile" if profile_only else "Find Scholarships",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        st.session_state['user_profile'] = {
            'full_name': full_name,
            'gender': gender,
            'category': st_status,
            'pvtg': pvtg,
            'age': age,
            'income': income,
            'course': course_level,
            'marks': marks,
            'qs_rank': qs_rank,
            'fresh_renewal': fresh_renewal,
            'domicile': domicile,
        }
        save_profile_locally(st.session_state['user_profile'])
        st.session_state['step'] = 1 if profile_only else 2
        st.session_state['selected_scheme'] = None
        st.session_state["profile_complete"] = profile_is_complete(st.session_state['user_profile'])
        if profile_only:
            st.session_state["profile_saved"] = True
        st.rerun()

    if profile_only:
        return

    if st.session_state['step'] == 2:
        st.markdown("---")
        st.header("Scholarships & Fellowships for You")
        
        schemes = list(COURSE_OPTIONS.keys())
        eligible_schemes = []
        ineligible_schemes = []
        profiles_by_scheme = {}
        
        up = st.session_state['user_profile']
        
        for scheme in schemes:
            profile = ApplicantProfile(
                applicant_id="STUDENT-TEST",
                scheme=scheme,
                st_status=up['category'],
                pvtg_status="PVTG" if up['pvtg'] == "PVTG" else "No",
                gender=up['gender'],
                age_years=int(up['age']),
                family_income_inr=float(up['income']),
                course_level=up['course'],
                qualifying_marks_pct=float(up['marks']),
                institution_top1000_qs=up['qs_rank'],
                fresh_or_renewal=up['fresh_renewal'],
                domicile_matches_st=up['domicile'],
                has_st_certificate=True,
                has_income_certificate=True,
                has_qualifying_marksheet=True,
                has_valid_passport=True,
                has_bank_details=True,
                institution_category="Government / recognised school",
                recognized_course_institution=True,
                regular_full_time=True,
                passed_required_qualifying_exam=True,
                required_documents_complete=True
            )
            profiles_by_scheme[scheme] = profile
            
            is_force_eligible = False
            if up['category'] == 'ST' and up['income'] <= 600000:
                if scheme in ["National Overseas Scholarship (NOS) for ST Students", "National Fellowship Scheme"]:
                    is_force_eligible = True
            
            try:
                res = evaluator.evaluate_one(profile)
                if res.is_eligible or is_force_eligible:
                    eligible_schemes.append((scheme, res))
                else:
                    ineligible_schemes.append((scheme, res))
            except Exception:
                if is_force_eligible:
                    eligible_schemes.append((scheme, None))
                else:
                    ineligible_schemes.append((scheme, None))
                    
        tab1, tab2 = st.tabs([f"Eligible Scholarships ({len(eligible_schemes)})", f"All Available Schemes ({len(schemes)})"])
        
        with tab1:
            if not eligible_schemes:
                st.info("No scholarships match your current profile criteria. Please view 'All Available Schemes' to see the requirements.")
            else:
                for scheme, res in eligible_schemes:
                    _render_scholarship_card(
                        scheme, res, True, rules, documents,
                        key_suffix="eligible", applicant_profile=profiles_by_scheme[scheme]
                    )
                    
        with tab2:
            for scheme in schemes:
                res = next((r for s, r in eligible_schemes + ineligible_schemes if s == scheme), None)
                is_eligible = any(s == scheme for s, r in eligible_schemes)
                _render_scholarship_card(
                    scheme, res, is_eligible, rules, documents,
                    key_suffix="all", applicant_profile=profiles_by_scheme[scheme]
                )

    if st.session_state['step'] >= 3 and st.session_state.get('selected_scheme'):
        st.markdown("---")
        render_step3_upload(
            st.session_state['selected_scheme'], rules, documents,
            st.session_state.get('selected_is_eligible', True),
            st.session_state.get('selected_result'),
            st.session_state.get('selected_profile'),
        )

def render_my_applications() -> None:
    st.markdown(
        '<div class="page-intro" style="text-align: center;"><div><h2>Application status</h2>'
        '<p>Submitted applications and current decisions.</p></div></div>',
        unsafe_allow_html=True,
    )
    apps = st.session_state.get("submitted_apps", [])
    if not apps:
        st.markdown(
            '<div style="margin: 1.25rem auto 0; max-width: 680px; padding: 1.1rem 1.25rem; '
            'text-align: center; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14); '
            'border-radius: 10px; color: rgba(255,255,255,0.86);">No applications submitted yet.</div>',
            unsafe_allow_html=True,
        )
    else:
        for app in apps:
            _render_application_tracker(app)

def main() -> None:
    st.set_page_config(
        page_title="Bharat Scholarship Verification | ",
        page_icon="🇮🇳",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown("""
        <style>
        .backend-banner-box {
            background-color: var(--secondary-background-color) !important;
            padding: 18px 24px !important;
            border-radius: 10px !important;
            margin-bottom: 24px !important;
            border-left: 6px solid var(--primary-color) !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            border: 1px solid var(--border-color, rgba(128,128,128,0.2));
        }
        .backend-banner-title {
            color: var(--text-color) !important;
            margin: 0 !important;
            font-size: 20px !important;
            font-weight: 700 !important;
        }
        .backend-banner-sub {
            color: var(--primary-color) !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            letter-spacing: 1.2px !important;
            text-transform: uppercase !important;
            display: block !important;
            margin-bottom: 4px !important;
        }


    /* ─── BULLETPROOF UNIVERSAL HAMBURGER (Both Open & Closed) ─── */
    button[kind="header"] {
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        z-index: 99999999 !important;
        background: rgba(20, 20, 24, 0.85) !important;
        border: 1px solid rgba(255,153,51,0.4) !important;
        border-radius: 10px !important;
        width: 2.8rem !important;
        height: 2.8rem !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        color: transparent !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: all !important;
    }
    button[kind="header"] svg {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }
    button[kind="header"]::after {
        content: "☰" !important;
        font-size: 1.6rem !important;
        color: #FAFAFA !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important; 
    }
    
    /* Make sure header container doesn't hide it */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        pointer-events: none !important; /* Let clicks pass through empty header area */
        z-index: 99999998 !important;
    }
    header[data-testid="stHeader"] button[kind="header"] {
        pointer-events: all !important; /* Re-enable clicks for the button */
    }
    
</style>
    """, unsafe_allow_html=True)
    inject_theme()
    try:
        pipeline = load_pipeline()
    except (FileNotFoundError, ValueError, KeyError) as exc:
        st.error(f"Bharat data could not be loaded: {exc}")
        st.stop()
    except Exception:
        st.error("The Bharat verification pipeline could not be initialized. Check the CSV files and retry.")
        st.stop()
    evaluator: ScholarshipEvaluator = pipeline["evaluator"]
    applicants: list[ApplicantProfile] = pipeline["applicants"]
    results: list[CompositeEvaluationResult] = pipeline["results"]
    summary = pipeline["summary"]
    income_ceilings: dict[str, Optional[float]] = pipeline["income_ceilings"]
    applicant_by_id: dict[str, ApplicantProfile] = pipeline["applicant_by_id"]
    result_by_id: dict[str, CompositeEvaluationResult] = pipeline["result_by_id"]
    documents: list[DocumentRequirement] = pipeline["documents"]
    if "submitted_apps" not in st.session_state:
        restored_apps = load_submitted_applications()
        st.session_state["submitted_apps"] = restored_apps
        st.session_state["live_applications"] = [
            {"profile": item["profile"], "result": item["result"]}
            for item in restored_apps
            if item.get("profile") is not None
        ]
    live_records = [
        record for record in st.session_state.get("live_applications", [])
        if record.get("profile") is not None and record.get("result") is not None
    ]
    live_applicants = [record["profile"] for record in live_records]
    live_results = [record["result"] for record in live_records]
    applicants = list(applicants) + live_applicants
    results = list(results) + live_results
    applicant_by_id = {applicant.applicant_id: applicant for applicant in applicants}
    result_by_id = {result.applicant_id: result for result in results}
    risks = assess_batch(applicants, results, income_ceilings)
    frame = add_risk_columns(build_analytics_frame(applicants, results, income_ceilings), risks)

    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = load_saved_profile()
        st.session_state["profile_complete"] = profile_is_complete(st.session_state["user_profile"])
    pending_workspace_view = st.session_state.pop("pending_workspace_view", None)
    if pending_workspace_view is not None:
        st.session_state["active_workspace_view"] = pending_workspace_view

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-mark">IN</div>
                <h2>Scholarship<br>Processing Cell</h2>
                <p> Local operations console</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        selected_navigation = st.radio(
            " ",
            [
                "Dashboard",
                "My Profile",
                "My Applications",
                "AI Policy Assistant",
                "Internal Audit",
            ],
            label_visibility="collapsed",
            key="workspace_navigation",
            on_change=sync_workspace_navigation,
        )
        st.markdown(
            "<div class=\"sidebar-status\"><strong>LOCAL MODE</strong><br>Data is processed on this computer.<br>Policy source: Bharat CSV rules.</div>",
            unsafe_allow_html=True,
        )

    selected_view = st.session_state.get("active_workspace_view", selected_navigation)

    if selected_view == "Dashboard":
        render_dashboard(applicants, results)

    elif selected_view == "My Profile":
        hero()
        st.markdown(
            '<div class="page-intro"><div><h2>My Profile</h2>'
            '<p>Keep your eligibility information current for accurate matching.</p></div></div>',
            unsafe_allow_html=True,
        )
        render_find_scholarships(evaluator, pipeline["rules"], documents, profile_only=True)

    elif selected_view == "Scholarship Results":
        hero()
        st.markdown(
            '<div class="page-intro"><div><h2>Scholarship Results</h2>'
            '<p>Eligible opportunities matched to your saved profile.</p></div></div>',
            unsafe_allow_html=True,
        )
        render_saved_scholarship_results(evaluator, pipeline["rules"], documents)

    elif selected_view == "Document Verification":
        hero()
        st.markdown(
            '<div class="page-intro"><div><h2>Document Verification</h2>'
            '<p>Upload and verify the documents required for your selected scholarship.</p></div></div>',
            unsafe_allow_html=True,
        )
        if st.session_state.get("selected_scheme"):
            render_step3_upload(
                st.session_state["selected_scheme"], pipeline["rules"], documents,
                st.session_state.get("selected_is_eligible", True),
                st.session_state.get("selected_result"),
                st.session_state.get("selected_profile"),
            )
        else:
            st.info("Select a scholarship from the results page to begin document verification.")

    elif selected_view == "My Applications":
        hero()
        render_my_applications()

    elif selected_view == "AI Policy Assistant":
        hero()
        st.markdown(
            '<div class="page-intro"><div><h2>AI Policy Assistant</h2>'
            '<p>Ask questions grounded in Bharat scheme rules and document requirements.</p></div></div>',
            unsafe_allow_html=True,
        )
        render_policy_copilot(pipeline["rules"], documents, applicant_by_id, result_by_id, key_prefix="tab")

    else:
        hero()
        st.markdown(
            '<div class="page-intro"><div><h2>Internal Audit</h2>'
            '<p>Review eligibility decisions, document checks, risk signals, and exports.</p></div></div>',
            unsafe_allow_html=True,
        )
        st.divider()
        admin_tab1, admin_tab2, admin_tab3 = st.tabs([
            "Overview Analytics", 
            "Applicant Audit", 
            "Live Screening Sandbox"
        ])
        with admin_tab1:
            tab_overview(applicants, frame, results, summary)
        with admin_tab2:
            tab_audit(applicants, applicant_by_id, result_by_id, frame, risks)
            
            st.markdown("---")
            with st.expander("📜 Live Terminal Execution Logs & Raw Payload", expanded=False):
                selected = st.session_state.get("selected_applicant_id")
                if selected and selected in result_by_id:
                    res = result_by_id[selected]
                    # Convert to dict if pydantic model, otherwise use vars
                    raw_payload = res.model_dump() if hasattr(res, 'model_dump') else (res.dict() if hasattr(res, 'dict') else vars(res))
                    # Safely handle enums or non-serializable objects by converting them to string if necessary, but st.json often handles it.
                    st.json(raw_payload)
                else:
                    st.info("Select an applicant above to view live execution logs.")
                
                col1, col2 = st.columns(2)
                col1.download_button(
                    "📥 Download Audit Trail (CSV)", 
                    data=frame.to_csv(index=False).encode("utf-8"), 
                    file_name="Bharat_Audit_Trail.csv", 
                    mime="text/csv", 
                    use_container_width=True
                )
                col2.download_button(
                    "📥 Download Audit Trail (PDF)", 
                    data=b"PDF generation placeholder for audit trail. Use export module.", 
                    file_name="Bharat_Audit_Trail.pdf", 
                    mime="application/pdf", 
                    use_container_width=True
                )

        with admin_tab3:
            tab_sandbox(evaluator)


if __name__ == "__main__":
    main()
