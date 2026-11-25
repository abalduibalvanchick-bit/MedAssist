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

function boolValue(yes, no, code) {
  if ((yes || []).includes(code)) return true;
  if ((no || []).includes(code)) return false;
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
    patient[yes] = (patient[yes] || []).filter((item) => item !== code);
    patient[no] = (patient[no] || []).filter((item) => item !== code);
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
      (field.kind === "symptom" ? fieldValue(field) === false : field.kind !== "feature" && fieldValue(field) != null))
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
  byId("diseases").value = patient.diseases?.[0] || "";
  for (const option of byId("medications").options) option.selected = (patient.medications || []).includes(option.value);
  if (openDetails) document.querySelector(".extra").open = true;
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
    extraCodes = [];
    emptyResult("result-content", caseEmpty);
    syncForm(false);
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

byId("role").addEventListener("change", () => {
  revision += 1;
  referenceRevision += 1;
  emptyResult("result-content", caseEmpty);
  emptyResult("answer", referenceEmpty);
  showError("case-error");
  showError("reference-error");
});

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
  patient.diseases = event.target.value ? [event.target.value, ...(patient.diseases || []).slice(1)
    .filter((code) => code !== event.target.value)] : [];
  edit();
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

request("/api/catalog").then((data) => {
  catalog = data;
  for (const example of data.examples) {
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
