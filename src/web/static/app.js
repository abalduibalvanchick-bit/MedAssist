"use strict";

const byId = (id) => document.getElementById(id);
const node = (tag, text, className) => {
  const item = document.createElement(tag);
  if (text != null) item.textContent = text;
  if (className) item.className = className;
  return item;
};

const views = {
  professional: {
    title: "Разбор случая",
    intro: "Введите данные или загрузите учебный случай, чтобы увидеть оценку и её основания.",
    measurements: "Основные измерения", symptoms: "Симптомы",
    primary: ["age", "temperature", "spo2", "sbp", "dbp", "hr"],
    action: "Разобрать случай", result: "Срочность, гипотезы и подробности решения.",
    reference: "Задайте вопрос по всей базе знаний. Ниже доступны карточки, правила и демонстрации.",
    sections: [["diagnosis", "Диагностика"], ["care", "Протоколы и наблюдение"],
      ["therapy", "Терапия и безопасность"], ["reasoning", "Обоснование"]],
  },
  nursing: {
    title: "Измерения и наблюдение",
    intro: "Начните с измерений. В результате сначала появятся срочность, маршрут и тревожные признаки.",
    measurements: "Показатели для наблюдения", symptoms: "Наблюдаемые симптомы",
    primary: ["age", "sbp", "dbp", "hr", "rr", "spo2", "temperature", "glucose"],
    action: "Разобрать случай", result: "Срочность, обследования и план наблюдения.",
    reference: "Задайте вопрос по доступным карточкам и памяткам. Полная база доступна в режиме специалиста.",
    sections: [["care", "Обследования и наблюдение"], ["diagnosis", "Диагностическая оценка"],
      ["therapy", "Терапия и безопасность"], ["reasoning", "Обоснование"]],
  },
  student: {
    title: "Учебный разбор",
    intro: "Загрузите сценарий и проследите, какие факты запустили правила и как появились гипотезы.",
    measurements: "Измерения в сценарии", symptoms: "Признаки учебного случая",
    primary: ["age", "temperature", "spo2", "sbp", "dbp", "hr"],
    action: "Запустить учебный разбор", result: "Ход вывода и разбор гипотез по шагам.",
    reference: "Ищите по доступным карточкам или откройте каталог правил вывода.",
    sections: [["reasoning", "Как решатель пришёл к выводу"], ["diagnosis", "Гипотезы и шкалы"],
      ["care", "Протоколы и наблюдение"], ["therapy", "Терапия и безопасность"]],
  },
  patient: {
    title: "Жалобы и срочность",
    intro: "Выберите, что беспокоит, и внесите известные измерения. Неизвестные значения можно оставить пустыми.",
    measurements: "Что уже измерили", symptoms: "Что беспокоит",
    primary: ["age", "temperature", "sbp", "dbp", "hr", "spo2", "glucose"],
    action: "Посмотреть оценку", result: "Насколько срочно нужна помощь, куда обратиться и что сделать дальше.",
    reference: "Задайте вопрос по памяткам для пациентов.",
    sections: [["advice", "Памятки для пациента"], ["reasoning", "Что учтено при оценке"]],
  },
};
const commonSymptoms = ["DIAG-SYMPTOM-002", "DIAG-SYMPTOM-001", "DIAG-SYMPTOM-008",
  "DIAG-SYMPTOM-004", "DIAG-SYMPTOM-003", "DIAG-SYMPTOM-005", "DIAG-SYMPTOM-014"];
const showAllSymptoms = {professional: false, nursing: false, student: false, patient: false};
const currentRole = () => document.querySelector('input[name="role"]:checked').value;
const currentView = () => views[currentRole()];
const extraKinds = ["param", "fact", "exam_result", "feature"];
const extraLabels = {symptom: "Жалобы", feature: "Характер жалоб", param: "Измерения",
  fact: "Самочувствие и анамнез", exam_result: "Известные результаты обследований"};
const patientLabels = {
  sbp: "Верхнее давление", dbp: "Нижнее давление", hr: "Пульс", spo2: "Насыщение крови кислородом",
  "dyspnea.cyanosis": "Посинели губы или кожа",
  "dyspnea.unable_full_sentences": "Из-за одышки трудно говорить целыми фразами",
  "dyspnea.accessory_muscles": "При дыхании заметно напрягаются мышцы груди или шеи",
  glucose: "Глюкоза крови", confusion: "Есть ли спутанность сознания?",
  "DIAG-SYMPTOM-006": "Повышенная жажда", "DIAG-SYMPTOM-007": "Частое мочеиспускание",
  "DIAG-SYMPTOM-010": "Внезапное нарушение речи, движений или чувствительности",
};
const patientRoutes = {outpatient: "Амбулаторно, через поликлинику", urgent_referral: "К профильному специалисту",
  hospitalization: "В стационар", emergency: "Скорая медицинская помощь"};
let catalog;
let patient = {};
let extraCodes = [];
let revision = 0;
let referenceRevision = 0;
let selectedExample = "";
let hasCaseResult = false;
let questionsFinished = false;
let lastSolution;
let lastUpdate;
let knowledgeRevision = 0;
let cardRevision = 0;
let caseReturn;
let knowledgeData;
const groups = {example: "Учебные примеры", published: "По публикации",
  typical: "Типовые", boundary: "Граничные", negative: "Проверки ошибок"};
const domains = {diag: "Диагностика", pharm: "Фармакология", prot: "Протоколы", glb: "Общие знания"};
const caseEmpty = byId("result-content").cloneNode(true);
const referenceEmpty = byId("answer").cloneNode(true);

function emptyResult(id, template) {
  const output = byId(id);
  output.className = template.className;
  output.replaceChildren(...[...template.children].map((child) => child.cloneNode(true)));
}

async function request(path, body) {
  const options = body === undefined ? {} : {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body),
  };
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Запрос не выполнен.");
  return data;
}

function showError(id, message = "") {
  const error = byId(id);
  error.textContent = message;
  error.hidden = !message;
}

function showView() {
  const view = location.hash === "#reference" ? "reference" : "case";
  byId("reference-view").hidden = view !== "reference";
  byId("case-view").hidden = view !== "case";
  for (const link of document.querySelectorAll("[data-view]")) {
    const active = link.dataset.view === view;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
}

function asList(value) {
  return Array.isArray(value) ? value : typeof value === "string" ? [value] : [];
}

function boolValue(yes, no, code) {
  if (asList(yes).includes(code)) return true;
  if (asList(no).includes(code)) return false;
  return null;
}

function fieldValue(field) {
  const {code, kind} = field;
  if (kind === "param") return patient.params?.[code] ?? (code === "age" ? patient.age : null);
  if (kind === "fact") return patient.facts?.[code];
  if (kind === "exam_result") return patient.exam_results?.[code];
  if (kind === "feature") return boolValue(patient.features, patient.denied_features, code);
  return boolValue(patient.symptoms, patient.denied_symptoms, code);
}

function setField(field, value) {
  const {code, kind} = field;
  if (kind === "symptom" || kind === "feature") {
    const yes = kind === "symptom" ? "symptoms" : "features";
    const no = "denied_" + yes;
    patient[yes] = asList(patient[yes]).filter((item) => item !== code);
    patient[no] = asList(patient[no]).filter((item) => item !== code);
    if (value != null) patient[value ? yes : no].push(code);
  } else {
    const group = {param: "params", fact: "facts", exam_result: "exam_results"}[kind];
    patient[group] ??= {};
    if (code === "age") delete patient.age;
    if (value == null) delete patient[group][code];
    else patient[group][code] = value;
  }
}

function control(field, initial) {
  const input = node(field.type === "number" ? "input" : "select");
  input.setAttribute("aria-label", fieldName(field));
  if (field.type === "number") {
    input.type = "number";
    input.step = "any";
    input.placeholder = field.unit || "—";
    if (field.min != null) input.min = field.min;
    if (field.max != null) input.max = field.max;
  } else {
    input.add(new Option("Не указано", ""));
    const options = field.type === "boolean"
      ? [{value: "true", label: "Да"}, {value: "false", label: "Нет"}] : field.options;
    for (const item of options) input.add(new Option(item.label, item.value));
  }
  input.value = initial ?? "";
  return input;
}

function readControl(input, field) {
  if (input.value === "") return null;
  if (field.type === "number") return input.valueAsNumber;
  if (field.type === "boolean") return input.value === "true";
  return input.value;
}

function fieldName(field) {
  return (currentRole() === "patient" && patientLabels[field.code]) || field.label;
}

function edit() {
  revision += 1;
  hasCaseResult = false;
  lastSolution = lastUpdate = undefined;
  questionsFinished = false;
  selectedExample = "";
  byId("scenario-info").hidden = true;
  syncRawCase();
  showError("case-error");
  emptyResult("result-content", caseEmpty);
}

function fieldLabel(field, callback, initial) {
  const name = fieldName(field);
  const label = node("label", field.unit ? `${name}, ${field.unit}` : name);
  const input = control(field, initial);
  if (callback) input.addEventListener(field.type === "number" ? "input" : "change",
    () => callback(readControl(input, field)));
  label.append(input);
  return [label, input];
}

function renderPrimary() {
  const controls = currentView().primary.map((code) => {
    const field = catalog.fields.param.find((item) => item.code === code);
    return fieldLabel(field, (value) => { setField(field, value); edit(); }, fieldValue(field))[0];
  });
  byId("primary-fields").replaceChildren(...controls);
}

function symptomOn(field) {
  return fieldValue(field) === true || catalog.fields.feature.some((f) => f.symptom === field.code && fieldValue(f) === true);
}

function renderSymptoms() {
  const container = byId("symptoms");
  const focusCode = document.activeElement?.dataset.code;
  container.replaceChildren();
  const role = currentRole();
  const expanded = showAllSymptoms[role];
  const toggle = byId("toggle-symptoms");
  toggle.hidden = catalog.fields.symptom.length <= commonSymptoms.length;
  toggle.setAttribute("aria-expanded", String(expanded));
  toggle.textContent = expanded ? "Свернуть список" : `Все симптомы (${catalog.fields.symptom.length})`;
  for (const field of catalog.fields.symptom) {
    if (!expanded && fieldValue(field) == null && !symptomOn(field) && !commonSymptoms.includes(field.code)) continue;
    const button = node("button", fieldName(field), "chip");
    button.type = "button";
    button.dataset.code = field.code;
    const value = fieldValue(field);
    button.dataset.state = value === false ? "no" : symptomOn(field) ? "yes" : "";
    button.setAttribute("aria-pressed", String(symptomOn(field)));
    if (value === false) button.textContent += " · нет";
    button.addEventListener("click", () => {
      const selected = symptomOn(field);
      setField(field, selected ? null : true);
      if (selected) {
        for (const feature of catalog.fields.feature.filter((f) => f.symptom === field.code)) setField(feature, null);
      }
      edit();
      renderSymptoms();
      renderExtra();
    });
    container.append(button);
  }
  if (focusCode) [...container.children].find((button) => button.dataset.code === focusCode)?.focus();
  const active = new Set(catalog.fields.symptom.filter(symptomOn).map((field) => field.code));
  const features = catalog.fields.feature.filter((field) => active.has(field.symptom) && fieldValue(field) != null);
  const content = features.map((field) => fieldLabel(field, (value) => {
    setField(field, value); edit(); renderSymptoms(); renderExtra();
  }, fieldValue(field))[0]);
  for (const code of active) {
    const available = catalog.fields.feature.filter((field) => field.symptom === code && fieldValue(field) == null);
    if (!available.length) continue;
    const label = node("label", fieldName(catalog.fields.symptom.find((field) => field.code === code)));
    const select = node("select");
    select.setAttribute("aria-label", "Добавить признак для " + label.textContent);
    select.add(new Option("Добавить признак", ""));
    for (const field of available) select.add(new Option(field.label, field.code));
    select.addEventListener("change", () => {
      const field = available.find((f) => f.code === select.value);
      if (!field) return;
      setField(field, true); edit(); renderSymptoms(); renderExtra();
    });
    label.append(select);
    content.push(label);
  }
  byId("features").replaceChildren(...content);
}

function renderExtra() {
  const primaryCodes = currentView().primary;
  const root = byId("extra-controls");
  root.replaceChildren();
  const fieldChoices = extraKinds.flatMap((kind) => catalog.fields[kind])
    .filter((field) => !primaryCodes.includes(field.code) && (field.kind !== "feature" || fieldValue(field) == null));
  fieldChoices.unshift(...catalog.fields.symptom.filter((field) => fieldValue(field) == null),
    ...catalog.fields.symptom.filter((field) => fieldValue(field) === false));
  const allExtras = extraKinds.flatMap((kind) => catalog.fields[kind]).concat(catalog.fields.symptom);
  const codes = new Set([...extraCodes, ...allExtras
    .filter((field) => !primaryCodes.includes(field.code) &&
      (field.kind === "symptom" ? fieldValue(field) === false :
        field.kind === "feature" ? fieldValue(field) === false &&
          !symptomOn(catalog.fields.symptom.find((symptom) => symptom.code === field.symptom)) : fieldValue(field) != null))
    .map((field) => field.code)]);
  for (const code of codes) {
    const field = allExtras.find((item) => item.code === code);
    if (!field) continue;
    const row = node("div", null, "extra-row");
    const [, input] = fieldLabel(field, (value) => {
      setField(field, value); edit();
      if (field.kind === "symptom" || field.kind === "feature") renderSymptoms();
    }, fieldValue(field));
    const remove = node("button", "Убрать", "text-btn");
    remove.type = "button";
    remove.setAttribute("aria-label", "Убрать " + field.label);
    remove.addEventListener("click", () => {
      setField(field, null);
      extraCodes = extraCodes.filter((id) => id !== code);
      edit(); renderSymptoms(); renderExtra();
    });
    row.append(node("span", field.unit ? `${fieldName(field)}, ${field.unit}` : fieldName(field)), input, remove);
    root.append(row);
  }
  const select = node("select");
  const description = currentRole() === "patient"
    ? "Добавить жалобу, измерение или результат" : "Добавить параметр, факт или обследование";
  select.setAttribute("aria-label", description);
  select.add(new Option(description, ""));
  for (const [kind, title] of Object.entries(extraLabels)) {
    const group = node("optgroup");
    group.label = title;
    for (const field of fieldChoices.filter((item) => item.kind === kind && !codes.has(item.code))) {
      group.append(new Option(fieldName(field), field.code));
    }
    if (group.children.length) select.append(group);
  }
  select.addEventListener("change", () => {
    if (!select.value) return;
    extraCodes.push(select.value);
    renderExtra();
    root.querySelector(".extra-row:last-of-type input, .extra-row:last-of-type select")?.focus();
  });
  root.append(select);
}

function syncForm(openDetails = false) {
  renderPrimary();
  renderSymptoms();
  renderExtra();
  renderDiseases();
  for (const option of byId("medications").options) option.selected = asList(patient.medications).includes(option.value);
  syncRawCase();
  if (openDetails) document.querySelector(".extra").open = true;
}

function syncRawCase() {
  const raw = byId("raw-case");
  raw.hidden = !selectedExample && !Object.keys(patient).length;
  byId("raw-json").textContent = JSON.stringify(patient, null, 2);
}

function renderDiseases() {
  const selected = asList(patient.diseases);
  const choices = byId("diseases");
  for (const option of choices.options) option.disabled = selected.includes(option.value);
  choices.value = "";
  const container = byId("selected-diseases");
  container.replaceChildren();
  for (const code of selected) {
    const name = catalog.diseases.find((item) => item.id === code)?.title || code;
    const remove = node("button", name + " ×", "chip");
    remove.type = "button";
    remove.setAttribute("aria-label", "Убрать диагноз: " + name);
    remove.addEventListener("click", () => {
      patient.diseases = selected.filter((item) => item !== code);
      edit();
      renderDiseases();
      choices.focus();
    });
    container.append(remove);
  }
}

function filterText(value) {
  return value.toLowerCase().replaceAll("ё", "е").trim();
}

function renderScenarioList() {
  if (!catalog) return;
  const group = byId("scenario-group").value;
  const query = filterText(byId("scenario-search").value);
  const list = byId("scenario-list");
  const selected = list.value;
  list.replaceChildren();
  for (const [kind, heading] of Object.entries(groups)) {
    if (group && kind !== group) continue;
    const cases = catalog.examples.filter((entry) => entry.group === kind &&
      filterText([entry.title, entry.code || "", entry.id].join(" ")).includes(query));
    if (!cases.length) continue;
    const section = node("optgroup");
    section.label = heading;
    for (const entry of cases) section.append(new Option(
      entry.code ? entry.code + " · " + entry.title : entry.title, entry.id));
    list.append(section);
  }
  const count = list.options.length;
  list.value = selected;
  if (!list.value && count) list.selectedIndex = 0;
  byId("load-scenario").disabled = !count;
  byId("scenario-count").textContent = count ? `${count} из ${catalog.examples.length}` : "Сценарии не найдены";
}

function addList(root, title, texts, collapsible = false) {
  if (!texts?.length) return;
  const section = node(collapsible ? "details" : "section");
  section.append(node(collapsible ? "summary" : "h3", title));
  const list = node("ul");
  for (const text of texts) list.append(node("li", text));
  section.append(list);
  root.append(section);
}

function renderQuestions(root, data) {
  const {questions = [], outcome} = data.solution;
  const role = currentRole();
  const emergency = outcome.kind === "emergency";
  if (role === "patient" && emergency) return;
  const needsData = outcome.kind === "incomplete";
  if (!questions.length && !needsData) return;
  const section = node("details", null, "result-group questions-group");
  section.open = !emergency && (needsData || outcome.provisional || role === "nursing" || role === "patient");
  section.append(node("summary", emergency ? "Уточнения для последующего разбора" : "Что можно уточнить"));
  section.id = "result-questions";
  const buckets = [
    {title: "Срочность и маршрут", kinds: ["safety_check", "routing"], open: true},
    {title: "Симптомы и оценка", kinds: []},
    {title: "Применимость протоколов", kinds: ["protocol"]},
    {title: "Безопасность терапии", kinds: ["therapy"]},
  ].map((bucket) => ({...bucket, fields: [], texts: new Set()}));
  const fieldCodes = new Set();
  for (const bucket of buckets) {
    for (const question of questions) {
      const target = buckets.find((entry) => entry.kinds.includes(question.kind)) || buckets[1];
      if (target !== bucket) continue;
      if (question.text) bucket.texts.add(question.text);
      for (const field of question.inputs || []) {
        if (fieldCodes.has(field.code) || (field.type === "choice" && !field.options?.length)) continue;
        fieldCodes.add(field.code);
        bucket.fields.push(field);
      }
    }
  }
  if (questionsFinished && fieldCodes.size) {
    section.open = true;
    const resume = node("button", "Вернуться к вопросам", "secondary edit-case");
    resume.type = "button";
    resume.addEventListener("click", () => {
      questionsFinished = false;
      renderSolution(data);
      root.querySelector(".questions-group details[open] input, .questions-group details[open] select")?.focus();
    });
    section.append(node("p", "Оценка показана по введённым данным. Пропущенные ответы остаются неизвестными."), resume);
    root.append(section);
    return;
  }
  const content = node(fieldCodes.size ? "form" : "div", null, "question-content");
  const controls = [];
  const visible = buckets.filter((bucket) => bucket.fields.length || bucket.texts.size);
  const firstInput = visible.find((bucket) => bucket.fields.length);
  for (const bucket of visible) {
    const group = node("details", null, "question-bucket");
    group.open = bucket.open || bucket === firstInput;
    group.append(node("summary", bucket.title + (bucket.fields.length ? ` · ${bucket.fields.length}` : "")));
    if (bucket.fields.length) {
      const grid = node("div", null, "question-grid");
      bucket.fields.sort((a, b) => (b.priority || 0) - (a.priority || 0));
      for (const field of bucket.fields) {
        const [label, input] = fieldLabel(field);
        grid.append(label);
        controls.push([field, input]);
      }
      group.append(grid);
    }
    addList(group, "Зачем нужны эти сведения", [...bucket.texts], Boolean(bucket.fields.length));
    content.append(group);
  }
  if (!visible.length) content.append(node("p", "Можно внести другие известные жалобы, измерения или результаты обследований."));
  if (fieldCodes.size) {
    const form = content;
    const apply = node("button", "Пересчитать с ответами", "primary");
    apply.type = "submit";
    const finish = node("button", "Завершить уточнения", "secondary");
    finish.type = "button";
    const actions = node("div", null, "question-actions");
    actions.append(apply, finish);
    form.append(actions);
    const message = node("div", null, "message error");
    message.hidden = true;
    message.setAttribute("role", "alert");
    form.append(message);
    const readAnswers = () => Object.fromEntries(controls
        .map(([field, input]) => [field.code, readControl(input, field)]).filter(([, value]) => value != null));
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const answers = readAnswers();
      message.hidden = Boolean(Object.keys(answers).length);
      if (!message.hidden) {
        message.textContent = "Заполните хотя бы одно уточнение.";
        return;
      }
      await solveCase(answers, apply, message);
    });
    finish.addEventListener("click", async () => {
      const answers = readAnswers();
      if (Object.keys(answers).length) {
        await solveCase(answers, finish, message, true, true);
      } else {
        questionsFinished = true;
        renderSolution(data);
        root.querySelector(".case-outcome h3").focus();
      }
    });
  } else if (needsData) {
    const editCase = node("button", "Дополнить данные", "secondary edit-case");
    editCase.type = "button";
    editCase.addEventListener("click", () => {
      if (!catalog) return;
      showAllSymptoms[currentRole()] = true;
      renderSymptoms();
      document.querySelector(".extra").open = true;
      byId("symptoms").querySelector("button")?.focus();
    });
    section.append(editCase);
  }
  section.append(content);
  root.append(section);
}

function subsection(title, key) {
  const group = node("details", null, "result-group");
  group.id = "result-" + key;
  group.append(node("summary", title), node("div", null, "result-group-body"));
  return group;
}

function renderOutcome(root, result, role) {
  const {outcome, routing} = result;
  const tone = outcome.kind === "invalid" ? "error"
    : outcome.provisional || result.urgency?.level === "urgent" ? "urgent" : "";
  const block = node("div", null, `case-outcome message ${outcome.kind} ${tone}`);
  const title = node("h3", outcome.title);
  title.tabIndex = -1;
  block.append(title);
  if (outcome.summary) block.append(node("p", outcome.summary));
  const route = role === "patient" ? patientRoutes[routing?.route] || routing?.label : routing?.label;
  const facts = [
    ["Срочность", outcome.urgency || (route && outcome.provisional ? "Уточняется" : null)],
    [outcome.provisional ? "Предварительный маршрут" : role === "patient" ? "Куда обратиться" : "Маршрут", route],
    [outcome.provisional ? "Предварительный срок" : "Когда", route ? routing.timeframe || "Пока не определён" : null],
  ].filter(([, value]) => value);
  if (facts.length) {
    const list = node("dl", null, "outcome-facts");
    for (const [label, value] of facts) {
      const row = node("div");
      row.append(node("dt", label), node("dd", value));
      list.append(row);
    }
    block.append(list);
  }
  if (outcome.next_step) block.append(node("p", outcome.next_step, "outcome-next"));
  root.append(block);
}

function listItems(root, title, items, render, open = false) {
  if (!items?.length) return;
  const group = node("details", null, "detail-list");
  group.open = open;
  const list = node("ul", null, "item-list");
  for (const item of items) {
    const entry = node("li");
    render(entry, item);
    list.append(entry);
  }
  group.append(node("summary", title), list);
  root.append(group);
}

function bulletList(items) {
  const list = node("ul");
  list.append(...items.map((item) => node("li", item)));
  return list;
}

function textLine(root, label, value) {
  if (!value) return;
  const line = node("p", null, "detail-line");
  line.append(node("strong", label), document.createTextNode(" " + value));
  root.append(line);
}

function formatValue(field, value) {
  if (typeof value === "boolean") return value ? "да" : "нет";
  if (field.type === "choice") return field.options.find((item) => item.value === value)?.label || value;
  return [value, field.unit].filter((item) => item != null && item !== "").join(" ");
}

function renderMeasurements(root) {
  const fields = (catalog?.fields.param || []).filter((field) => fieldValue(field) != null);
  if (!fields.length) return;
  const section = node("section", null, "role-highlight");
  const list = node("dl", null, "measurement-list");
  for (const field of fields) {
    const pair = node("div");
    pair.append(node("dt", fieldName(field)), node("dd", formatValue(field, fieldValue(field))));
    list.append(pair);
  }
  section.append(node("h3", "Уже измерено"), list);
  root.append(section);
}

function openReferenceFromCase(button) {
  caseReturn = button;
  byId("back-to-case").hidden = false;
  location.hash = "reference";
  showView();
}

byId("back-to-case").addEventListener("click", () => {
  location.hash = "case";
  showView();
  if (caseReturn?.isConnected) moveTo(caseReturn);
  else moveTo(byId("case-form-title"));
});

const traceKinds = {input: "Входные данные", profile: "Профиль", scale: "Шкала", redflag: "Красный флаг",
  emergency: "Неотложное состояние", rule: "Правило", routing: "Маршрутизация", ranking: "Оценка гипотезы",
  protocol: "Протокол", differential: "Дифференциальная диагностика", therapy: "Терапия"};

function renderTrace(root, result, role) {
  if (!result.explanation) return;
  const details = node("details", null, "trace-view");
  details.open = role === "student";
  details.append(node("summary", "Ход вывода"));
  if (result.trace?.length) {
    const list = node("ol", null, "trace-list");
    list.tabIndex = 0;
    list.setAttribute("aria-label", "Шаги хода вывода");
    for (const step of result.trace) {
      const entry = node("li");
      entry.append(node("small", `${traceKinds[step.kind] || step.kind} · ${step.source}`), node("h4", step.title));
      if (step.because.length) {
        entry.append(node("strong", "На каких данных"), bulletList(step.because));
      }
      if (step.effects.length) {
        entry.append(node("strong", "Что получилось"), bulletList(step.effects));
      }
      if (step.kind === "rule" && (role === "student" || role === "professional")) {
        const link = node("button", "Открыть " + step.source, "text-btn");
        link.type = "button";
        link.addEventListener("click", () => {
          openReferenceFromCase(link);
          openKnowledge("knowledge-rules", step.source);
        });
        entry.append(link);
      }
      list.append(entry);
    }
    details.append(list);
  }
  const raw = node("details");
  const trace = node("pre", result.explanation, "result-trace");
  trace.tabIndex = 0;
  raw.append(node("summary", "Полная текстовая трасса"), trace);
  details.append(raw);
  root.append(details);
}

function moveTo(element) {
  if (element.tagName === "DETAILS") element.open = true;
  const target = element.querySelector(":scope > summary") || element;
  target.focus({preventScroll: true});
  target.scrollIntoView({block: "start"});
}

function renderResultNav(root, sections) {
  const nav = node("nav", null, "result-nav");
  nav.setAttribute("aria-label", "Разделы результата");
  for (const section of sections) {
    const button = node("button", section.querySelector("summary").textContent, "secondary");
    button.type = "button";
    button.addEventListener("click", () => moveTo(section));
    nav.append(button);
  }
  const expand = node("button", "Раскрыть все разделы", "text-btn");
  expand.type = "button";
  expand.addEventListener("click", () => {
    for (const detail of root.querySelectorAll("details")) detail.open = true;
  });
  const editLink = node("button", "К данным пациента", "text-btn");
  editLink.type = "button";
  editLink.addEventListener("click", () => moveTo(byId("case-form-title")));
  nav.append(expand, editLink);
  return nav;
}

function renderRouteEvidence(root, result) {
  const routing = result.routing;
  const origins = new Set(routing?.sources || []);
  const decisive = (routing?.decisions || []).filter((item) => origins.has(item.id) && item.route === routing.route);
  const evidence = [...new Set(decisive.flatMap((item) => item.because || []))];
  if (!evidence.length) {
    for (const step of result.trace || []) {
      if (origins.has(step.source) && step.kind !== "routing") evidence.push(...step.because);
    }
  }
  if (evidence.length) {
    const content = node("div", null, "route-evidence");
    const clean = (fact) => fact.replace(/^Клиническая шкала: /, "")
      .replace(/ = (\d+)\.0(?=\s|$)/g, " = $1")
      .replace(/ = (\d+) \(= \1\)$/, " — $1");
    content.append(node("h4", "Что определило маршрут"), bulletList([...new Set(evidence.map(clean))]));
    root.append(content);
  }
}

function renderSolution(data) {
  const result = data.solution;
  const root = byId("result-content");
  const role = currentRole();
  root.className = "output";
  root.replaceChildren();
  byId("back-to-case").hidden = true;
  caseReturn = undefined;
  const routing = result.routing;
  renderOutcome(root, result, role);
  if (lastUpdate) root.append(node("p", lastUpdate, "update-note"));
  if (role !== "patient" && result.routing?.route) renderRouteEvidence(root.firstElementChild, result);
  addList(root, "Замечания к данным", (result.input_issues || []).concat(data.answer_issues || []).map((item) => item.message));
  const disclaimers = result.disclaimer?.filter((text) => text !== result.outcome.next_step);
  if (result.status === "invalid" || result.status === "refused") {
    addList(root, "Справочная информация", disclaimers, true);
    return;
  }
  addList(root, role === "patient" ? "Выявленные тревожные признаки" : "Тревожные признаки и неотложные состояния",
    [...(result.red_flags || []), ...(role === "patient" ? [] : result.emergencies || [])].map((item) => item.title));

  if (role === "professional" && result.hypotheses?.length) {
    const preview = node("p", "Первая гипотеза · " + result.hypotheses[0].title, "result-preview");
    root.append(preview);
  }
  if (role === "nursing" && result.exams?.length) {
    const preview = node("p", "Предложено обследований · " + result.exams.length, "result-preview");
    root.append(preview);
  }
  if (role === "student" && result.trace?.length) {
    root.append(node("p", "Шагов вывода · " + result.trace.length, "result-preview"));
  }
  if (role === "nursing") renderMeasurements(root);

  const groups = {};
  for (const [key, title] of currentView().sections) groups[key] = subsection(title, key);
  const panel = (key) => groups[key]?.lastElementChild;
  const diagnosis = panel("diagnosis");
  if (diagnosis) {
    addList(diagnosis, "Профили", result.profiles?.map((item) => item.title), true);
    addList(diagnosis, "Рабочие диагнозы", result.working_diagnoses?.map((item) => item.title), true);
    listItems(diagnosis, "Гипотезы", result.hypotheses, (entry, item) => {
      entry.append(node("h4", item.title));
      const rank = item.rank_score ?? item.score;
      textLine(entry, "Оценка гипотезы", `${rank} · вес сработавших правил ${item.score}`);
      const names = (sign) => item.arguments.filter((argument) => sign * argument.contribution > 0)
        .map((argument) => `${argument.title} (${sign > 0 ? "+" : "−"}${Math.abs(argument.contribution)})`).join(", ");
      textLine(entry, "За", names(1));
      textLine(entry, "Против", names(-1));
    }, role === "professional");
    for (const table of result.differential || []) {
      listItems(diagnosis, table.title, table.branches, (entry, branch) => {
        entry.append(node("h4", branch.title), node("p", branch.label, "item-status"));
        textLine(entry, "За", branch.for.join(", "));
        textLine(entry, "Против", branch.against.join(", "));
        const exam = branch.key_exam;
        if (exam?.recommended) textLine(entry, exam.completed ? "Уже выполнено" : "Ключевое обследование", exam.title);
      });
    }
    listItems(diagnosis, "Шкалы", result.scales, (entry, item) => {
      entry.append(node("h4", item.title));
      textLine(entry, "Баллы шкалы", `${item.value ?? item.range.join("–")} · ${item.category_label}`);
      addList(entry, "Как посчитано", item.items?.map((part) =>
        [part.label, `${part.points ?? "нет данных"} балл.`, part.detail].filter(Boolean).join(" · ")), true);
    });
  }

  const care = panel("care");
  if (care) {
    const examRoles = {confirms: "подтверждение", excludes: "исключение", supports: "поддержка гипотезы",
      stratifies: "оценка тяжести", monitors: "наблюдение"};
    const exams = result.exams?.map((item) =>
      [item.title, item.roles.map((value) => examRoles[value] || value).join(", ")].filter(Boolean).join(" · "));
    addList(care, "Обследования", exams, role !== "nursing");
    addList(care, "Выполненные обследования", result.completed_exams?.map((item) =>
      [item.title, ...item.results.map((value) => `${value.label} — ${value.value}`)].join(" · ")), true);
    addList(care, "Обследования после стабилизации", result.deferred_exams?.map((item) => item.title), true);
    const conditions = {conditional: "нужно уточнить применимость", not_required: "не требуется",
      not_applicable: "не применяется"};
    for (const item of result.protocols || []) {
      addList(care, item.title, [
        conditions[item.status],
        ...(item.steps || []).map((step) => [step.action, conditions[step.status]].filter(Boolean).join(" · ")),
        ...(item.phases || []).flatMap((phase) => phase.steps.map((step) => `${phase.window} · ${step}`)),
      ].filter(Boolean), true);
    }
    addList(care, "Наблюдение", result.follow_up?.flatMap((item) => [
      item.title, ...(item.schedule || []).map((row) => [row.after, row.interval, row.purpose].filter(Boolean).join(" · ")),
    ]), role !== "nursing");
    listItems(care, "Основания маршрутизации", routing?.decisions, (entry, item) => {
      entry.append(node("h4", item.title));
      textLine(entry, "Маршрут", [item.label, item.timeframe].filter(Boolean).join(" · "));
      if (item.because?.length) {
        entry.append(node("strong", "Условия, которые сработали"), bulletList(item.because));
      }
      textLine(entry, "Описание строки в базе", item.explanation);
      addList(entry, "Действия по этой строке", item.actions);
      if (item.source_available) {
        const link = node("button", "Источник маршрута · " + item.title, "text-btn");
        link.type = "button";
        link.addEventListener("click", () => {
          openReferenceFromCase(link);
          byId("question").value = "Какие основания и действия указаны в выбранной строке маршрута?";
          submitReference({id: item.id, row: item.row}, true);
        });
        entry.append(link);
      }
    });
  }

  const therapy = panel("therapy");
  if (therapy) {
    for (const regimen of result.therapy?.regimens || []) {
      listItems(therapy, regimen.title,
        regimen.lines.flatMap((line) => line.options.map((option) => ({...option, line: line.line}))),
        (entry, option) => {
          entry.append(node("h4", option.title));
          textLine(entry, "Линия " + option.line, option.label);
          if (option.note) entry.append(node("p", option.note));
          const reasons = [...option.reasons, ...option.dose_notes].map((r) => `${r.text} [${r.source}]`);
          if (reasons.length) entry.append(bulletList(reasons));
        });
    }
    addList(therapy, "Взаимодействия", result.therapy?.interactions?.map((item) => item.title + " · " + item.text), true);
    addList(therapy, "Предупреждения", result.warnings?.map((item) => item.text), true);
  }

  const advice = panel("advice");
  if (advice) addList(advice, "Когда нужна срочная помощь", [...new Set(
    (result.advice || []).flatMap((item) => item.seek_help_when))]);

  const reasoning = panel("reasoning");
  if (role === "patient") {
    const symptoms = catalog.fields.symptom.filter((field) => fieldValue(field) != null || symptomOn(field));
    const details = [...catalog.fields.feature, ...catalog.fields.fact].filter((field) => fieldValue(field) != null);
    const measurements = catalog.fields.param.filter((field) => fieldValue(field) != null);
    const showValue = (value) => typeof value === "boolean" ? (value ? "да" : "нет") : value;
    addList(reasoning, "Жалобы и ответы", symptoms.map((field) =>
      fieldName(field) + (fieldValue(field) === false ? " — нет" : " — да")));
    addList(reasoning, "Уточнения по жалобам", details.map((field) =>
      `${fieldName(field)} — ${showValue(fieldValue(field))}`));
    addList(reasoning, "Введённые значения", measurements.map((field) =>
      [`${fieldName(field)} — ${showValue(fieldValue(field))}`, field.unit].filter(Boolean).join(" ")));
  } else {
    const reasons = result.urgency?.reasons || [];
    listItems(reasoning, "Основания оценки срочности", reasons, (entry, item) => {
      const step = result.trace?.find((row) => row.source === item.source && row.because.length);
      if (step) entry.append(bulletList(step.because));
      textLine(entry, "Источник", [item.source, item.reason].filter(Boolean).join(" · "));
    });
    renderTrace(reasoning, result, role);
  }
  const available = Object.values(groups).filter((group) => group.lastElementChild.children.length);
  if (available.length && (role !== "patient" || advice?.children.length)) available[0].open = true;
  const position = root.children.length;
  const leadingPanel = role === "student" && available[0] === groups.reasoning ? available.shift() : null;
  // Экстренный итог и тревожные признаки всегда остаются первыми.
  if (leadingPanel && result.outcome.kind !== "emergency") root.append(leadingPanel);
  renderQuestions(root, data);
  if (leadingPanel && result.outcome.kind === "emergency") root.append(leadingPanel);
  root.append(...available);
  const navigation = [...root.children].filter((element) => element.classList.contains("result-group"));
  if (navigation.length) root.insertBefore(renderResultNav(root, navigation), root.children[position]);
  addList(root, "Справочная информация", disclaimers, true);
}

async function solveCase(answers, button, inlineError, focusResult = true, finishQuestions = false) {
  const stamp = ++revision;
  showError("case-error");
  if (inlineError) inlineError.hidden = true;
  button.disabled = true;
  try {
    const data = await request("/api/solve", {patient, answers, role: currentRole()});
    if (stamp !== revision) return;
    if (inlineError && data.solution.status === "invalid") {
      inlineError.textContent = data.solution.input_issues.map((item) => item.message).join(" ");
      inlineError.hidden = false;
      return;
    }
    if (data.solution.status !== "invalid") {
      const fields = Object.values(catalog.fields).flat().filter((field) => Object.hasOwn(answers, field.code));
      const previous = fields.map((field) => fieldValue(field));
      patient = data.patient;
      if (fields.length) {
        const applied = fields.filter((field, index) => previous[index] !== fieldValue(field))
          .map((field) => `${fieldName(field)} — ${formatValue(field, fieldValue(field))}`);
        const route = (value) => currentRole() === "patient" ? patientRoutes[value?.route] || value?.label : value?.label;
        const before = route(lastSolution?.routing);
        const after = route(data.solution.routing);
        const notes = [];
        if (applied.length) notes.push("Учтены ответы — " + applied.join(", ") + ".");
        if (before !== after) {
          if (after) notes.push(before ? `Маршрут изменился (${before} → ${after}).` : `Определён маршрут — ${after}.`);
          else if (before) notes.push("По обновлённым данным маршрут пока не определён.");
        } else if (lastSolution?.outcome.provisional && !data.solution.outcome.provisional && after) {
          notes.push("Пометка о предварительности маршрута снята.");
        }
        lastUpdate = notes.join(" ");
      } else {
        lastUpdate = undefined;
      }
      lastSolution = data.solution;
      syncForm();
    }
    if (finishQuestions) questionsFinished = true;
    hasCaseResult = true;
    renderSolution(data);
    if (focusResult) {
      byId("case-results").querySelector(".case-outcome h3").focus();
    }
  } catch (error) {
    if (stamp === revision) {
      if (inlineError) {
        inlineError.textContent = error.message;
        inlineError.hidden = false;
      } else showError("case-error", error.message);
    }
  } finally {
    button.disabled = false;
  }
}

async function loadExample(example) {
  const stamp = ++revision;
  showError("case-error");
  try {
    const data = await request("/api/examples/" + example.id);
    if (stamp !== revision) return;
    patient = data.request.patient || data.request;
    selectedExample = data.title;
    hasCaseResult = false;
    lastSolution = lastUpdate = undefined;
    questionsFinished = false;
    const info = byId("scenario-info");
    info.replaceChildren(node("strong", data.title));
    if (data.note) info.append(node("p", data.note));
    if (data.source) {
      const link = node("a", "Открыть публикацию после проверки");
      link.href = data.source;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      info.append(link);
    }
    info.hidden = false;
    extraCodes = [];
    emptyResult("result-content", caseEmpty);
    syncForm(Boolean(patient.diseases?.length || patient.medications?.length ||
      Object.keys(patient.exam_results || {}).length));
  } catch (error) {
    if (stamp === revision) showError("case-error", error.message);
  }
}

function renderReference(result) {
  const root = byId("answer");
  root.className = "output";
  root.replaceChildren();
  if (result.status === "not_found") {
    root.append(node("div", "В базе знаний не нашлось достаточно сведений по этому вопросу.", "message"));
    const retry = node("button", "Уточнить вопрос", "text-btn");
    retry.type = "button";
    retry.addEventListener("click", () => moveTo(byId("question")));
    root.append(retry);
    return;
  }
  root.append(node("div", result.mode === "generated" ? "Выдержки из источников, отобранные моделью" : "Фрагменты из базы знаний", "message"));
  const modelNote = {unavailable: "Локальная модель не ответила. Приведены исходные выдержки.",
    invalid_evidence: "Модель не вернула проверяемую цитату. Приведены исходные выдержки."};
  if (modelNote[result.generation]) root.append(node("p", modelNote[result.generation]));
  const retrieval = result.sources[0]?.retrieval;
  if (retrieval === "hybrid_fallback") root.append(node("p", "Модель смыслового поиска недоступна. Показаны результаты локального поиска."));
  if (retrieval === "hybrid_semantic") root.append(node("p", "Порядок источников учитывает смысловую близость к вопросу."));
  for (const claim of result.answer) {
    const paragraph = node("p", claim.text + " ", "reference-excerpt");
    const link = node("a", "[" + claim.source + "]");
    link.href = "#source-" + claim.source;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      byId("source-" + claim.source)?.focus();
    });
    paragraph.append(link);
    root.append(paragraph);

  }
  const section = node("section");
  section.append(node("h3", "Источники"));
  const list = node("ul", null, "sources");
  for (const source of result.sources) {
    const item = node("li", null, "source");
    item.id = "source-" + source.n;
    item.tabIndex = -1;
    item.append(node("strong", `[${source.n}] ${source.title}`),
      node("small", source.id + " · " + source.section), node("p", source.excerpt, "reference-excerpt"));
    const fullCard = node("button", "Открыть карточку", "text-btn");
    fullCard.type = "button";
    fullCard.addEventListener("click", () => openKnowledge("knowledge", source.id));
    item.append(fullCard);
    list.append(item);
  }
  section.append(list);
  root.append(section);
}

async function submitReference(routeSource = null, focusAnswer = false) {
  const answer = byId("answer");
  answer.className = "output";
  answer.replaceChildren(node("p", "Поиск по базе знаний…", "message"));
  byId("reference-query").hidden = false;
  byId("reference-query").textContent = routeSource ? "Основание маршрута" : byId("question").value.trim();
  showError("reference-error");
  const stamp = ++referenceRevision;
  const button = byId("search-button");
  button.disabled = true;
  button.setAttribute("aria-busy", "true");
  try {
    const result = await request("/api/reference", {question: byId("question").value, role: currentRole(), route_source: routeSource});
    if (stamp === referenceRevision) {
      renderReference(result);
      if (focusAnswer || window.matchMedia("(max-width: 760px)").matches) moveTo(byId("answer-title"));
    }
  } catch (error) {
    if (stamp === referenceRevision) {
      emptyResult("answer", referenceEmpty);
      byId("reference-query").hidden = true;
      showError("reference-error", error.message);
    }
  } finally {
    if (stamp === referenceRevision) {
      button.disabled = false;
      button.removeAttribute("aria-busy");
    }
  }
}

byId("reference-form").addEventListener("submit", (event) => {
  event.preventDefault();
  submitReference();
});

function renderViewLabels() {
  const view = currentView();
  const role = currentRole();
  document.body.dataset.role = role;
  byId("case-title").textContent = view.title;
  byId("case-intro").textContent = view.intro;
  byId("primary-title").textContent = view.measurements;
  byId("symptom-title").textContent = view.symptoms;
  byId("solve-label").textContent = view.action;
  byId("result-hint").textContent = view.result;
  byId("reference-intro").textContent = view.reference;
  const suggestions = byId("suggestions");
  suggestions.replaceChildren();
  const questions = role === "professional"
    ? ["Из чего состоит шкала CURB-65?", "Куда обращаться при астме?", "Что означает пульсоксиметрия?"]
    : ["Памятка по бронхиальной астме", "Памятка по мигрени", "Памятка по артериальной гипертензии"];
  byId("question").placeholder = "Например, " + questions[0].replace(/^./u, (letter) => letter.toLowerCase());
  for (const text of questions) {
    const button = node("button", text);
    button.type = "button";
    button.addEventListener("click", () => {
      byId("question").value = text;
      byId("question").focus();
    });
    suggestions.append(button);
  }
  const symptoms = byId("symptom-section");
  const measurements = byId("primary-section");
  if (role === "nursing") symptoms.before(measurements);
  else measurements.before(symptoms);
  byId("examples").hidden = role === "patient";
}

function updateRoleViews() {
  const repeat = hasCaseResult;
  revision += 1;
  referenceRevision += 1;
  byId("search-button").disabled = false;
  byId("search-button").removeAttribute("aria-busy");
  renderViewLabels();
  if (catalog) syncForm();
  emptyResult("result-content", caseEmpty);
  emptyResult("answer", referenceEmpty);
  byId("reference-query").hidden = true;
  showError("case-error");
  showError("reference-error");
  loadKnowledge();
  if (repeat && catalog) solveCase({}, byId("solve-button"), null, false);
}

byId("role-chooser").addEventListener("change", updateRoleViews);
byId("toggle-symptoms").addEventListener("click", () => {
  const role = currentRole();
  showAllSymptoms[role] = !showAllSymptoms[role];
  if (catalog) renderSymptoms();
});
renderViewLabels();

byId("case-form").addEventListener("submit", (event) => {
  event.preventDefault();
  questionsFinished = false;
  if (catalog) solveCase({}, byId("solve-button"));
});

byId("clear").addEventListener("click", () => {
  patient = {};
  extraCodes = [];
  edit();
  if (catalog) syncForm();
});

byId("diseases").addEventListener("change", (event) => {
  if (!event.target.value) return;
  patient.diseases = [...new Set([...asList(patient.diseases), event.target.value])];
  edit();
  renderDiseases();
});

byId("medications").addEventListener("change", (event) => {
  patient.medications = [...event.target.selectedOptions].map((option) => option.value);
  edit();
});

window.addEventListener("hashchange", showView);
showView();

function knowledgePath(collection, id = "") {
  return "/api/" + collection + (id ? "/" + encodeURIComponent(id) : "") +
    "?role=" + encodeURIComponent(currentRole());
}

function renderKnowledgeList() {
  if (!knowledgeData) return;
  const list = byId("knowledge-list");
  const selected = list.value;
  const query = filterText(byId("knowledge-search").value);
  const domain = byId("knowledge-domain").value;
  list.replaceChildren();
  for (const card of knowledgeData.cards) {
    if (domain && card.domain !== domain) continue;
    if (!filterText([card.id, card.title, card.category, ...card.tags].join(" ")).includes(query)) continue;
    list.append(new Option(card.title + " · " + card.id, card.id));
  }
  list.value = selected;
  if (!list.value && list.options.length) list.selectedIndex = 0;
  byId("open-card").disabled = !list.value;
  byId("knowledge-count").textContent = `Найдено ${list.options.length} из ${knowledgeData.cards.length}`;
}

async function loadKnowledge() {
  const stamp = ++knowledgeRevision;
  cardRevision += 1;
  knowledgeData = undefined;
  byId("knowledge-content").replaceChildren(node("p", "Выберите карточку для просмотра."));
  byId("knowledge-list").replaceChildren();
  byId("open-card").disabled = true;
  byId("knowledge-demos").hidden = true;
  byId("knowledge-rules").hidden = true;
  try {
    const data = await request(knowledgePath("knowledge"));
    if (stamp !== knowledgeRevision) return;
    knowledgeData = data;
    renderKnowledgeList();
    const select = byId("knowledge-demo");
    select.replaceChildren(...Object.entries(data.demos).map(([id, label]) => new Option(label, id)));
    byId("knowledge-demos").hidden = !select.options.length;
    const rules = byId("knowledge-rule");
    rules.replaceChildren(...data.rules.map((rule) => new Option(rule.id + " · " + rule.title, rule.id)));
    byId("knowledge-rules").hidden = !rules.options.length;
  } catch (error) {
    if (stamp === knowledgeRevision) byId("knowledge-content").textContent = error.message;
  }
}

function appendKnowledgeText(root, content, title) {
  // Показываем заголовки и исходный текст карточки без вставки HTML.
  for (const block of content.trim().split(/\n\s*\n/)) {
    const lines = block.trim().split("\n");
    const heading = lines[0].match(/^#{1,6}\s+(.+)$/);
    if (heading && heading[1] !== title) root.append(node("h4", heading[1]));
    const body = (heading ? lines.slice(1) : lines).join("\n").replace(/\*\*/g, "").trim();
    if (body) root.append(node("p", body, "knowledge-text"));
  }
}

async function openKnowledge(collection, id) {
  if (!id) return;
  const stamp = ++cardRevision;
  byId("knowledge-browser").open = true;
  const root = byId("knowledge-content");
  root.replaceChildren(node("p", "Загрузка…"));
  try {
    const card = await request(knowledgePath(collection, id));
    if (stamp !== cardRevision) return;
    root.replaceChildren(node("h3", card.title));
    if (card.id) root.append(node("p", card.id, "knowledge-id"));
    if (card.content) appendKnowledgeText(root, card.content, card.title);
    if (card.metadata) {
      const formal = node("details");
      formal.append(node("summary", "Машиночитаемые данные"),
        node("pre", JSON.stringify(card.metadata, null, 2), "knowledge-formal"));
      root.append(formal);
    }
    addList(root, "Источники", card.sources);
    if (card.related?.length) {
      const section = node("section");
      section.append(node("h4", "Связанные карточки"));
      const list = node("ul");
      for (const ref of card.related) {
        const item = node("li");
        const button = node("button", ref.title + " · " + ref.id, "text-btn");
        button.type = "button";
        button.addEventListener("click", () => openKnowledge("knowledge", ref.id));
        item.append(button);
        list.append(item);
      }
      section.append(list);
      root.append(section);
    }
    root.focus();
  } catch (error) {
    if (stamp === cardRevision) root.textContent = error.message;
  }
}

byId("scenario-group").addEventListener("change", renderScenarioList);
byId("scenario-search").addEventListener("input", renderScenarioList);
byId("load-scenario").addEventListener("click", () => {
  const id = byId("scenario-list").value;
  if (id) loadExample({id});
});
byId("scenario-list").addEventListener("dblclick", () => byId("load-scenario").click());

byId("knowledge-domain").add(new Option("Все разделы", ""));
for (const [id, label] of Object.entries(domains)) byId("knowledge-domain").add(new Option(label, id));
byId("knowledge-domain").addEventListener("change", renderKnowledgeList);
byId("knowledge-search").addEventListener("input", renderKnowledgeList);
byId("browse-knowledge").addEventListener("click", () => moveTo(byId("knowledge-browser")));
byId("open-card").addEventListener("click", () => openKnowledge("knowledge", byId("knowledge-list").value));
byId("knowledge-list").addEventListener("dblclick", () => byId("open-card").click());
byId("open-rule").addEventListener("click", () => openKnowledge("knowledge-rules", byId("knowledge-rule").value));
byId("open-demo").addEventListener("click", () => openKnowledge("knowledge-demos", byId("knowledge-demo").value));
loadKnowledge();

request("/api/catalog").then((data) => {
  catalog = data;
  byId("scenario-title").textContent = `Все сценарии (${data.examples.length})`;
  byId("scenario-group").add(new Option("Все группы", ""));
  for (const [id, label] of Object.entries(groups)) byId("scenario-group").add(new Option(label, id));
  renderScenarioList();
  for (const id of data.quick_examples) {
    const example = data.examples.find((entry) => entry.id === id);
    if (!example) continue;
    const button = node("button", example.title);
    button.type = "button";
    button.addEventListener("click", () => loadExample(example));
    byId("examples").append(button);
  }
  for (const item of data.diseases) byId("diseases").add(new Option(item.title, item.id));
  for (const item of data.medications) byId("medications").add(new Option(item.title, item.id));
  byId("stats").textContent = `${data.counts.cards} карточка · ${data.counts.rules} правил`;
  syncForm();
}).catch((error) => showError("app-error", error.message));
