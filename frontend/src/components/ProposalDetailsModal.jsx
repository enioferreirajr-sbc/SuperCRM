import { Alert, Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';
import { NumericFormat } from 'react-number-format';
import useSWR from 'swr';
import { API_BASE_URL } from '../config/api';

const fetcher = async (url) => {
    const res = await fetch(url);
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const message = err?.message || err?.detail || 'Erro ao carregar dados.';
        throw new Error(message);
    }
    return res.json();
};

const formatDate = (value) => {
    if (!value) return '-';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '-';
    return date.toLocaleDateString('pt-BR');
};

export default function ProposalDetailsModal({ open, proposalId, onClose }) {
    const shouldFetch = open && proposalId !== null && proposalId !== undefined;
    const { data, error } = useSWR(
        shouldFetch ? `${API_BASE_URL}/proposals/${proposalId}/details` : null,
        fetcher
    );

    const proposal = data?.proposal;
    const items = data?.items || [];
    const isLoading = shouldFetch && !data && !error;

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>Detalhes da Proposta #{proposalId}</DialogTitle>
            <DialogContent dividers>
                {error ? (
                    <Alert severity="error" sx={{ width: '100%' }}>
                        Erro ao carregar detalhes: {error?.message || 'Falha na conexão com o servidor'}
                    </Alert>
                ) : (
                    <>
                        {isLoading && (
                            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                                Carregando detalhes...
                            </Typography>
                        )}

                        <Grid container spacing={2} sx={{ mb: 2 }}>
                            <Grid item xs={12} sm={6}>
                                <Typography variant="subtitle2" color="textSecondary">Nome da Proposta</Typography>
                                <Typography variant="body1">{proposal?.proposal_name || '-'}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography variant="subtitle2" color="textSecondary">Cliente</Typography>
                                <Typography variant="body1">{proposal?.customer_reference || '-'}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography variant="subtitle2" color="textSecondary">Contato</Typography>
                                <Typography variant="body1">{proposal?.recipient_name || '-'}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography variant="subtitle2" color="textSecondary">E-mail</Typography>
                                <Typography variant="body1">{proposal?.recipient_email || '-'}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography variant="subtitle2" color="textSecondary">Etapa do Funil</Typography>
                                <Typography variant="body1">{proposal?.funnel_percentage || '-'}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography variant="subtitle2" color="textSecondary">Status</Typography>
                                <Typography variant="body1">{proposal?.proposal_status || '-'}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography variant="subtitle2" color="textSecondary">Data da Proposta</Typography>
                                <Typography variant="body1">{formatDate(proposal?.business_proposal_date)}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography variant="subtitle2" color="textSecondary">Data do Status</Typography>
                                <Typography variant="body1">{formatDate(proposal?.last_status_date)}</Typography>
                            </Grid>
                            <Grid item xs={12}>
                                <Typography variant="subtitle2" color="textSecondary">Último Comentário</Typography>
                                <Typography variant="body1">{proposal?.last_note || '-'}</Typography>
                            </Grid>
                        </Grid>

                        <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Itens da Proposta</Typography>
                        <TableContainer component={Paper} variant="outlined">
                            <Table size="small">
                                <TableHead sx={{ bgcolor: 'grey.100' }}>
                                    <TableRow>
                                        <TableCell>Produto</TableCell>
                                        <TableCell>Tipo</TableCell>
                                        <TableCell>Time</TableCell>
                                        <TableCell>Responsável</TableCell>
                                        <TableCell align="right">Total</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {isLoading ? (
                                        <TableRow><TableCell colSpan={5} align="center">Carregando itens...</TableCell></TableRow>
                                    ) : items.length > 0 ? (
                                        items.map((item, index) => (
                                            <TableRow key={index}>
                                                <TableCell>{item.product_name}</TableCell>
                                                <TableCell>{item.proposal_type_name}</TableCell>
                                                <TableCell>{item.team_name}</TableCell>
                                                <TableCell>{item.owner}</TableCell>
                                                <TableCell align="right">
                                                    <NumericFormat value={item.total_sales || 0} displayType="text" thousandSeparator="." decimalSeparator="," prefix="R$ " />
                                                </TableCell>
                                            </TableRow>
                                        ))
                                    ) : (
                                        <TableRow><TableCell colSpan={5} align="center">Nenhum item encontrado.</TableCell></TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">Fechar</Button>
            </DialogActions>
        </Dialog>
    );
}
