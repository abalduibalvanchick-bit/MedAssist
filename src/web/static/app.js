"use strict";

const byId = (id) => document.getElementById(id);
const node = (tag, text, className) => {
  const item = document.createElement(tag);
  if (text != null) item.textContent = text;
  if (className) item.className = className;
  return item;
};

const primaryCodes = ["age", "temperature", "spo2", "sbp", "dbp", "hr"];
const extraKinds = ["param", "fact", "exam_result", "feature"];
let catalog;
let patient = {};
let extraCodes = [];
let revision = 0;
let referenceRevision = 0;
let selectedExample = "";
let knowledgeRevision = 0;
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
  input.setAttribute("aria-label", field.label);
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

function edit() {
  revision += 1;
  selectedExample = "";
  byId("scenario-info").hidden = true;
  syncRawCase();
  showError("case-error");
  emptyResult("result-content", caseEmpty);
}

function fieldLabel(field, callback, initial) {
  const label = node("label", field.label);
  const input = control(field, initial);
  if (callback) input.addEventListener("change", () => callback(readControl(input, field)));
  label.append(input);
  return [label, input];
}

function renderPrimary() {
  const controls = primaryCodes.map((code) => {
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
  for (const field of catalog.fields.symptom) {
    const button = node("button", field.label, "chip");
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
    const label = node("label", catalog.fields.symptom.find((field) => field.code === code).label);
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
    row.append(node("span", field.label), input, remove);
    root.append(row);
  }
  const select = node("select");
  select.setAttribute("aria-label", "Добавить параметр, факт или обследование");
  select.add(new Option("Добавить параметр, факт или обследование", ""));
  for (const field of fieldChoices.filter((item) => !codes.has(item.code))) {
    select.add(new Option(field.label, field.code));
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

function renderQuestions(root, questions) {
  if (!questions?.length) return;
  const section = node("section");
  section.append(node("h3", "Что можно уточнить"));
  const fields = new Map();
  for (const question of questions) {
    for (const field of question.inputs || []) {
      if (!fields.has(field.code)) fields.set(field.code, field);
    }
  }
  const shown = questions.slice(0, 4);
  const notes = node("ul");
  for (const question of shown) notes.append(node("li", question.text));
  section.append(notes);
  if (fields.size) {
    const form = node("form");
    const grid = node("div", null, "question-grid");
    const more = node("details");
    const rest = node("div", null, "question-grid");
    more.append(node("summary", "Другие уточнения"), rest);
    const controls = [];
    for (const field of fields.values()) {
      if (field.type === "choice" && !field.options?.length) continue;
      const [label, input] = fieldLabel(field);
      (controls.length < 6 ? grid : rest).append(label);
      controls.push([field, input]);
    }
    form.append(grid);
    if (rest.children.length) form.append(more);
    const apply = node("button", "Пересчитать с ответами", "primary");
    apply.type = "submit";
    form.append(apply);
    const message = node("div", null, "message error");
    message.hidden = true;
    message.setAttribute("role", "alert");
    form.append(message);
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const answers = Object.fromEntries(controls
        .map(([field, input]) => [field.code, readControl(input, field)]).filter(([, value]) => value != null));
      message.hidden = Boolean(Object.keys(answers).length);
      if (!message.hidden) {
        message.textContent = "Заполните хотя бы одно уточнение.";
        return;
      }
      await solveCase(answers, apply, message);
    });
    section.append(form);
  }
  root.append(section);
}

function renderSolution(data) {
  const result = data.solution;
  const root = byId("result-content");
  root.className = "output";
  root.replaceChildren();
  const labels = {ok: "Случай разобран", need_more_data: "Нужны уточнения", invalid: "Проверьте данные",
    refused: "Вне области применимости"};
  const level = result.urgency?.level;
  const routing = result.routing;
  const caption = result.status === "ok" && result.urgency?.reasons?.length
    ? labels[result.status] + " · срочность: " + result.urgency.label : labels[result.status];
  root.append(node("div", caption, "message " + (result.status === "invalid" ? "error" : (level || ""))));
  if (selectedExample) root.append(node("p", "Учебный пример · " + selectedExample));
  if (result.refusal?.text) root.append(node("p", result.refusal.text));
  addList(root, "Замечания к данным", (result.input_issues || []).concat(data.answer_issues || []).map((item) => item.message));
  if (routing?.label) addList(root, "Маршрут", [[routing.label, routing.timeframe,
    routing.provisional ? "предварительно" : ""].filter(Boolean).join(" · ")]);
  addList(root, "Основания оценки", result.urgency?.reasons?.map((item) => item.reason));
  addList(root, "Красные флаги", result.red_flags?.map((item) => item.title));
  addList(root, "Неотложные состояния", result.emergencies?.map((item) => item.title));
  addList(root, "Профили", result.profiles?.map((item) => item.title), true);
  renderQuestions(root, result.questions);
  addList(root, "Гипотезы", result.hypotheses?.map((item) => {
    const argumentsText = item.arguments.map((argument) =>
      (argument.contribution > 0 ? "+" : "−") + " " + argument.title).join(", ");
    return item.title + (argumentsText ? " · " + argumentsText : "");
  }), true);
  for (const table of result.differential || []) {
    addList(root, table.title, table.branches.map((branch) => {
      const exam = branch.key_exam;
      return [branch.title + " — " + branch.label,
        branch.for.length ? "за: " + branch.for.join(", ") : "",
        branch.against.length ? "против: " + branch.against.join(", ") : "",
        exam?.recommended ? (exam.completed ? "уже выполнено: " : "ключевое обследование: ") + exam.title : "",
      ].filter(Boolean).join(" · ");
    }), true);
  }
  addList(root, "Шкалы", result.scales?.map((item) => `${item.title} · ${item.value ?? item.range.join("–")} · ${item.category_label}`), true);
  addList(root, "Обследования", result.exams?.map((item) => item.title), true);
  addList(root, "Выполненные обследования", result.completed_exams?.map((item) => item.title), true);
  addList(root, "Обследования после стабилизации", result.deferred_exams?.map((item) => item.title), true);
  addList(root, "Протоколы", result.protocols?.flatMap((item) => [item.title, ...(item.steps || []).map((step) => step.action), ...(item.phases || []).flatMap((phase) => phase.steps)]), true);
  addList(root, "Наблюдение", result.follow_up?.flatMap((item) => [item.title, ...(item.schedule || []).map((row) => [row.after, row.interval, row.purpose].filter(Boolean).join(" · "))]), true);
  for (const regimen of result.therapy?.regimens || []) {
    addList(root, regimen.title, regimen.lines.flatMap((line) => line.options.map((option) =>
      [`Линия ${line.line} · ${option.title} — ${option.label}`, option.note,
        ...option.reasons.map((reason) => reason.text + " [" + reason.source + "]"), ...option.dose_notes.map((reason) => reason.text + " [" + reason.source + "]")]
        .filter(Boolean).join(" · "))), true);
  }
  addList(root, "Взаимодействия", result.therapy?.interactions?.map((item) => item.title + " · " + item.text), true);
  addList(root, "Предупреждения", result.warnings?.map((item) => item.text), true);
  addList(root, "Памятки", result.advice?.flatMap((item) => item.seek_help_when), true);
  if (result.explanation) {
    const details = node("details");
    details.append(node("summary", "Ход вывода"), node("pre", result.explanation));
    root.append(details);
  }
  addList(root, "Справочная информация", result.disclaimer, true);
}

async function solveCase(answers, button, inlineError) {
  const stamp = ++revision;
  showError("case-error");
  button.disabled = true;
  try {
    const data = await request("/api/solve", {patient, answers, role: byId("role").value});
    if (stamp !== revision) return;
    if (inlineError && data.solution.status === "invalid") {
      inlineError.textContent = data.solution.input_issues.map((item) => item.message).join(" ");
      inlineError.hidden = false;
      return;
    }
    if (data.solution.status !== "invalid") {
      patient = data.patient;
      syncForm();
    }
    renderSolution(data);
    if (matchMedia("(max-width: 760px)").matches && !inlineError) byId("case-results").focus();
  } catch (error) {
    if (stamp === revision) showError("case-error", error.message);
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
    if (data.role && data.role !== byId("role").value) {
      byId("role").value = data.role;
      updateRoleViews();
    }
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
    return;
  }
  root.append(node("div", result.mode === "generated" ? "Ответ по источникам" : "Фрагменты из базы знаний", "message"));
  for (const claim of result.answer) {
    const paragraph = node("p", claim.text + " ");
    const link = node("a", "[" + claim.source + "]");
    link.href = "#source-" + claim.source;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      byId("source-" + claim.source)?.focus();
    });
    paragraph.append(link);
    root.append(paragraph);
    if (claim.evidence) {
      const citation = node("details");
      citation.append(node("summary", "Цитата из источника"), node("p", claim.evidence));
      root.append(citation);
    }
  }
  const section = node("section");
  section.append(node("h3", "Источники"));
  const list = node("ul", null, "sources");
  for (const source of result.sources) {
    const item = node("li", null, "source");
    item.id = "source-" + source.n;
    item.tabIndex = -1;
    item.append(node("strong", `[${source.n}] ${source.title}`),
      node("small", source.id + " · " + source.section), node("p", source.excerpt));
    const fullCard = node("button", "Открыть карточку", "text-btn");
    fullCard.type = "button";
    fullCard.addEventListener("click", () => openKnowledge("knowledge", source.id));
    item.append(fullCard);
    list.append(item);
  }
  section.append(list);
  root.append(section);
}

byId("reference-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  showError("reference-error");
  const stamp = ++referenceRevision;
  const button = byId("search-button");
  button.disabled = true;
  button.setAttribute("aria-busy", "true");
  try {
    const result = await request("/api/reference", {question: byId("question").value, role: byId("role").value});
    if (stamp === referenceRevision) renderReference(result);
  } catch (error) {
    if (stamp === referenceRevision) showError("reference-error", error.message);
  } finally {
    button.disabled = false;
    button.removeAttribute("aria-busy");
  }
});

function updateRoleViews() {
  revision += 1;
  referenceRevision += 1;
  emptyResult("result-content", caseEmpty);
  emptyResult("answer", referenceEmpty);
  showError("case-error");
  showError("reference-error");
  loadKnowledge();
}

byId("role").addEventListener("change", updateRoleViews);

byId("case-form").addEventListener("submit", (event) => {
  event.preventDefault();
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

for (const text of ["Из чего состоит шкала CURB-65?", "Что такое бронхиальная астма?", "Что означает пульсоксиметрия?"]) {
  const button = node("button", text);
  button.type = "button";
  button.addEventListener("click", () => {
    byId("question").value = text;
    byId("question").focus();
  });
  byId("suggestions").append(button);
}

window.addEventListener("hashchange", showView);
showView();

function knowledgePath(collection, id = "") {
  return "/api/" + collection + (id ? "/" + encodeURIComponent(id) : "") +
    "?role=" + encodeURIComponent(byId("role").value);
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
  const stamp = ++knowledgeRevision;
  const root = byId("knowledge-content");
  root.replaceChildren(node("p", "Загрузка…"));
  try {
    const card = await request(knowledgePath(collection, id));
    if (stamp !== knowledgeRevision) return;
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
    if (stamp === knowledgeRevision) root.textContent = error.message;
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
