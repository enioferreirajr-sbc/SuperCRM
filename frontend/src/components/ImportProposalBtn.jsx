import { useRef, useState } from 'react';
import { Button, CircularProgress, Alert, Snackbar } from '@mui/material';
import { UploadOutlined } from '@ant-design/icons';
import { useImportProposals } from 'hooks/useImportProposals';
import { useSWRConfig } from 'swr';
import { API_BASE_URL } from '../config/api';

export default function ImportProposalBtn() {
    const fileInputRef = useRef(null);
    const { importProposals, isLoading } = useImportProposals();
    const { mutate } = useSWRConfig();
    const [feedbackOpen, setFeedbackOpen] = useState(false);
    const [feedbackMessage, setFeedbackMessage] = useState('');
    const [feedbackSeverity, setFeedbackSeverity] = useState('info');

    const handleButtonClick = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        // Validation
        const validTypes = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ];
        const hasValidExt = file.name.toLowerCase().endsWith('.xlsx');
        const hasValidMime = !file.type || validTypes.includes(file.type);
        const isValidParams = hasValidExt && hasValidMime; // Relaxed mime check when browser omits file.type

        if (!isValidParams) {
            showFeedback('Apenas arquivos .xlsx são permitidos.', 'error');
            event.target.value = ''; // Reset
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB
            showFeedback('O arquivo excede o limite de 10MB.', 'error');
            event.target.value = '';
            return;
        }

        // Process
        const result = await importProposals(file);

        if (result && typeof result.ok === 'boolean') {
            const stats = result.stats || {};
            const message = result.ok
                ? `Importação concluída. Linhas: ${stats.total_rows ?? 0}, Propostas: ${stats.proposals_found ?? 0}, Itens: ${stats.details_found ?? 0}.`
                : (result?.errors?.[0]?.message || 'Erro na importação.');
            const severity = result.ok && result.warnings?.length ? 'warning' : (result.ok ? 'success' : 'error');
            showFeedback(message, severity);
            if (result.ok) {
                mutate((key) => typeof key === 'string' && key.startsWith(`${API_BASE_URL}/proposals`));
            }
        } else {
            showFeedback(result?.message || 'Erro na importação.', 'error');
        }

        event.target.value = ''; // Reset input
    };

    const showFeedback = (msg, severity) => {
        setFeedbackMessage(msg);
        setFeedbackSeverity(severity);
        setFeedbackOpen(true);
    };

    const handleCloseFeedback = () => {
        setFeedbackOpen(false);
    };

    return (
        <>
            <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept=".xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                onChange={handleFileChange}
            />
            <Button
                variant="contained"
                startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <UploadOutlined />}
                onClick={handleButtonClick}
                disabled={isLoading}
            >
                {isLoading ? 'Importando...' : 'Importar Propostas'}
            </Button>

            <Snackbar open={feedbackOpen} autoHideDuration={6000} onClose={handleCloseFeedback} anchorOrigin={{ vertical: 'top', horizontal: 'center' }}>
                <Alert onClose={handleCloseFeedback} severity={feedbackSeverity} sx={{ width: '100%' }}>
                    {feedbackMessage}
                </Alert>
            </Snackbar>

        </>
    );
}
