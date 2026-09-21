<!-- Сгенерировано scripts/generate_docs.py из kb/_schema/schema.yaml. Не редактировать вручную. -->

# Типы связей между документами (v2)
Автор записывает связь в одном направлении. Обратная связь материализуется загрузчиком по таблице ниже; если обе стороны записаны явно, валидатор проверяет их согласованность.

| Тип | Обратный | От (категории) | К (категории) | Симметр. |
|---|---|---|---|---|
| `has_symptom` | `symptom_of` | disease, emergency | symptom |  |
| `symptom_of` | `has_symptom` | symptom | disease, emergency |  |
| `diagnosed_by` | `diagnoses` | disease, emergency, symptom, redflag | exam |  |
| `diagnoses` | `diagnosed_by` | exam | disease, emergency, symptom, redflag |  |
| `has_red_flag` | `red_flag_for` | disease, symptom, emergency, difdiag, routing | redflag |  |
| `red_flag_for` | `has_red_flag` | redflag | disease, symptom, emergency, difdiag, routing |  |
| `uses_exam` | `exam_used_in` | protocol, checklist, follow_up, screening, routing, emergency_p, difdiag | exam |  |
| `exam_used_in` | `uses_exam` | exam | protocol, checklist, follow_up, screening, routing, emergency_p, difdiag |  |
| `differentiates_from` | `differentiates_from` | disease, emergency | disease, emergency | да |
| `considers` | `considered_in` | difdiag | disease, emergency, redflag |  |
| `considered_in` | `considers` | disease, emergency, redflag | difdiag |  |
| `differential_for` | `has_differential` | difdiag | symptom |  |
| `has_differential` | `differential_for` | symptom | difdiag |  |
| `complicates` | `complicated_by` | disease, redflag, emergency | disease |  |
| `complicated_by` | `complicates` | disease | disease, redflag, emergency |  |
| `associated_with` | `associated_with` | любая | любая | да |
| `protocol_for` | `has_protocol` | protocol | disease, emergency |  |
| `has_protocol` | `protocol_for` | disease, emergency | protocol |  |
| `emergency_protocol_for` | `has_emergency_protocol` | emergency_p | emergency, redflag, disease, protocol, routing, follow_up |  |
| `has_emergency_protocol` | `emergency_protocol_for` | emergency, redflag, disease, protocol, routing, follow_up | emergency_p |  |
| `routing_for` | `has_routing` | routing | disease, emergency, symptom, protocol, patient_info, checklist |  |
| `has_routing` | `routing_for` | disease, emergency, symptom, protocol, patient_info, checklist | routing |  |
| `assessed_by` | `assesses` | disease, emergency, protocol, routing, symptom, emergency_p, follow_up, checklist, screening | scale |  |
| `assesses` | `assessed_by` | scale | disease, emergency, protocol, routing, symptom, emergency_p, follow_up, checklist, screening |  |
| `checklist_for` | `has_checklist` | checklist | disease, protocol |  |
| `has_checklist` | `checklist_for` | disease, protocol | checklist |  |
| `screening_for` | `has_screening` | screening | disease, protocol |  |
| `has_screening` | `screening_for` | disease, protocol | screening |  |
| `follow_up_for` | `has_follow_up` | follow_up | disease, protocol |  |
| `has_follow_up` | `follow_up_for` | disease, protocol | follow_up |  |
| `patient_info_for` | `has_patient_info` | patient_info | disease, protocol, drug, emergency, nonpharm |  |
| `has_patient_info` | `patient_info_for` | disease, protocol, drug, emergency, nonpharm | patient_info |  |
| `next_step` | `previous_step` | routing, protocol, emergency_p, screening, scale, follow_up | routing, protocol, emergency_p, follow_up |  |
| `previous_step` | `next_step` | routing, protocol, emergency_p, follow_up | routing, protocol, emergency_p, screening, scale, follow_up |  |
| `treats` | `treated_with` | regimen, drug, drugclass, nonpharm | disease, emergency, symptom |  |
| `treated_with` | `treats` | disease, emergency, symptom | regimen, drug, drugclass, nonpharm |  |
| `recommends` | `recommended_by` | protocol, emergency_p, follow_up, routing, scale | regimen, drug, drugclass, nonpharm |  |
| `recommended_by` | `recommends` | regimen, drug, drugclass, nonpharm | protocol, emergency_p, follow_up, routing, scale |  |
| `includes` | `included_in` | regimen, drugclass | drug, drugclass, nonpharm |  |
| `included_in` | `includes` | drug, drugclass, nonpharm | regimen, drugclass |  |
| `has_interaction` | `interaction_for` | drug, drugclass | interaction |  |
| `interaction_for` | `has_interaction` | interaction | drug, drugclass |  |
| `causes_adr` | `adr_caused_by` | drug, drugclass | adr |  |
| `adr_caused_by` | `causes_adr` | adr | drug, drugclass |  |
| `dose_adjusted_by` | `dose_adjustment_for` | drug, drugclass, regimen | dosing |  |
| `dose_adjustment_for` | `dose_adjusted_by` | dosing | drug, drugclass, regimen |  |
| `contraindicated_in` | `contraindicates` | drug, drugclass, exam | disease, profile |  |
| `contraindicates` | `contraindicated_in` | disease, profile | drug, drugclass, exam |  |
| `defines` | `defined_by` | glossary | любая |  |
| `defined_by` | `defines` | любая | glossary |  |
| `applies_to_profile` | `profile_applies_to` | любая | profile |  |
| `profile_applies_to` | `applies_to_profile` | profile | любая |  |
| `belongs_to_system` | `system_includes` | любая | anatomy |  |
| `system_includes` | `belongs_to_system` | anatomy | любая |  |

## Соответствие типам схемы v1
| Тип v1 | Тип v2 |
|---|---|
| `related_to` | `associated_with` |
| `requires_exam` | `diagnosed_by` |
| `confirmed_by` | `diagnosed_by` |
| `excluded_by` | `diagnosed_by` |
| `uses_redflag` | `has_red_flag` |
| `requires_attention` | `has_red_flag` |
| `may_indicate` | `symptom_of` |
| `managed_by_protocol` | `has_protocol` |
| `treated_by` | `treated_with` |
| `used_by_protocol` | `recommended_by` |
| `uses_protocol` | `has_protocol` |
| `uses_routing` | `has_routing` |
| `influences_routing` | `next_step` |
| `uses_scale` | `assessed_by` |
| `uses_checklist` | `has_checklist` |
| `uses_screening` | `has_screening` |
| `uses_follow_up` | `has_follow_up` |
| `uses_regimen` | `recommends` |
| `uses_drug` | `recommends` |
| `uses_drugclass` | `includes` |
| `uses_vaccine` | `recommends` |
| `regimen_for` | `treats` |
| `used_for` | `treats` |
| `nonpharm_for` | `treats` |
| `includes_drug` | `includes` |
| `includes_nonpharm` | `includes` |
| `drug_in_regimen` | `included_in` |
| `used_by_regimen` | `included_in` |
| `belongs_to_class` | `included_in` |
| `class_contains_drug` | `includes` |
| `may_cause_adr` | `causes_adr` |
| `adverse_reaction_for` | `adr_caused_by` |
| `requires_dose_adjustment` | `dose_adjusted_by` |
