---
id: GLB-GLOSSARY-022
schema_version: 2
title: Маршрутизация пациента
domain: glb
category: glossary
body_system:
- multisystem
tags:
- glossary
- routing
urgency: routine
access_level: professional
target_specialist:
- all_specialties
age_group:
- all_ages
synonyms:
- маршрутизация
- маршрут пациента
- направление к специалисту
relations:
- target: PROT-ROUTING-001
  type: defines
  description: выведено из машиночитаемого слоя (refers_to)
- target: PROT-ROUTING-002
  type: defines
  description: выведено из машиночитаемого слоя (refers_to)
- target: PROT-ROUTING-003
  type: defines
  description: выведено из машиночитаемого слоя (refers_to)
- target: PROT-ROUTING-004
  type: defines
  description: выведено из машиночитаемого слоя (refers_to)
- target: PROT-ROUTING-005
  type: defines
  description: выведено из машиночитаемого слоя (refers_to)
- target: PROT-ROUTING-006
  type: defines
  description: выведено из машиночитаемого слоя (refers_to)
term: Маршрутизация пациента
definition: 'Определение уровня и срочности медицинской помощи: амбулаторное ведение, срочное направление к специалисту, госпитализация или экстренная помощь.'
refers_to:
- PROT-ROUTING-001
- PROT-ROUTING-002
- PROT-ROUTING-003
- PROT-ROUTING-004
- PROT-ROUTING-005
- PROT-ROUTING-006
sources:
- Международная классификация болезней 11-го пересмотра (МКБ-11). Всемирная организация здравоохранения, 2022.
- Клинические рекомендации Минздрава РФ, соответствующие нозологии (рубрикатор cr.minzdrav.gov.ru), редакции 2023–2024.
clinical_guidelines:
- Рубрикатор клинических рекомендаций Минздрава РФ
last_medical_review: '2026-09-16'
medical_reviewer: модельная верификация (учебный проект)
author: Инженеры знаний №1 и №3
version: '2.1'
date_created: '2026-09-16'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Маршрутизация пациента — Patient routing

## Определение
Определение уровня и срочности медицинской помощи: амбулаторное ведение, срочное направление к специалисту, госпитализация или экстренная помощь.

## Определение для пациента
Решение о том, куда и насколько срочно пациенту нужно обратиться.

## Синонимы и сокращения
маршрутизация, маршрут пациента, направление к специалисту.

## Контекст использования
Термин используется в карточках: [[PROT-ROUTING-001]], [[PROT-ROUTING-002]], [[PROT-ROUTING-003]], [[PROT-ROUTING-004]], [[PROT-ROUTING-005]], [[PROT-ROUTING-006]]. Синонимы применяются поисковым модулем и распознаванием запросов на естественном языке.
