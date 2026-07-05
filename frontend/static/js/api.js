const BASE_URL = "http://localhost:8000/api";

const API = {
    // Shared headers helper
    getHeaders(multipart = false) {
        const token = Auth.getToken();
        const headers = {};
        
        if (!multipart) {
            headers["Content-Type"] = "application/json";
        }
        
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
        
        return headers;
    },

    // Standard Response Handler
    async handleResponse(response) {
        if (!response.ok) {
            if (response.status === 401) {
                // If token is invalid or expired, clear session and force login
                Auth.logout();
                throw new Error("Session expired. Please login again.");
            }
            let errorMessage = "An error occurred with the request.";
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                // Fallback for non-JSON or missing details
            }
            throw new Error(errorMessage);
        }
        
        // For standard 204 or empty responses, return success flag
        if (response.status === 204) return { success: true };
        
        return await response.json();
    },

    // HTTP GET
    async get(endpoint) {
        try {
            const response = await fetch(`${BASE_URL}${endpoint}`, {
                method: "GET",
                headers: this.getHeaders()
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`API GET ${endpoint} failed:`, error);
            throw error;
        }
    },

    // HTTP POST
    async post(endpoint, data) {
        try {
            const response = await fetch(`${BASE_URL}${endpoint}`, {
                method: "POST",
                headers: this.getHeaders(),
                body: JSON.stringify(data)
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`API POST ${endpoint} failed:`, error);
            throw error;
        }
    },

    // HTTP PUT
    async put(endpoint, data) {
        try {
            const response = await fetch(`${BASE_URL}${endpoint}`, {
                method: "PUT",
                headers: this.getHeaders(),
                body: JSON.stringify(data)
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`API PUT ${endpoint} failed:`, error);
            throw error;
        }
    },

    // HTTP DELETE
    async delete(endpoint) {
        try {
            const response = await fetch(`${BASE_URL}${endpoint}`, {
                method: "DELETE",
                headers: this.getHeaders()
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`API DELETE ${endpoint} failed:`, error);
            throw error;
        }
    },

    // HTTP POST Multipart (Form Data upload)
    async postMultipart(endpoint, formData) {
        try {
            const response = await fetch(`${BASE_URL}${endpoint}`, {
                method: "POST",
                headers: this.getHeaders(true), // Skip content-type header for fetch boundary injection
                body: formData
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`API POST Multipart ${endpoint} failed:`, error);
            throw error;
        }
    }
};
