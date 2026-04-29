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

  const keywords = (blog.keywords || [])
    .map((k) => `<span class="badge">${escapeHtml(k)}</span>`)
    .join(" ");

  const suggestions = (blog.seo_suggestions || [])
    .map((s) => `<li>${escapeHtml(s)}</li>`)
    .join("");

  const container = document.getElementById("blog-view");
  container.innerHTML = `
    <article class="article">
      <div class="blog-view-meta">
        <span>${escapeHtml(blog.topic || "Saved blog")}</span>
        ${blog.created_at ? `<span>${escapeHtml(blog.created_at)}</span>` : ""}
        <button id='btn-publish' class="btn-generate" style="margin-bottom: 1rem;" onclick="publishBlog(${blog.id})">Publish Blog to Dev.to</button>
      </div>
      <h1>${escapeHtml(blog.title || "Generated blog")}</h1>

      ${blog.summary ? `<p class="summary">${escapeHtml(blog.summary)}</p>` : ""}

      <div class="seo-card">
        <h3>SEO Analysis</h3>
        <p><strong>Meta Description:</strong> ${escapeHtml(blog.meta_description || "N/A")}</p>
        <p><strong>Keywords:</strong> ${keywords || "None"}</p>
        ${suggestions ? `<strong>Suggestions:</strong><ul>${suggestions}</ul>` : ""}
      </div>

      ${outline ? `<h3>Outline</h3><ol>${outline}</ol>` : ""}
      ${sections || `<pre>${escapeHtml(blog.article || "")}</pre>`}
      ${blog.conclusion ? `<h3>Conclusion</h3><p>${escapeHtml(blog.conclusion)}</p>` : ""}
      ${sources ? `<h3>Search sources</h3><ul class="sources">${sources}</ul>` : ""}
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

async function publishApi(id) {
  try {
    const res = await fetch(`/api/publish/${id}`, {
      method: "POST",
    });
    const data = await res.json();
    console.log(data);
  } catch {
    console.log("Got an error on publishing the blog to Dev.to");
  }
}

async function publishBlog(id) {
  console.log("Publish blog button clicked with id ", id);
  const btn = document.querySelector("#btn-publish");
  btn.innerHTML = "Publishing...";
  await publishApi(id);
  btn.innerHTML = "Published";
  setInterval(() => {
    btn.innerHTML = "Publish Blog to Dev.to";
  }, 2000);
}
