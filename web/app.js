/* Власний файл користувача читається локально; бекенд не потрібен. */
(() => {
  "use strict";
  const status = document.querySelector("#status");
  const file = document.querySelector("#file");
  const reset = document.querySelector("#reset");
  if (!window.d3) {
    status.textContent = "Не вдалося завантажити d3.js. Перевірте інтернет і перезавантажте сторінку.";
    file.disabled = true;
    return;
  }
  const svg = d3.select("#tree");
  const scene = svg.append("g");
  const zoom = d3.zoom().scaleExtent([0.04, 4]).on("zoom", event => scene.attr("transform", event.transform));
  svg.call(zoom);
  let root = null;
  let total = 0;

  function color(type) {
    if (["If", "While", "Return", "Print"].includes(type)) return "#ae6cdb";
    if (["Declaration", "Assignment", "Variable"].includes(type)) return "#d78b37";
    if (["BinaryOp", "UnaryOp", "IntegerLiteral"].includes(type)) return "#319e85";
    return "#5689ce";
  }

  function validate(document) {
    const pending = [{node: document, depth: 0}];
    const ids = new Set();
    while (pending.length) {
      const {node, depth} = pending.pop();
      if (!node || typeof node.id !== "string" || ids.has(node.id) ||
          typeof node.type !== "string" || typeof node.label !== "string" ||
          !Array.isArray(node.children) || depth > 200 || ids.size >= 10000) {
        throw new Error("Очікується AST Mini C з унікальними id, type, label, children (до 10000 вузлів, глибина до 200).");
      }
      ids.add(node.id);
      for (const child of node.children) pending.push({node: child, depth: depth + 1});
    }
    return ids.size;
  }

  function fit() {
    if (!root) return;
    const bounds = scene.node().getBBox();
    const width = svg.node().clientWidth;
    const height = svg.node().clientHeight;
    const scale = Math.max(0.04, Math.min(1.4, (width - 60) / Math.max(1, bounds.width), (height - 60) / Math.max(1, bounds.height)));
    const x = width / 2 - scale * (bounds.x + bounds.width / 2);
    const y = height / 2 - scale * (bounds.y + bounds.height / 2);
    svg.call(zoom.transform, d3.zoomIdentity.translate(x, y).scale(scale));
  }

  function toggle(event, node) {
    if (node.children) { node.hidden = node.children; node.children = null; }
    else if (node.hidden) { node.children = node.hidden; node.hidden = null; }
    render();
  }

  function render() {
    d3.tree().nodeSize([42, 275])(root);
    scene.selectAll("path.link").data(root.links(), d => d.target.data.id).join("path")
      .attr("class", "link").attr("d", d3.linkHorizontal().x(d => d.y).y(d => d.x));
    const nodes = scene.selectAll("g.node").data(root.descendants(), d => d.data.id)
      .join(enter => {
        const group = enter.append("g").attr("class", "node").attr("tabindex", 0).attr("role", "button");
        group.append("circle").attr("r", 7);
        group.append("text").attr("x", 13).attr("dy", "0.35em");
        group.append("title");
        return group;
      })
      .attr("transform", d => `translate(${d.y},${d.x})`)
      .attr("aria-label", d => d.data.label)
      .attr("aria-expanded", d => d.children ? "true" : "false")
      .on("click", toggle)
      .on("keydown", (event, node) => {
        if (event.key === "Enter" || event.key === " ") { event.preventDefault(); toggle(event, node); }
      });
    nodes.select("circle").attr("fill", d => d.hidden ? color(d.data.type) : "white")
      .attr("stroke", d => color(d.data.type)).attr("stroke-width", 2.5);
    nodes.select("text").text(d => d.data.label.length > 34 ? d.data.label.slice(0, 31) + "…" : d.data.label);
    nodes.select("title").text(d => `${d.data.label}\nРоль: ${d.data.role}\nРядок ${d.data.line}, стовпець ${d.data.column}\nID: ${d.data.id}`);
    status.textContent = `Вузлів: ${total}. Видимих: ${root.descendants().length}.`;
  }

  file.addEventListener("change", async () => {
    const selected = file.files[0];
    if (!selected) return;
    try {
      if (selected.size > 10 * 1024 * 1024) throw new Error("Файл перевищує 10 МБ.");
      const document = JSON.parse(await selected.text());
      const count = validate(document);
      root = d3.hierarchy(document);
      total = count;
      render();
      reset.disabled = false;
      fit();
    } catch (error) {
      status.textContent = "Помилка: " + error.message;
    }
  });
  reset.addEventListener("click", fit);
  window.addEventListener("resize", fit);
})();