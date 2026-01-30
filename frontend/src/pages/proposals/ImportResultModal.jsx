import { Dialog, DialogTitle, DialogContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, DialogActions, Typography, Grid, Box, Card, CardContent } from '@mui/material';
import { CheckCircle, Warning, Error as ErrorIcon, CloudUpload } from '@mui/icons-material';

// --- KPI Card Component ---
function KpiCard({ title, value, color, icon: Icon }) {
    return (
        <Card sx={{ bgcolor: color + '.light', minWidth: 100 }}>
            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Box display="flex" alignItems="center" gap={1}>
                    {Icon && <Icon color={color} />}
                    <Typography variant="h5" color={color + '.main'} fontWeight="bold">
                        {value}
                    </Typography>
                </Box>
                <Typography variant="caption" color="textSecondary">
                    {title}
                </Typography>
            </CardContent>
        </Card>
    );
}

export default function ImportResultModal({ open, onClose, result }) {
    if (!result) return null;

    const { summary, errors, status } = result;
    const isSuccess = status === 'success';
    const hasWarnings = status === 'completed_with_warnings';
    const hasErrors = errors && errors.length > 0;

    // Header Color based on Status
    const headerColor = isSuccess ? 'success.main' : hasWarnings ? 'warning.main' : 'error.main';
    const headerText = isSuccess ? 'Importação Concluída' : hasWarnings ? 'Concluído com Alertas' : 'Falha na Importação';

    // Export CSV Logic
    const handleExportLog = () => {
        if (!errors || errors.length === 0) return;

        const csvContent = [
            'Line,Proposal ID,Column,Error Message,Value Provided',
            ...errors.map(e => `${e.line_number},"${e.proposal_id || ''}","${e.column || ''}","${e.message.replace(/"/g, '""')}","${e.value_provided || ''}"`)
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'import_errors_log.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle sx={{ bgcolor: headerColor, color: 'white' }}>
                <Box display="flex" alignItems="center" gap={1}>
                    {isSuccess ? <CheckCircle /> : hasWarnings ? <Warning /> : <ErrorIcon />}
                    {headerText}
                </Box>
            </DialogTitle>

            <DialogContent dividers>
                {/* Summary KPIs */}
                <Grid container spacing={2} sx={{ mb: 3, mt: 0 }}>
                    <Grid item xs={6} sm={2.4}>
                        <KpiCard title="Linhas Lidas" value={summary.total_lines_processed} color="info" icon={CloudUpload} />
                    </Grid>
                    <Grid item xs={6} sm={2.4}>
                        <KpiCard title="Propostas (Cabeçalho)" value={summary.proposals_upserted} color="primary" />
                    </Grid>
                    <Grid item xs={6} sm={2.4}>
                        <KpiCard title="Itens (Detalhes)" value={summary.details_inserted} color="success" />
                    </Grid>
                    <Grid item xs={6} sm={2.4}>
                        <KpiCard title="Clientes" value={summary.customers_updated} color="secondary" />
                    </Grid>
                    <Grid item xs={6} sm={2.4}>
                        <KpiCard title="Erros/Ignorados" value={summary.errors_count} color="error" icon={ErrorIcon} />
                    </Grid>
                </Grid>

                {/* Error Table */}
                {hasErrors && (
                    <>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                            <Typography variant="h6" color="error">
                                Detalhes dos Erros ({errors.length})
                            </Typography>
                            <Button variant="outlined" color="error" size="small" onClick={handleExportLog}>
                                Exportar Log (.csv)
                            </Button>
                        </Box>

                        <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 300 }}>
                            <Table size="small" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Linha</TableCell>
                                        <TableCell>ID Proposta</TableCell>
                                        <TableCell>Coluna</TableCell>
                                        <TableCell>Mensagem de Erro</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {errors.map((err, idx) => (
                                        <TableRow key={idx} hover>
                                            <TableCell>{err.line_number > 0 ? err.line_number : '-'}</TableCell>
                                            <TableCell>{err.proposal_id || '-'}</TableCell>
                                            <TableCell>{err.column || '-'}</TableCell>
                                            <TableCell sx={{ color: 'error.main' }}>
                                                {err.message.includes('Inexact')
                                                    ? 'Valor numérico com precisão inválida (muitas casas decimais)'
                                                    : err.message}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </>
                )}

                {!hasErrors && (
                    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={4}>
                        <CheckCircle color="success" sx={{ fontSize: 60, mb: 2 }} />
                        <Typography variant="h6" color="success.main">
                            Todos os registros foram processados com sucesso!
                        </Typography>
                    </Box>
                )}

            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} variant="contained" color="primary">
                    Concluir
                </Button>
            </DialogActions>
        </Dialog>
    );
}
