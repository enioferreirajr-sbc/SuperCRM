import { useState } from 'react';

// Set base URL for API (assuming standard Vite proxy or specific URL)
// If you have a global axios instance, use that. For now using default.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useImportProposals = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const importProposals = async (file) => {
        setIsLoading(true);
        setError(null);
        setSuccess(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/proposals/import`, {
                method: 'POST',
                body: formData,
                // Do NOT set Content-Type header for FormData, browser sets it with boundary
            });

            const data = await response.json();

            if (response.ok) {
                // Determine success based on API status
                if (data.status === 'success' || data.status === 'completed_with_warnings') {
                    setSuccess(`Importação finalizada. Verifique os resultados.`);
                    return data;
                } else {
                    // Logic for explicit "failed" status inside 200 OK (if design permits, but usually failed is 400)
                    // Our API returns 'failed' with 200 if parsed but rejected? No, we likely want to just pass it through.
                    // Let's just pass data if response is OK, letting UI decide.
                    return data;
                }
            } else {
                const msg = data.message || data.detail || 'Erro desconhecido na importação.';
                setError(msg);
                return { status: 'error', message: msg };
            }
        } catch (err) {
            console.error(err);
            const msg = err.message || 'Erro ao conectar com o servidor.';
            setError(msg);
            return { status: 'error', message: msg };
        } finally {
            setIsLoading(false);
        }
    };

    return { importProposals, isLoading, error, success };
};
