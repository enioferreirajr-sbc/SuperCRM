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
            const response = await fetch(`${API_BASE_URL}/imports/proposals`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json().catch(() => ({}));

            if (response.ok) {
                if (data?.ok) {
                    setSuccess('Importação concluída com sucesso.');
                    return data;
                }
                const msg = data?.errors?.[0]?.message || 'A importação falhou.';
                setError(msg);
                return data;
            }
            const msg = data?.message || data?.detail || data?.errors?.[0]?.message || 'Erro desconhecido na importação.';
            setError(msg);
            return { ok: false, errors: msg ? [{ message: msg }] : [] };
        } catch (err) {
            console.error(err);
            const msg = err.message || 'Erro ao conectar com o servidor.';
            setError(msg);
            return { ok: false, errors: msg ? [{ message: msg }] : [] };
        } finally {
            setIsLoading(false);
        }
    };

    return { importProposals, isLoading, error, success };
};
