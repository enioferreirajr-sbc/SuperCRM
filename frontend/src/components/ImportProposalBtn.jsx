import { useRef, useState } from 'react';
import { Button, Typography, Box, CircularProgress, Alert, Snackbar } from '@mui/material';
import { UploadOutlined } from '@ant-design/icons';
import { useImportProposals } from 'hooks/useImportProposals';
import ImportResultModal from 'pages/proposals/ImportResultModal';

export default function ImportProposalBtn() {
    const fileInputRef = useRef(null);
    const { importProposals, isLoading, error, success } = useImportProposals();
    const [feedbackOpen, setFeedbackOpen] = useState(false);
    const [feedbackMessage, setFeedbackMessage] = useState('');
    const [feedbackSeverity, setFeedbackSeverity] = useState('info');

    // Modal State
    const [importResult, setImportResult] = useState(null);
    const [modalOpen, setModalOpen] = useState(false);

    const handleButtonClick = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        // Validation
        const validTypes = [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ];
        const isValidParams = file.name.endsWith('.xlsx'); // Relaxed mime check as browser might vary, relying on extension + backend strictness

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

        if (result && (result.status === 'success' || result.status === 'completed_with_warnings' || result.status === 'failed')) {
            setImportResult(result);
            setModalOpen(true);
        } else {
            // Fallback for network errors or unexpected format
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

            <ImportResultModal
                open={modalOpen}
                onClose={() => setModalOpen(false)}
                result={importResult}
            />
        </>
    );
}
