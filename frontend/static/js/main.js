const UI = {
    // Show alert notification
    showAlert(message, type = "success") {
        const container = document.getElementById("alert-container");
        if (!container) {
            const div = document.createElement("div");
            div.id = "alert-container";
            document.body.appendChild(div);
        }
        
        const alertDiv = document.createElement("div");
        alertDiv.className = `alert alert-${type === "success" ? "success" : "danger"} alert-dismissible fade show shadow-sm border-0 mb-2 fade-in`;
        alertDiv.role = "alert";
        alertDiv.innerHTML = `
            <div>${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.getElementById("alert-container").appendChild(alertDiv);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            alertDiv.classList.remove("show");
            setTimeout(() => alertDiv.remove(), 150);
        }, 4000);
    },

    // Show processing overlay spinner
    showLoader() {
        if (document.getElementById("loading-overlay")) return;
        
        const overlay = document.createElement("div");
        overlay.id = "loading-overlay";
        overlay.className = "loader-overlay";
        overlay.innerHTML = `<div class="loader-spinner"></div>`;
        document.body.appendChild(overlay);
    },

    // Hide processing overlay spinner
    hideLoader() {
        const overlay = document.getElementById("loading-overlay");
        if (overlay) {
            overlay.remove();
        }
    },

    // Dynamically insert sidebar navigation to protected screens
    renderSidebar() {
        const sidebarContainer = document.getElementById("sidebar-root");
        if (!sidebarContainer) return;

        const role = Auth.getUserRole() || "employee";
        const email = Auth.getUserEmail() || "user@onboardgenius.com";
        const currentPath = window.location.pathname;

        const isHr = (role === "admin" || role === "hr");

        let sidebarHTML = `
            <div class="sidebar">
                <div class="brand">
                    <i class="bi bi-rocket-takeoff-fill"></i>
                    <span>OnboardGenius</span>
                </div>
                <ul class="nav-menu">
                    <li>
                        <a href="dashboard.html" class="nav-link-item ${currentPath.endsWith('dashboard.html') ? 'active' : ''}">
                            <i class="bi bi-grid-1x2-fill"></i> Dashboard
                        </a>
                    </li>
        `;

        if (isHr) {
            sidebarHTML += `
                <li>
                    <a href="employees.html" class="nav-link-item ${currentPath.endsWith('employees.html') ? 'active' : ''}">
                        <i class="bi bi-people-fill"></i> Employees
                    </a>
                </li>
            `;
        }

        sidebarHTML += `
                    <li>
                        <a href="tasks.html" class="nav-link-item ${currentPath.endsWith('tasks.html') ? 'active' : ''}">
                            <i class="bi bi-check2-square"></i> Tasks
                        </a>
                    </li>
                    <li>
                        <a href="documents.html" class="nav-link-item ${currentPath.endsWith('documents.html') ? 'active' : ''}">
                            <i class="bi bi-file-earmark-arrow-up-fill"></i> Documents
                        </a>
                    </li>
                    <li>
                        <a href="chatbot.html" class="nav-link-item ${currentPath.endsWith('chatbot.html') ? 'active' : ''}">
                            <i class="bi bi-chat-left-dots-fill"></i> AI Chat
                        </a>
                    </li>
                    <li>
                        <a href="profile.html" class="nav-link-item ${currentPath.endsWith('profile.html') ? 'active' : ''}">
                            <i class="bi bi-person-bounding-box"></i> Profile
                        </a>
                    </li>
                </ul>
                <div class="sidebar-footer">
                    <div class="d-flex align-items-center mb-3">
                        <div class="bg-primary text-white rounded-circle p-2 me-2 d-flex justify-content-center align-items-center" style="width: 38px; height: 38px; font-weight: bold;">
                            ${email.charAt(0).toUpperCase()}
                        </div>
                        <div class="overflow-hidden" style="flex: 1;">
                            <h6 class="text-white mb-0 text-truncate" style="font-size: 0.9rem;">${email}</h6>
                            <small class="text-muted text-uppercase" style="font-size: 0.7rem;">${role}</small>
                        </div>
                    </div>
                    <button class="btn btn-outline-danger w-100 btn-sm" onclick="Auth.logout()">
                        <i class="bi bi-box-arrow-right"></i> Logout
                    </button>
                </div>
            </div>
        `;

        sidebarContainer.innerHTML = sidebarHTML;
    },

    // Dynamically insert floating AI assistant drawer
    renderFloatingChat() {
        if (!Auth.isAuthenticated()) return;
        
        const currentPath = window.location.pathname;
        const publicPages = ["index.html", "login.html", "register.html", "/"];
        const isPublic = publicPages.some(page => currentPath.endsWith(page) || currentPath === "/");
        if (isPublic) return;

        if (document.getElementById("floating-chat-trigger")) return;

        // 1. Create Floating action button
        const trigger = document.createElement("button");
        trigger.id = "floating-chat-trigger";
        trigger.innerHTML = `<i class="bi bi-robot"></i>`;
        trigger.title = "OnboardGenius AI Assistant";
        document.body.appendChild(trigger);

        // 2. Create Floating chat drawer window
        const windowDiv = document.createElement("div");
        windowDiv.id = "floating-chat-window";
        windowDiv.innerHTML = `
            <div class="floating-chat-header">
                <div class="d-flex align-items-center text-white">
                    <i class="bi bi-robot me-2 fs-5"></i>
                    <div>
                        <h6 class="fw-bold mb-0" style="font-size: 0.9rem;">Genius AI Assistant</h6>
                        <small class="opacity-75" style="font-size: 0.7rem;">Online & ready</small>
                    </div>
                </div>
                <button type="button" class="btn-close btn-close-white btn-sm" id="floating-chat-close"></button>
            </div>
            
            <div class="floating-chat-actions">
                <div class="action-chip" onclick="floatingAI.action('tasks')">Suggest Tasks</div>
                <div class="action-chip" onclick="floatingAI.action('email')">Draft Email</div>
                <div class="action-chip" onclick="floatingAI.action('summarize')">Summarize Files</div>
            </div>

            <div class="floating-chat-body" id="floating-chat-body">
                <div class="chat-bubble bot">
                    Hi! I am OnboardGenius AI. How can I help you with your onboarding today?
                </div>
            </div>
            
            <div class="floating-chat-footer">
                <form id="floating-chat-form" class="d-flex gap-2">
                    <input type="text" id="floating-chat-input" class="form-control form-control-sm border shadow-none" required placeholder="Ask Genius AI...">
                    <button type="submit" class="btn btn-primary btn-sm px-3" style="background: var(--primary-gradient); border: none;">
                        <i class="bi bi-send-fill"></i>
                    </button>
                </form>
            </div>
        `;
        document.body.appendChild(windowDiv);

        // Event hooks
        trigger.addEventListener("click", () => {
            windowDiv.classList.toggle("show");
            if (windowDiv.classList.contains("show")) {
                document.getElementById("floating-chat-input").focus();
                const body = document.getElementById("floating-chat-body");
                body.scrollTop = body.scrollHeight;
            }
        });

        document.getElementById("floating-chat-close").addEventListener("click", () => {
            windowDiv.classList.remove("show");
        });

        document.getElementById("floating-chat-form").addEventListener("submit", async (e) => {
            e.preventDefault();
            const input = document.getElementById("floating-chat-input");
            const message = input.value.trim();
            if (!message) return;
            
            input.value = "";
            await floatingAI.sendMessage(message);
        });
    }
};

// Global Floating AI actions handlers
const floatingAI = {
    async sendMessage(message) {
        const body = document.getElementById("floating-chat-body");
        
        // Append user message
        const uMsg = document.createElement("div");
        uMsg.className = "chat-bubble user";
        uMsg.textContent = message;
        body.appendChild(uMsg);
        body.scrollTop = body.scrollHeight;

        // Show typing loader
        const loader = document.createElement("div");
        loader.id = "floating-typing";
        loader.className = "chat-bubble bot text-muted";
        loader.innerHTML = `<span class="spinner-grow spinner-grow-sm"></span> Thinking...`;
        body.appendChild(loader);
        body.scrollTop = body.scrollHeight;

        try {
            const result = await API.post("/chat/query", { message });
            loader.remove();
            
            const bMsg = document.createElement("div");
            bMsg.className = "chat-bubble bot";
            bMsg.textContent = result.response;
            body.appendChild(bMsg);
        } catch (e) {
            loader.remove();
            const bMsg = document.createElement("div");
            bMsg.className = "chat-bubble bot text-danger";
            bMsg.textContent = "Failed to fetch response.";
            body.appendChild(bMsg);
        }
        body.scrollTop = body.scrollHeight;
    },
    
    async action(type) {
        const body = document.getElementById("floating-chat-body");
        if (type === 'tasks') {
            const bMsg = document.createElement("div");
            bMsg.className = "chat-bubble bot";
            bMsg.innerHTML = `
                <strong>Recommend Onboarding Tasks</strong><br>
                Please enter the position and department in the input box below. e.g. "Recommend onboarding tasks for Software Engineer in IT"
            `;
            body.appendChild(bMsg);
        } else if (type === 'email') {
            const bMsg = document.createElement("div");
            bMsg.className = "chat-bubble bot";
            bMsg.innerHTML = `
                <strong>Generate Email Drafts</strong><br>
                Choose email type:<br>
                <button class="btn btn-xs btn-outline-primary btn-sm mt-1" onclick="floatingAI.runEmail('welcome')">Welcome Email</button>
                <button class="btn btn-xs btn-outline-primary btn-sm mt-1 ms-1" onclick="floatingAI.runEmail('equipment')">IT Equipment request</button>
            `;
            body.appendChild(bMsg);
        } else if (type === 'summarize') {
            const bMsg = document.createElement("div");
            bMsg.className = "chat-bubble bot";
            bMsg.innerHTML = `
                <strong>Summarize Uploaded Documents</strong><br>
                Loading file list...
            `;
            body.appendChild(bMsg);
            body.scrollTop = body.scrollHeight;
            
            try {
                const user = await API.get("/auth/me");
                let empId = null;
                try {
                    const emp = await API.get(`/employees/user/${user.id}`);
                    empId = emp.id;
                } catch(err){}
                
                if (!empId) {
                    bMsg.innerHTML = `<strong>Error</strong><br>Please complete your employee profile details first.`;
                    return;
                }
                
                const docs = await API.get(`/documents/employee/${empId}`);
                if (docs.length === 0) {
                    bMsg.innerHTML = `<strong>Summarize Documents</strong><br>No uploaded documents found. Go to Documents tab to upload.`;
                    return;
                }
                
                let html = `<strong>Select document to summarize:</strong><br>`;
                docs.forEach(doc => {
                    html += `<button class="btn btn-outline-primary btn-sm mt-1 w-100 text-truncate text-start" onclick="floatingAI.runSummary(${doc.id}, '${doc.title.replace(/'/g, "\\'")}')"><i class="bi bi-file-earmark-text"></i> ${doc.title}</button><br>`;
                });
                bMsg.innerHTML = html;
            } catch(e) {
                bMsg.innerHTML = `<strong>Error</strong><br>Failed to retrieve documents.`;
            }
        }
        body.scrollTop = body.scrollHeight;
    },

    async runEmail(type) {
        const body = document.getElementById("floating-chat-body");
        const loader = document.createElement("div");
        loader.className = "chat-bubble bot text-muted";
        loader.innerHTML = `<span class="spinner-grow spinner-grow-sm"></span> Drafting email...`;
        body.appendChild(loader);
        body.scrollTop = body.scrollHeight;

        try {
            const user = await API.get("/auth/me");
            let name = "New Employee";
            let dept = "Engineering";
            let pos = "Software Engineer";
            try {
                const emp = await API.get(`/employees/user/${user.id}`);
                name = `${emp.first_name} ${emp.last_name}`;
                dept = emp.department || dept;
                pos = emp.position || pos;
            } catch(err){}

            const res = await API.post("/chat/generate-email", {
                email_type: type,
                details: { employee_name: name, department: dept, position: pos, start_date: new Date().toLocaleDateString() }
            });
            loader.remove();
            
            const bMsg = document.createElement("div");
            bMsg.className = "chat-bubble bot";
            bMsg.innerHTML = `<strong>Drafted Email:</strong><br><pre style="white-space: pre-wrap; font-size: 0.8rem; background: #fff; padding: 8px; border-radius: 4px; border: 1px solid #ddd;">${res.email}</pre>`;
            body.appendChild(bMsg);
        } catch (e) {
            loader.remove();
            const bMsg = document.createElement("div");
            bMsg.className = "chat-bubble bot text-danger";
            bMsg.textContent = "Failed to generate email draft.";
            body.appendChild(bMsg);
        }
        body.scrollTop = body.scrollHeight;
    },

    async runSummary(docId, title) {
        const body = document.getElementById("floating-chat-body");
        const loader = document.createElement("div");
        loader.className = "chat-bubble bot text-muted";
        loader.innerHTML = `<span class="spinner-grow spinner-grow-sm"></span> Summarizing ${title}...`;
        body.appendChild(loader);
        body.scrollTop = body.scrollHeight;

        try {
            const res = await API.post(`/chat/summarize/${docId}`);
            loader.remove();
            
            const bMsg = document.createElement("div");
            bMsg.className = "chat-bubble bot";
            bMsg.innerHTML = `<strong>Summary for ${title}:</strong><br><div style="font-size:0.85rem; line-height: 1.4;">${res.response.replace(/\n/g, '<br>')}</div>`;
            body.appendChild(bMsg);
        } catch (e) {
            loader.remove();
            const bMsg = document.createElement("div");
            bMsg.className = "chat-bubble bot text-danger";
            bMsg.textContent = `Failed to summarize document: ${e.message}`;
            body.appendChild(bMsg);
        }
        body.scrollTop = body.scrollHeight;
    }
};

// Hook sidebar and floating chat rendering into DOM load
document.addEventListener("DOMContentLoaded", () => {
    UI.renderSidebar();
    UI.renderFloatingChat();
});
