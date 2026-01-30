// Generic Form Interceptor for SPA-like feel
document.addEventListener("submit", async function (e) {
    if (e.target.tagName !== "FORM") return;

    // Skip if explicitly opted out (e.g. login form or external action)
    if (e.target.getAttribute("data-no-ajax")) return;

    e.preventDefault();
    const form = e.target;
    const action = form.action;
    const method = form.method.toUpperCase();
    const formData = new FormData(form);

    // Show loading state on button
    const submitBtn = form.querySelector("button[type='submit']");
    const originalBtnText = submitBtn ? submitBtn.innerText : "";
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = "Processing...";
    }

    try {
        const response = await fetch(action, {
            method: method,
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest" // Mark as AJAX
            }
        });

        if (response.type === "opaqueredirect" || response.redirected) {
            // Handle redirects (fetch follows them automatically usually, but we want the final URL content)
            // Fetch the **final** destination content
            const finalUrl = response.url;

            // Check success/error in params
            const urlObj = new URL(finalUrl);
            const successMsg = urlObj.searchParams.get("success");
            const errorMsg = urlObj.searchParams.get("error");

            if (successMsg) showToast(successMsg, 'success');
            if (errorMsg) showToast(errorMsg, 'error');

            // Replace content
            const html = await response.text();

            // Dom Parser
            const doc = new DOMParser().parseFromString(html, "text/html");

            // Swap Main Content
            const newContent = doc.querySelector(".container");
            const oldContent = document.querySelector(".container");

            // Also need to update the calendar if it exists on page
            // Or just swap the whole body content excluding scripts that might re-run?
            // Safest for this simple app: Swap .container

            if (newContent && oldContent) {
                oldContent.innerHTML = newContent.innerHTML;

                // Re-initialize active tab
                const activeTabId = document.querySelector(".tab-content.active")?.id || "dashboard";
                // Re-apply active class if lost (though innerHTML swap might preserve if container wraps content)
                // Actually, if we swap innerHTML of container, we might lose event listeners attached to elements inside.
                // But we are using delegated events or global functions mostly.

                // Re-run window.onload logic if any needed? 
                // Specifically: checkUrlToasts() is already handled manually above.

                // Restore active tab
                openTab(activeTabId);

            } else {
                // Fallback: Full reload if structure mismatch
                window.location.reload();
            }

        } else if (!response.ok) {
            showToast("Server Error: " + response.statusText, 'error');
        } else {
            // Just a regular 200 without redirect?
            // Maybe we just reload content too.
            const html = await response.text();
            // Same swap logic...
            const doc = new DOMParser().parseFromString(html, "text/html");
            const newContent = doc.querySelector(".container");
            const oldContent = document.querySelector(".container");
            if (newContent && oldContent) oldContent.innerHTML = newContent.innerHTML;
        }

    } catch (err) {
        showToast("Network Request Failed: " + err, 'error');
        console.error(err);
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerText = originalBtnText;
        }

        // Close any open modals
        document.querySelectorAll(".modal-overlay").forEach(m => m.style.display = "none");
    }
});
