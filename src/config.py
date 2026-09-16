"""Настройки MVP MedAssist.

Начиная со схемы v2 все сведения о структуре базы знаний (домены, категории,
перечисления, типы связей, обязательные поля) читаются из kb/_schema/schema.yaml
через модуль src.schema. Здесь остаются только пути, служебные исключения и
константы совместимости для карточек схемы v1, которые ещё не мигрированы.
"""

from __future__ import annotations

from pathlib import Path

from .schema import load_schema

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KB_ROOT = PROJECT_ROOT / "kb"
RULES_ROOT = KB_ROOT / "rules"

SCHEMA = load_schema(KB_ROOT / "_schema" / "schema.yaml")

# Файлы и папки, которые не являются карточками знаний.
EXCLUDED_FILE_NAMES = {"index.md", "README.md"}
EXCLUDED_DIR_NAMES = {"templates", "_schema", "rules"}

# ---------------------------------------------------------------------------
# Совместимость со схемой v1 (карточки без поля schema_version).
# После завершения миграции этот блок удаляется вместе с ветвью v1 в валидаторе.
# ---------------------------------------------------------------------------
REQUIRED_FIELDS_V1 = [
    "id", "title", "domain", "category", "body_system", "tags", "urgency",
    "access_level", "target_specialist", "age_group", "related", "sources",
    "clinical_guidelines", "last_medical_review", "author", "version",
    "date_created", "date_updated", "status", "disclaimer",
]
REQUIRED_FIELDS = REQUIRED_FIELDS_V1  # устаревшее имя, используется старыми тестами

# Устаревшие имена папок доменов (v1) -> канонический код домена (v2).
LEGACY_DOMAIN_FOLDERS = {"diagnostics": "diag", "therapy": "pharm", "protocols": "prot", "global": "glb"}

# Разрешённые значения. В режиме v1 допускаются устаревшие синонимы.
ALLOWED_DOMAINS = set(SCHEMA.domain_codes) | set(SCHEMA.legacy_domain_aliases)
ALLOWED_DIAGNOSTIC_CATEGORIES = SCHEMA.categories_of_domain("diag")
ALLOWED_PHARM_CATEGORIES = SCHEMA.categories_of_domain("pharm") | set(SCHEMA.legacy_category_aliases)
ALLOWED_PROTOCOL_CATEGORIES = SCHEMA.categories_of_domain("prot")
ALLOWED_GLOBAL_CATEGORIES = SCHEMA.categories_of_domain("glb")
ALLOWED_URGENCY = set(SCHEMA.enum("urgency"))
ALLOWED_STATUS = set(SCHEMA.enum("status"))

# Соответствие подпапки и категории (v2) плюс устаревшие имена v1.
FOLDER_CATEGORY_RULES = dict(SCHEMA.folder_category_rules())

# Типы связей: канонические v2 плюс устаревшие v1 (только для карточек v1).
ALLOWED_RELATION_TYPES = set(SCHEMA.relation_types) | set(SCHEMA.legacy_relation_aliases)
