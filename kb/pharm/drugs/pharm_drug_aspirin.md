---
id: PHARM-DRUG-011
schema_version: 2
title: Ацетилсалициловая кислота – Аспирин Кардио, ТромбоАСС
domain: pharm
category: drug
atc_code: B01AC06
inn: Acetylsalicylic acid
body_system:
- cardiovascular
- hematologic
tags:
- antiplatelet
- aspirin
- ihd
- acs
urgency: routine
access_level: professional
target_specialist:
- therapist
- cardiologist
- emergency_physician
age_group:
- adult
- elderly
relations:
- target: PHARM-DRUGCLASS-011
  type: included_in
  description: относится к фармакологической группе
- target: DIAG-DISEASE-002
  type: treats
  description: применяется по назначению врача
- target: DIAG-EMERGENCY-001
  type: treats
  description: применяется по назначению врача
- target: PHARM-REGIMEN-003
  type: included_in
  description: входит в терапевтическую схему
contraindications:
- when:
    fact: gi_bleeding_history
  absolute: false
  explanation: ЖКТ-кровотечение в анамнезе — гастропротекция и оценка риска
- when:
    fact: on_anticoagulants
  absolute: false
  explanation: повышенный риск кровотечения
- when:
    any:
    - fact: known_asthma
    - disease: DIAG-DISEASE-004
  absolute: false
  explanation: возможна аспириновая астма
interactions:
- with: PHARM-DRUGCLASS-010
  severity: moderate
indications:
- DIAG-DISEASE-002
- DIAG-EMERGENCY-001
sources:
- Byrne R.A. et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44:3720–3826.
- Vrints C. et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45:3415–3537.
clinical_guidelines:
- 2023 ESC Guidelines for the management of acute coronary syndromes
- 2024 ESC Guidelines for the management of chronic coronary syndromes
last_medical_review: '2026-09-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.0'
date_created: '2026-09-30'
date_updated: '2026-09-30'
status: approved
disclaimer: true
---

# Ацетилсалициловая кислота – Аспирин Кардио, ТромбоАСС

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не заменяет консультацию врача.

## Общие сведения
Антиагрегант, основа профилактики сердечно-сосудистых событий при ИБС и неотложной терапии острого коронарного синдрома.

## Механизм действия
Необратимо ацетилирует ЦОГ-1 тромбоцитов и подавляет синтез тромбоксана A2 на весь срок жизни тромбоцита (7–10 дней).

## Фармакокинетика
Быстро всасывается, антиагрегантный эффект разжёванной таблетки — через 15–30 минут; кишечнорастворимые формы действуют медленнее.

## Показания
- ИБС (вторичная профилактика);
- острый коронарный синдром;
- после реваскуляризации миокарда.

## Дозирование
Длительно: 75–100 мг 1 раз в сутки. При ОКС: 150–300 мг однократно разжевать (некишечнорастворимая форма), затем 75–100 мг в сутки.

## Противопоказания
Активное кровотечение, геморрагический диатез, аллергия на салицилаты; с осторожностью — язвенный анамнез, приём антикоагулянтов, аспириновая астма.

## Побочные эффекты
Диспепсия, эрозии и кровотечения ЖКТ, повышенная кровоточивость, бронхоспазм у предрасположенных.

## Лекарственные взаимодействия
Ибупрофен может снижать антиагрегантный эффект; с антикоагулянтами и НПВС — риск кровотечения.

## Взаимодействие с пищей / алкоголем
Алкоголь повышает риск кровотечения из ЖКТ.

## Беременность и лактация
Низкие дозы допустимы по показаниям (в том числе профилактика преэклампсии); в III триместре высокие дозы противопоказаны.

## Мониторинг терапии
Признаки кровотечения, гемоглобин; при язвенном анамнезе — ингибитор протонной помпы.

## Передозировка
Шум в ушах, тошнота, метаболический ацидоз, нарушение сознания.

## Сравнение с аналогами в группе
Клопидогрел — альтернатива при непереносимости; при ОКС применяется в комбинации с ингибитором P2Y12.

## Информация для пациента
Не прекращайте приём без согласования с врачом. При чёрном стуле или рвоте с кровью срочно обратитесь за помощью.

## Связанные документы
- [[PHARM-DRUGCLASS-011]] Антитромбоцитарные препараты (антиагреганты) — относится к фармакологической группе
- [[DIAG-DISEASE-002]] Ишемическая болезнь сердца — применяется по назначению врача
- [[DIAG-EMERGENCY-001]] Острый коронарный синдром — применяется по назначению врача
- [[PHARM-REGIMEN-003]] Схема лечения хронической ишемической болезни сердца (стабильная стенокардия) — входит в терапевтическую схему

## Источники
1. Byrne R.A. et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44:3720–3826.
2. Vrints C. et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45:3415–3537.
