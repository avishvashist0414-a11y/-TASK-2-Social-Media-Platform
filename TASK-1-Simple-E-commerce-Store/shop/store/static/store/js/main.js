// Add-to-cart without page reload (progressive enhancement: forms still work without JS)
(function () {
  const toast = document.getElementById("toast");
  const badge = document.getElementById("cart-count");
  let timer;

  function showToast(msg, isError) {
    toast.textContent = msg;
    toast.style.background = isError ? "#b42318" : "#1c2430";
    toast.classList.add("show");
    clearTimeout(timer);
    timer = setTimeout(() => toast.classList.remove("show"), 2200);
  }

  document.querySelectorAll(".add-form").forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = form.querySelector("button");
      btn.disabled = true;
      try {
        const res = await fetch(form.action, {
          method: "POST",
          body: new FormData(form),
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const data = await res.json();
        if (data.count !== undefined) badge.textContent = data.count;
        showToast(data.message, !data.ok);
      } catch (err) {
        form.submit(); // fall back to normal submit
      } finally {
        btn.disabled = false;
      }
    });
  });
})();
