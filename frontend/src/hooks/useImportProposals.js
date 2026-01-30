import { useState } from 'react';
import { API_BASE_URL } from '../config/api';

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
            const response = await fetch(`${API_BASE_URL}/proposals/import`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                // Determine success based on API status AND summary
                // If we have errors but no rows upserted, it's a critical failure even if API returned 200
                const { summary } = data;

                if (summary && summary.errors_count > 0 && summary.proposals_upserted === 0) {
                    const msg = 'A importação falhou. Verifique o registro de erros.';
                    setError(msg);
                    // We still return data so the modal can show the error table
                    return data;
                }

                if (data.status === 'success' || data.status === 'completed_with_warnings') {
                    setSuccess(`Importação finalizada. Verifique os resultados.`);
                    return data;
                } else {
                    return data;
                }
            } else {
                const msg = data.message || data.detail || 'Erro desconhecido na importação.';
                setError(msg);
                return { status: 'error', message: msg, errors: [] };
            }
        } catch (err) {
            console.error(err);
            const msg = err.message || 'Erro ao conectar com o servidor.';
            setError(msg);
            return { status: 'error', message: msg, errors: [] };
        } finally {
            setIsLoading(false);
        }
    };

    return { importProposals, isLoading, error, success };
};
