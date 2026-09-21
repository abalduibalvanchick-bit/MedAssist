---
id: GLB-PROFILE-004
schema_version: 2
title: Дети и подростки (до 18 лет)
domain: glb
category: profile
body_system:
- multisystem
tags:
- profile
- pediatrics
- boundary
urgency: routine
access_level: professional
target_specialist:
- pediatrician
age_group:
- neonate
- infant
- child
- adolescent
relations: []
criteria:
  param: age
  op: <
  value: 18
considerations:
- нормы АД, ЧСС и ЧДД зависят от возраста и не совпадают со взрослыми порогами
- дозирование препаратов по массе тела
- шкалы CURB-65, ACT (взрослая версия), MIDAS валидированы для взрослых
- решатель MedAssist ориентирован на взрослых; для детей выдаётся ограничение применимости
sources:
- WHO. Pocket book of hospital care for children, 2nd ed., 2013.
- 'Fleming S. et al. Normal ranges of heart rate and respiratory rate in children from birth to 18 years of age: a systematic review of observational studies. Lancet. 2011;377:1011–1018.'
clinical_guidelines:
- WHO Pocket book of hospital care for children, 2013
last_medical_review: '2026-09-16'
medical_reviewer: модельная верификация (учебный проект)
author: Инженеры знаний №1 и №3
version: '2.0'
date_created: '2026-09-16'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Дети и подростки (до 18 лет)

> ⚕️ **Дисклеймер**: Профиль фиксирует границу применимости базы знаний и не содержит педиатрических рекомендаций.

## Определение группы
К профилю относятся пациенты младше 18 лет. Формальный критерий: возраст менее 18 лет.

## Почему профиль важен
Пороговые значения артериального давления, частоты сердечных сокращений и частоты дыхания у детей зависят от возраста и отличаются от взрослых. Большинство шкал, представленных в базе знаний (CURB-65, взрослая версия ACT, MIDAS), валидированы для взрослых. Дозы препаратов у детей рассчитываются по массе тела.

## Граница применимости
Карточки базы знаний MedAssist подготовлены для взрослых пациентов. Для пациентов из этого профиля решатель сообщает об ограничении применимости и рекомендует консультацию педиатра, а не выдаёт заключение по взрослым порогам.

## Источники
1. WHO. Pocket book of hospital care for children, 2nd ed., 2013.
2. Fleming S. et al. Normal ranges of heart rate and respiratory rate in children from birth to 18 years of age: a systematic review of observational studies. Lancet. 2011;377:1011–1018.
