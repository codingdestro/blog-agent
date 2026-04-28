const blogView = document.querySelector("#blog-view");

loadBlog();

async function loadBlog() {
  const blogId = new URLSearchParams(window.location.search).get("id");
  if (!blogId) {
    renderError("Missing blog id.");
    return;
  }

  try {
    const response = await fetch(`/api/blogs/${encodeURIComponent(blogId)}`);
    const blog = await response.json();
    if (!response.ok) {
      throw new Error(blog.detail || "Unable to load blog.");
    }
    renderBlog(blog);
  } catch (error) {
    renderError(error.message);
  }
}

function renderBlog(blog) {
  const outline = (blog.outline || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  const sections = (blog.sections || [])
    .map(
      (section) => `
        <section class="blog-section">
          <h2>${escapeHtml(section.heading || "Section")}</h2>
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

  blogView.innerHTML = `
    <article class="article blog-view-article">
      <div class="blog-view-meta">
        <span>${escapeHtml(blog.topic || "Saved blog")}</span>
        ${blog.created_at ? `<span>${escapeHtml(blog.created_at)}</span>` : ""}
      </div>
      <h1>${escapeHtml(blog.title || "Generated blog")}</h1>
      ${blog.summary ? `<p class="summary">${escapeHtml(blog.summary)}</p>` : ""}
      ${outline ? `<h2>Outline</h2><ol>${outline}</ol>` : ""}
      ${sections || `<pre>${escapeHtml(blog.article || "")}</pre>`}
      ${blog.conclusion ? `<h2>Conclusion</h2><p>${escapeHtml(blog.conclusion)}</p>` : ""}
      ${sources ? `<h2>Search sources</h2><ul class="sources">${sources}</ul>` : ""}
    </article>
  `;
}

function renderError(message) {
  blogView.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">!</div>
      <p class="error">${escapeHtml(message)}</p>
    </div>
  `;
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


function publishBlog() {

  console.log("Publish blog button clicked");
}