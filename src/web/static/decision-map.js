"use strict";

const graphKinds = {
  param: "Параметр", fact: "Факт", feature: "Признак", symptom: "Симптом", disease: "Диагноз",
  medication: "Препарат", profile: "Профиль", redflag: "Красный флаг", emergency: "Неотложное состояние",
  scale: "Шкала", scale_category: "Категория шкалы", exam_result: "Результат обследования",
  hypothesis: "Гипотеза · вес правил", exam: "Рекомендованное обследование", urgency: "Срочность", protocol: "Протокол",
  route: "Маршрут из правила", routing_ref: "Таблица маршрутизации", warning: "Предупреждение",
  clarification: "Уточнение", refusal: "Граница применимости",
};

function showDecisionMap({nodes, steps, stop}) {
  const dialog = byId("decision-map");
  const controls = byId("decision-map-controls");
  const panel = byId("decision-map-panel");
  const factPanel = byId("decision-map-fact");
  const consumers = new Map();
  for (const step of steps) {
    for (const id of step.inputs) {
      if (!consumers.has(id)) consumers.set(id, []);
      consumers.get(id).push(step);
    }
  }

  function action(text, className, fn) {
    const button = node("button", text, className);
    button.type = "button";
    button.addEventListener("click", fn);
    return button;
  }

  let current = 0;
  let mode = "step";
  let redraw;
  let narrowRedraw;
  const picker = node("select");
  picker.id = "inference-step";
  picker.setAttribute("aria-label", "Шаг вывода");
  picker.add(new Option("0 · Исходные данные", "0"));
  for (const step of steps) picker.add(new Option(`${step.step} · ${step.title}`, step.step));
  picker.addEventListener("change", () => selectStep(Number(picker.value)));
  const prev = action("← Назад", "secondary", () => selectStep(current - 1));
  const next = action("Вперёд →", "secondary", () => selectStep(current + 1));
  const modeButton = action("Весь граф", "secondary", () => {
    mode = mode === "step" ? "full" : "step";
    render();
  });
  const live = node("p", null, "map-step-status");
  live.setAttribute("role", "status");
  controls.replaceChildren(prev, picker, next, modeButton, live);

  function selectStep(number) {
    current = number;
    render();
  }

  function kindLabel(fact) {
    if (fact.kind !== "disease") return graphKinds[fact.kind] || fact.kind;
    return fact.step && steps[fact.step - 1].iteration ? "Рабочий диагноз" : "Сообщённый диагноз";
  }

  function showFact(fact) {
    factPanel.hidden = false;
    factPanel.replaceChildren(node("h3", fact.label),
      node("p", `${kindLabel(fact)} · ${fact.value}`));
    if (fact.step) {
      const producer = steps[fact.step - 1];
      factPanel.append(action(`Получен на шаге ${fact.step} · ${producer.title}`, "text-btn", () => {
        mode = "step";
        selectStep(fact.step);
        picker.focus();
      }));
    } else {
      factPanel.append(node("p", fact.absent ? "На этом шаге решатель проверил отсутствие значения." : "Значение поступило на вход решателя."));
    }
    const uses = consumers.get(fact.id) || [];
    if (uses.length) {
      const list = node("ul");
      for (const step of uses) {
        const item = node("li");
        item.append(action(`Шаг ${step.step} · ${step.title}`, "text-btn", () => {
          mode = "step";
          selectStep(step.step);
          picker.focus();
        }));
        list.append(item);
      }
      factPanel.append(node("h4", "Где использован"), list);
    }
    factPanel.tabIndex = -1;
    factPanel.focus({preventScroll: true});
    factPanel.scrollIntoView({block: "nearest"});
  }

  function factNode(id, highlight) {
    const fact = nodes[id];
    const tone = highlight || (fact.absent ? "missing" : "input");
    const button = action(null, `graph-fact graph-${tone}`, () => showFact(fact));
    button.append(node("small", kindLabel(fact)), node("strong", fact.label), node("span", String(fact.value)));
    return button;
  }

  function transition(step, upcoming = false) {
    const row = node("div", null, `graph-transition${upcoming ? " upcoming" : ""}`);
    const input = node("div", null, "graph-stack inputs");
    const output = node("div", null, "graph-stack outputs");
    for (const id of step.inputs) input.append(factNode(id));
    for (const id of step.outputs) output.append(factNode(id, upcoming ? "next" : "new"));
    if (!step.inputs.length) input.append(node("p", "Без входного факта", "graph-empty"));
    if (!step.outputs.length) output.append(node("p", "Значения фактов не изменились", "graph-empty"));
    for (const stack of [input, output]) {
      if (!stack.querySelector(".graph-fact")) continue;
      stack.classList.add("linked");
    }
    const edge = node("div", null, "graph-edge");
    edge.append(node("small", `Шаг ${step.step} · ${step.source}`), node("strong", step.title));
    row.append(input, edge, output);
    return row;
  }

  function showStep() {
    const step = steps[current - 1];
    const upcoming = steps[current];
    if (step) {
      panel.append(node("h3", "Текущий переход"), transition(step));
      if (step.evidence.length || step.effects.length) {
        const evidence = node("details", null, "graph-evidence");
        evidence.append(node("summary", "Условия и действия решателя"));
        addList(evidence, "Проверенные условия", step.evidence);
        addList(evidence, "Что сделал решатель", step.effects);
        panel.append(evidence);
      }
    } else {
      panel.append(node("h3", "Исходные факты"));
      const initial = node("div", null, "graph-initial");
      for (const fact of nodes) if (fact.step === 0 && !fact.absent) initial.append(factNode(fact.id));
      if (initial.children.length) panel.append(initial);
      else panel.append(node("p", "Исходные факты не заданы."));
    }
    if (upcoming) {
      panel.append(node("h3", "Следующий переход", "graph-next-title"), transition(upcoming, true));
    } else {
      panel.append(node("p", stop, "graph-end"));
    }
  }

  function showFullGraph() {
    panel.append(node("h3", "Все связи между фактами"),
      node("p", "Выберите факт, чтобы перейти к шагу, на котором он получен или использован."));
    const layer = new Map(nodes.map((fact) => [fact.id, 0]));
    const depth = new Map();
    for (const step of steps) {
      const column = 1 + Math.max(0, ...step.inputs.map((id) => layer.get(id)));
      depth.set(step.step, column);
      for (const id of step.outputs) layer.set(id, column + 1);
    }
    const viewport = node("div", null, "graph-viewport");
    const board = node("div", null, "graph-board");
    const canvas = node("canvas", null, "graph-lines");
    canvas.setAttribute("aria-hidden", "true");
    const columns = Array.from({length: 1 + Math.max(0, ...layer.values(), ...depth.values())},
      () => node("div", null, "graph-column"));
    const positions = new Map();
    const junctions = new Map();
    for (const fact of nodes) {
      let tone;
      if (fact.step > current + 1) tone = "future";
      else if (fact.step === current + 1) tone = "next";
      else if (fact.step && fact.step === current) tone = "new";
      const button = factNode(fact.id, tone);
      positions.set(fact.id, button);
      columns[layer.get(fact.id)].append(button);
    }
    for (const step of steps) {
      const label = action(`${step.step} · ${step.source}`, "graph-junction", () => {
        mode = "step";
        selectStep(step.step);
        picker.focus();
      });
      label.title = step.title;
      label.setAttribute("aria-label", `Шаг ${step.step} · ${step.title}`);
      if (step.step === current + 1) label.classList.add("upcoming");
      if (step.step > current + 1) label.classList.add("future");
      junctions.set(step.step, label);
      columns[depth.get(step.step)].append(label);
    }
    board.append(canvas, ...columns);
    viewport.append(board);
    panel.append(viewport);

    function draw() {
      const bounds = board.getBoundingClientRect();
      canvas.width = Math.ceil(bounds.width);
      canvas.height = Math.ceil(bounds.height);
      const ctx = canvas.getContext("2d");
      const point = (el, side) => {
        const rect = el.getBoundingClientRect();
        return [rect[side] - bounds.left, rect.top + rect.height / 2 - bounds.top];
      };
      function line(from, to, stepNumber) {
        const isNext = stepNumber === current + 1;
        const [x1, y1] = point(from, "right");
        const [x2, y2] = point(to, "left");
        const middle = (x1 + x2) / 2;
        ctx.strokeStyle = isNext ? "#7036a1" : stepNumber > current + 1 ? "#afbdb8" : "#68857b";
        ctx.lineWidth = isNext ? 2.5 : 1;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.bezierCurveTo(middle, y1, middle, y2, x2 - 1, y2);
        ctx.moveTo(x2 - 6, y2 - 4);
        ctx.lineTo(x2 - 1, y2);
        ctx.lineTo(x2 - 6, y2 + 4);
        ctx.stroke();
      }
      for (const step of steps) {
        const junction = junctions.get(step.step);
        for (const id of step.inputs) line(positions.get(id), junction, step.step);
        for (const id of step.outputs) line(junction, positions.get(id), step.step);
      }
    }
    redraw = new ResizeObserver(draw);
    redraw.observe(board);
    const upcoming = junctions.get(current + 1) || junctions.get(current);
    if (upcoming && current && dialog.open) {
      const rect = upcoming.getBoundingClientRect();
      const frame = viewport.getBoundingClientRect();
      viewport.scrollTo(rect.left - frame.left - frame.width / 2 + rect.width / 2,
        rect.top - frame.top - frame.height / 2 + rect.height / 2);
    }
  }

  function render() {
    redraw?.disconnect();
    narrowRedraw?.disconnect();
    redraw = undefined;
    picker.value = String(current);
    prev.disabled = current === 0;
    next.disabled = current === steps.length;
    modeButton.textContent = mode === "step" ? "Весь граф" : "Пошаговый вид";
    byId("graph-future-key").hidden = mode !== "full";
    const step = steps[current - 1];
    live.textContent = step
      ? `Шаг ${current} из ${steps.length} · ${step.iteration ? "Итерация " + step.iteration : "Подготовка данных"}`
      : `Исходные данные · ${steps.length} переходов`;
    panel.replaceChildren();
    factPanel.hidden = true;
    factPanel.replaceChildren();
    if (mode === "full") {
      showFullGraph();
      return;
    }
    showStep();
    narrowRedraw = new ResizeObserver((entries) => {
      for (const {target} of entries) {
        const first = target.firstElementChild.getBoundingClientRect();
        const last = target.lastElementChild.getBoundingClientRect();
        target.style.setProperty("--join-top", first.height / 2 + "px");
        target.style.setProperty("--join-bottom", last.height / 2 + "px");
      }
    });
    for (const stack of panel.querySelectorAll(".graph-stack.linked")) narrowRedraw.observe(stack);
  }

  dialog.addEventListener("close", () => {
    redraw?.disconnect();
    narrowRedraw?.disconnect();
    controls.replaceChildren();
    panel.replaceChildren();
    factPanel.replaceChildren();
    factPanel.hidden = true;
  }, {once: true});
  render();
  dialog.showModal();
}
