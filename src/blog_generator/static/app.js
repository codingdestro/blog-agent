function fakeApiCall(delay = 2000) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ message: "Data fetched successfully!" });
    }, delay);
  });
}

const form = document.querySelector("#blog-form");
const output = document.querySelector("#output");
const statusLabel = document.querySelector("#status");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form);

  const btn = document.getElementById("gen-btn");
  const spinner = document.getElementById("spinner");
  const icon = btn.querySelector(".btn-gen-icon");
  const lbl = document.getElementById("gen-label");

  btn.disabled = true;
  spinner.style.display = "block";
  icon.style.display = "none";
  lbl.textContent = "Generating…";
  setStatus("Generating…", true);

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      body: data,
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "Generation failed");
    }
    // await fakeApiCall(3000);
    renderBlog(payload);
    statusLabel.textContent = "Done";
  } catch (error) {
    output.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
    console.log(error);
    statusLabel.textContent = "Error";
  } finally {
    btn.disabled = false;
    spinner.style.display = "none";
    icon.style.display = "block";
    lbl.textContent = "Generate blog";
  }
});

function renderLoading() {
  output.innerHTML =
    '<div class="empty-state">Researching and drafting...</div>';
}

function renderBlog(blog) {
  const outline = (blog.outline || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  const sections = (blog.sections || [])
    .map(
      (section) => `
        <section class="blog-section">
          <h3>${escapeHtml(section.heading || "Section")}</h3>
          <p>${escapeHtml(section.body || "")}</p>
        </section>
      `,
    )
    .join("");
  const sources = (blog.search_results || [])
    .filter((item) => item.url)
    .map(
      (item) =>
        `<li><a href="${escapeAttribute(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(
          item.title || item.url,
        )}</a></li>`,
    )
    .join("");

  output.innerHTML = `
    <article class="article">
      <h2>${escapeHtml(blog.title || "Generated blog")}</h2>
      ${
        blog.id
          ? `<p><a class="btn-view" href="/blog.html?id=${escapeAttribute(blog.id)}">View saved blog</a></p>`
          : ""
      }
      ${blog.summary ? `<p class="summary">${escapeHtml(blog.summary)}</p>` : ""}
      ${outline ? `<h3>Outline</h3><ol>${outline}</ol>` : ""}
      <h3>Draft</h3>
      ${sections || `<pre>${escapeHtml(blog.article || "")}</pre>`}
      ${blog.conclusion ? `<h3>Conclusion</h3><p>${escapeHtml(blog.conclusion)}</p>` : ""}
      ${sources ? `<h3>Search sources</h3><ul class="sources">${sources}</ul>` : ""}
    </article>
  `;
  document.getElementById("empty-state").style.display = "none";
  output.style.display = "block";

  document.getElementById("empty-state").style.display = "none";
  document.getElementById("copy-btn").style.display = "inline-flex";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}
