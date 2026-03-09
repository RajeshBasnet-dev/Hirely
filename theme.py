"""Design tokens and UI helpers for the Hirely Streamlit dashboard."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HirelyTheme:
    primary: str = "#5B8CFF"
    secondary: str = "#22C55E"
    accent: str = "#F97316"
    bg: str = "#0B1220"
    surface: str = "#111A2E"
    surface_alt: str = "#1A2540"
    text: str = "#E2E8F0"
    muted: str = "#94A3B8"


THEMES = {
    "Dark": HirelyTheme(),
    "Light": HirelyTheme(
        primary="#4263EB",
        secondary="#16A34A",
        accent="#EA580C",
        bg="#F8FAFC",
        surface="#FFFFFF",
        surface_alt="#EEF2FF",
        text="#0F172A",
        muted="#475569",
    ),
}


def inject_css(theme: HirelyTheme) -> str:
    return f"""
    <style>
    .stApp {{
        background: {theme.bg};
        color: {theme.text};
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}
    .block-container {{padding-top: 1rem; padding-bottom: 2rem; max-width: 1300px;}}
    [data-testid='stSidebar'] {{
        background: {theme.surface};
        border-right: 1px solid {theme.surface_alt};
    }}
    .hirely-shell {{
        border: 1px solid {theme.surface_alt};
        background: linear-gradient(180deg, {theme.surface}, {theme.bg});
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1rem;
    }}
    .hirely-logo {{font-size: 1.35rem; font-weight: 800; margin: 0;}}
    .hirely-subtitle {{color: {theme.muted}; margin: 0.2rem 0 0.8rem 0;}}
    .hirely-card {{
        background: {theme.surface};
        border: 1px solid {theme.surface_alt};
        border-radius: 16px;
        padding: 0.95rem;
        box-shadow: 0 10px 30px rgba(2, 8, 20, 0.2);
    }}
    .hirely-kpi-label {{font-size: 0.8rem; color: {theme.muted}; margin: 0;}}
    .hirely-kpi-value {{font-size: 1.55rem; font-weight: 750; margin: 0.15rem 0; color: {theme.text};}}
    .hirely-pill {{
        display: inline-block;
        border-radius: 999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.78rem;
        color: white;
        background: {theme.primary};
    }}
    .hirely-footer {{
        margin-top: 2rem;
        color: {theme.muted};
        font-size: 0.85rem;
        text-align: center;
    }}
    .stButton > button, .stDownloadButton > button {{
        border-radius: 12px;
        border: 1px solid {theme.surface_alt};
    }}
    div[data-testid='stMetricValue'] {{font-weight: 700;}}
    </style>
    """
