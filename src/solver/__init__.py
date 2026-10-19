"""Решатель задач MedAssist: триаж, диагностика, маршрутизация, объяснение."""

from .api import ROLES, solve
from .dialog import apply_answers, pending_inputs, run_dialog
from .knowledge import KnowledgeBase, load_default_kb

__all__ = ["solve", "apply_answers", "pending_inputs", "run_dialog", "ROLES", "KnowledgeBase", "load_default_kb"]
