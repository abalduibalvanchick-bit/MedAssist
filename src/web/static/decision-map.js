"use strict";

function showDecisionMap(result, role) {
  const dialog = byId("decision-map");
  const tree = byId("decision-map-tree");
  const panel = byId("decision-map-panel");
  const tabs = [];
  const hypotheses = result.hypotheses || [];
  const routeName = (role === "patient" && patientRoutes[result.routing?.route]) || result.routing?.label;

  function button(label, className) {
    const control = node("button", label, className);
    control.type = "button";
    return control;
  }

  function addTab(parent, title, caption, render) {
    const control = button(null, "map-node");
    control.setAttribute("aria-controls", panel.id);
    control.append(node("strong", title), node("span", caption));
    tabs.push(control);
    control.addEventListener("click", () => {
      for (const tab of tabs) tab.setAttribute("aria-pressed", String(tab === control));
      panel.replaceChildren();
      render(panel);
    });
    parent.append(control);
    return control;
  }

  function showStep(container, step) {
    const record = node("section", null, "map-evidence");
    record.append(node("h5", step.title), node("small", step.source));
    addList(record, "На каких данных", step.because);
    addList(record, "Что получилось", step.effects);
    container.append(record);
  }

  function traceFor(container, sources) {
    for (const step of result.trace || []) {
      if (sources.has(step.source)) showStep(container, step);
    }
  }

  function showInputs(container) {
    container.append(node("h4", "Данные случая"));
    const labels = {
      symptom: "Симптомы", feature: "Признаки симптомов", param: "Измерения и параметры",
      fact: "Сведения о пациенте", exam_result: "Результаты обследований",
    };
    for (const [kind, title] of Object.entries(labels)) {
      const values = catalog.fields[kind].flatMap((field) => {
        const value = fieldValue(field) ?? (kind === "symptom" && symptomOn(field) ? true : null);
        return value == null ? [] : [`${fieldName(field)} — ${formatValue(field, value)}`];
      });
      addList(container, title, values);
    }
    for (const [key, title] of [["diseases", "Ранее установленные диагнозы"], ["medications", "Принимаемые препараты"]]) {
      addList(container, title, asList(patient[key]).map((id) => catalog[key].find((item) => item.id === id)?.title || id));
    }
    if (container.children.length === 1) container.append(node("p", "Данные ещё не введены."));
  }

  function showHypotheses(container) {
    container.append(node("h4", "Сравнение гипотез"));
    if (!hypotheses.length) {
      container.append(node("p", "Решатель пока не выдвинул гипотезу по этим данным."));
      return;
    }
    const scores = hypotheses.map((item) => item.rank_score ?? item.score);
    const extent = Math.max(1, ...scores.map(Math.abs));
    const hasNegative = scores.some((score) => score < 0);
    const format = new Intl.NumberFormat("ru-RU", {maximumFractionDigits: 4});
    container.append(node("p", hypotheses.length === 1
      ? "В этом разборе одна гипотеза. На полосе показана её оценка в баллах."
      : "Все полосы используют общую шкалу. Порядок гипотез задан решателем с учётом приоритета опасных состояний."));
    const list = node("ul", null, "map-scores");
    const details = node("div", null, "map-selection");
    details.setAttribute("aria-live", "polite");
    details.id = "decision-map-hypothesis";
    const controls = hypotheses.map((item, index) => {
      const score = scores[index];
      const row = node("li");
      const control = button(null, "map-score");
      control.setAttribute("aria-controls", details.id);
      const label = node("span", null, "map-score-label");
      label.append(node("strong", item.title), node("span", format.format(score) + " балл."));
      if (index === 0) label.append(node("small", "Первая в списке"));
      if (item.time_critical_priority) label.append(node("small", "Приоритет по срочности", "map-priority"));
      const bar = node("span", null, `map-score-track${hasNegative ? " signed" : ""}`);
      bar.setAttribute("aria-hidden", "true");
      const fill = node("span", null, score < 0 ? "negative" : index === 0 ? "leading" : "");
      fill.style.inlineSize = (Math.abs(score) / extent * (hasNegative ? 50 : 100)) + "%";
      bar.append(fill);
      control.append(label, bar);
      control.addEventListener("click", () => {
        for (const candidate of controls) candidate.setAttribute("aria-pressed", String(candidate === control));
        details.replaceChildren(node("h5", item.title));
        textLine(details, "Вес сработавших правил", format.format(item.score));
        addList(details, "Вклад признаков", item.arguments.map((entry) =>
          `${entry.title} · ${entry.contribution > 0 ? "+" : ""}${format.format(entry.contribution)}`));
        traceFor(details, new Set(item.sources));
      });
      row.append(control);
      list.append(row);
      return control;
    });
    const axis = node("div", null, "map-axis");
    axis.setAttribute("aria-hidden", "true");
    if (hasNegative) axis.append(node("span", "−" + format.format(extent)));
    axis.append(node("span", "0"), node("span", format.format(extent)));
    container.append(list, axis, node("p", "Баллы показывают оценку по правилам базы. Вероятность заболевания по ним не вычисляется.", "map-note"), details);
    controls[0].click();
  }

  function showUrgency(container) {
    container.append(node("h4", "Срочность"),
      node("p", result.outcome.urgency || "Срочность пока не определена.",
        result.outcome.kind === "emergency" ? "map-urgent" : ""));
    const reasons = result.urgency?.reasons || [];
    if (role !== "patient") {
      addList(container, "Правила и признаки", reasons.map((item) => item.reason));
      traceFor(container, new Set(reasons.map((item) => item.source)));
    } else {
      addList(container, "Выявленные тревожные признаки", (result.red_flags || []).map((item) => item.title));
      if (result.outcome.next_step) container.append(node("p", result.outcome.next_step));
    }
  }

  function showRoute(container) {
    const routing = result.routing || {};
    container.append(node("h4", "Маршруты по текущим данным"));
    const band = node("ul", null, "map-routes");
    const details = node("div", null, "map-selection");
    details.id = "decision-map-route";
    details.setAttribute("aria-live", "polite");
    const controls = [];
    const questions = (result.questions || []).filter((item) => ["routing", "safety_check"].includes(item.kind));
    const questionFields = (items) => [...new Set(items.flatMap((item) => item.inputs.map(fieldName)))];

    function addRoute(tone, status, title, note, render) {
      const row = node("li");
      const control = button(null, `map-route ${tone}`);
      control.setAttribute("aria-controls", details.id);
      control.append(node("small", status), node("strong", title));
      if (note) control.append(node("span", note));
      controls.push(control);
      control.addEventListener("click", () => {
        for (const item of controls) item.setAttribute("aria-pressed", String(item === control));
        details.replaceChildren();
        render(details);
      });
      row.append(control);
      band.append(row);
    }

    const decisions = routing.decisions || [];
    const origins = new Set(routing.sources || []);
    const selected = decisions.filter((item) => origins.has(item.id) && item.route === routing.route);
    addRoute(result.outcome.kind === "emergency" ? "critical" : routeName ? "chosen" : "neutral",
      result.outcome.provisional && routeName ? "Предварительно выбран" : routeName ? "Выбран" : "Текущий результат",
      routeName || "Маршрут пока не определён", routing.timeframe, (body) => {
        if (selected.length) {
          for (const item of selected) {
            textLine(body, "Таблица решения", item.title);
            addList(body, "Основание выбранной строки", item.because);
          }
        } else if (origins.size) {
          traceFor(body, origins);
        }
        if (result.outcome.provisional) {
          addList(body, "Что можно уточнить для маршрута и срочности", questionFields(questions));
        }
        if (result.outcome.summary) body.append(node("p", result.outcome.summary));
        if (role === "patient" && result.outcome.next_step) body.append(node("p", result.outcome.next_step));
      });
    const alternatives = new Map();
    for (const decision of decisions) {
      for (const item of decision.unresolved || []) {
        if (item.route === routing.route) continue;
        if (!alternatives.has(item.label)) alternatives.set(item.label, []);
        alternatives.get(item.label).push({id: decision.id, title: decision.title, row: item.row});
      }
    }
    for (const [label, entries] of alternatives) {
      addRoute("possible", "Не хватает данных", label, "", (body) => {
        addList(body, "Таблицы, для которых нужны данные", entries.map((item) => `${item.title} · строка ${item.row + 1}`));
        const ids = new Set(entries.map((item) => item.id));
        addList(body, "Уточнения для этих таблиц", questionFields(questions.filter((item) => ids.has(item.source))));
      });
    }
    container.append(band);
    if (alternatives.size) container.append(node("p", "Выбери вариант, чтобы увидеть его основание или уточнения к таблице.", "map-note"));
    container.append(details);
    controls[0].click();
  }

  function showTrace(container) {
    container.append(node("h4", "Порядок выполнения шагов"));
    const path = node("ol", null, "map-steps");
    const details = node("div", null, "map-selection");
    details.id = "decision-map-step";
    details.setAttribute("aria-live", "polite");
    const controls = result.trace.map((step) => {
      const item = node("li");
      const control = button(null, "map-node");
      control.setAttribute("aria-controls", details.id);
      control.append(node("small", `Шаг ${step.step} · ${traceKinds[step.kind] || step.kind}`), node("strong", step.title));
      control.addEventListener("click", () => {
        for (const stepButton of controls) stepButton.setAttribute("aria-pressed", String(stepButton === control));
        details.replaceChildren();
        showStep(details, step);
      });
      item.append(control);
      path.append(item);
      return control;
    });
    container.append(path, details);
    controls[0].click();
  }

  tree.replaceChildren();
  addTab(tree, "Введённые данные", "Жалобы, параметры и результаты", showInputs).classList.add("map-root");
  const branches = node("div", null, "map-branches");
  tree.append(branches);
  const hypothesis = role === "patient" ? null : addTab(branches, "Гипотезы", hypotheses[0]?.title || "Пока нет гипотез", showHypotheses);
  const urgency = addTab(branches, "Срочность", result.outcome.urgency || "Уточняется", showUrgency);
  const route = addTab(branches, "Маршрут", routeName || "Уточняется", showRoute);
  if (result.trace?.length) addTab(tree, "Весь ход вывода", `${result.trace.length} шагов`, showTrace).classList.add("map-trace-tab");
  byId("decision-map-context").textContent = result.outcome.title;
  const initial = result.outcome.kind === "emergency" ? urgency : hypotheses.length && ["professional", "student"].includes(role) ? hypothesis : route;
  initial.click();
  dialog.showModal();
}

byId("decision-map").addEventListener("close", (event) => {
  if (event.currentTarget.open) return;
  byId("decision-map-tree").replaceChildren();
  byId("decision-map-panel").replaceChildren();
  byId("decision-map-context").textContent = "";
});
