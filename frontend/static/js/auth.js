const TOKEN_KEY = "onboardgenius_token";

const Auth = {
    // Save JWT token
    saveToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
    },

    // Retrieve JWT token
    getToken() {
        return localStorage.getItem(TOKEN_KEY);
    },

    // Check if token exists
    isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;
        
        // Simple expiry check
        try {
            const payload = this.getUserPayload();
            if (!payload || !payload.exp) return false;
            const expiryTime = payload.exp * 1000;
            return Date.now() < expiryTime;
        } catch (e) {
            return false;
        }
    },

    // Parse user payload from JWT token
    getUserPayload() {
        const token = this.getToken();
        if (!token) return null;
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch (e) {
            console.error("Failed to parse JWT payload", e);
            return null;
        }
    },

    // Retrieve user email
    getUserEmail() {
        const payload = this.getUserPayload();
        return payload ? payload.sub : null;
    },

    // Retrieve user role
    getUserRole() {
        const payload = this.getUserPayload();
        return payload ? payload.role : null;
    },

    // Delete token and exit session
    logout() {
        localStorage.removeItem(TOKEN_KEY);
        window.location.href = "login.html";
    },

    // Protect administrative views (e.g. users or console dashboards)
    protectPage() {
        const currentPath = window.location.pathname;
        const publicPages = ["index.html", "login.html", "register.html", "/"];
        
        const isPublic = publicPages.some(page => currentPath.endsWith(page) || currentPath === "/");

        if (!this.isAuthenticated()) {
            if (!isPublic) {
                // Not authenticated, accessing protected page -> login
                window.location.href = "login.html";
            }
        } else {
            if (currentPath.endsWith("login.html") || currentPath.endsWith("register.html")) {
                // Authenticated, accessing login/register -> redirect to dashboard
                window.location.href = "dashboard.html";
            }
        }
    }
};

// Auto run page protection checks
document.addEventListener("DOMContentLoaded", () => {
    Auth.protectPage();
});
