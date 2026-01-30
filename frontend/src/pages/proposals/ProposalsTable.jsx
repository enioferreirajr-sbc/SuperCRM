import { useState, useMemo } from 'react';
import {
    MaterialReactTable,
    useMaterialReactTable,
} from 'material-react-table';
import { MRT_Localization_PT_BR } from 'material-react-table/locales/pt-BR';
import { Box, Alert } from '@mui/material';
import useSWR from 'swr';
import { NumericFormat } from 'react-number-format';
import { API_BASE_URL } from '../../config/api';

// --- Modal Component ---
import { Dialog, DialogTitle, DialogContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, DialogActions, Typography, Grid } from '@mui/material';

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

function ProposalDetailsModal({ open, onClose, proposalId }) {
    const { data: header, error: headerError } = useSWR(
        proposalId ? `${API_BASE_URL}/proposals/${proposalId}` : null,
        fetcher
    );
    const { data: items, error: itemsError } = useSWR(
        proposalId ? `${API_BASE_URL}/proposals/${proposalId}/items` : null,
        fetcher
    );

    const isLoading = !header && !headerError;
    const isItemsLoading = !items && !itemsError;

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>Detalhes da Proposta #{proposalId}</DialogTitle>
            <DialogContent dividers>
                {/* Header Info */}
                <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Nome da Proposta</Typography>
                        <Typography variant="body1">{header?.proposal_name || '-'}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Cliente</Typography>
                        <Typography variant="body1">{header?.customer_reference || '-'}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Contato</Typography>
                        <Typography variant="body1">{header?.recipient_name || '-'}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">E-mail</Typography>
                        <Typography variant="body1">{header?.recipient_email || '-'}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography variant="subtitle2" color="textSecondary">Status</Typography>
                        <Typography variant="body1">{header?.proposal_status || '-'}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Data da Proposta</Typography>
                        <Typography variant="body1">{formatDate(header?.business_proposal_date)}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Data do Status</Typography>
                        <Typography variant="body1">{formatDate(header?.last_status_date)}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography variant="subtitle2" color="textSecondary">Último Comentário</Typography>
                        <Typography variant="body1">{header?.last_note || '-'}</Typography>
                    </Grid>
                </Grid>

                {/* Items Table */}
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Itens da Proposta</Typography>
                <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                        <TableHead sx={{ bgcolor: 'grey.100' }}>
                            <TableRow>
                                <TableCell>Produto</TableCell>
                                <TableCell>Tipo</TableCell>
                                <TableCell>Time</TableCell>
                                <TableCell>Responsável</TableCell>
                                <TableCell align="right">Licença</TableCell>
                                <TableCell align="right">Treinamento</TableCell>
                                <TableCell align="right">Mensal</TableCell>
                                <TableCell align="right">Consultoria</TableCell>
                                <TableCell align="right">Mensal Anualizado</TableCell>
                                <TableCell align="right">Total</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {(isLoading || isItemsLoading) ? (
                                <TableRow><TableCell colSpan={10} align="center">Carregando itens...</TableCell></TableRow>
                            ) : items?.length > 0 ? (
                                items.map((item, index) => (
                                    <TableRow key={index}>
                                        <TableCell>{item.product_name}</TableCell>
                                        <TableCell>{item.proposal_type_name}</TableCell>
                                        <TableCell>{item.team_name}</TableCell>
                                        <TableCell>{item.owner}</TableCell>
                                        <TableCell align="right">
                                            <NumericFormat value={item.license_of_use || 0} displayType="text" thousandSeparator="." decimalSeparator="," prefix="R$ " />
                                        </TableCell>
                                        <TableCell align="right">
                                            <NumericFormat value={item.training || 0} displayType="text" thousandSeparator="." decimalSeparator="," prefix="R$ " />
                                        </TableCell>
                                        <TableCell align="right">
                                            <NumericFormat value={item.monthly_fee || 0} displayType="text" thousandSeparator="." decimalSeparator="," prefix="R$ " />
                                        </TableCell>
                                        <TableCell align="right">
                                            <NumericFormat value={item.professional_services || 0} displayType="text" thousandSeparator="." decimalSeparator="," prefix="R$ " />
                                        </TableCell>
                                        <TableCell align="right">
                                            <NumericFormat value={item.monthly_fee_annualized || 0} displayType="text" thousandSeparator="." decimalSeparator="," prefix="R$ " />
                                        </TableCell>
                                        <TableCell align="right">
                                            <NumericFormat value={item.total_sales || 0} displayType="text" thousandSeparator="." decimalSeparator="," prefix="R$ " />
                                        </TableCell>
                                    </TableRow>
                                ))
                            ) : (
                                <TableRow><TableCell colSpan={10} align="center">Nenhum item encontrado (ou erro ao carregar).</TableCell></TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">Fechar</Button>
            </DialogActions>
        </Dialog>
    );
}

export default function ProposalsTable() {
    // MRT State
    const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });

    // Modal State
    const [selectedProposalId, setSelectedProposalId] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const handleOpenDetails = (row) => {
        setSelectedProposalId(row.original.proposal_id);
        setIsModalOpen(true);
    };

    const handleCloseDetails = () => {
        setIsModalOpen(false);
        setSelectedProposalId(null);
    };

    // Construct URL for SWR
    const url = new URL(`${API_BASE_URL}/proposals`);
    url.searchParams.append('skip', (pagination.pageIndex * pagination.pageSize).toString());
    url.searchParams.append('limit', pagination.pageSize.toString());

    // Data Fetching
    const { data: apiData, error, isValidating } = useSWR(url.toString(), fetcher, {
        keepPreviousData: true,
    });

    const rows = apiData?.items || [];
    const totalRowCount = apiData?.total || 0;
    const isLoading = !apiData && !error;
    const isError = !!error;
    const isRefetching = isValidating;

    const columns = useMemo(() => [
        {
            accessorKey: 'proposal_id',
            header: 'ID', // Was proposal_id
            size: 90,
        },
        {
            accessorKey: 'customer_reference',
            header: 'Cliente',
            size: 150,
        },
        {
            accessorKey: 'proposal_name',
            header: 'Nome Proposta',
            size: 200,
        },
        {
            accessorKey: 'funnel_percentage',
            header: 'Etapa Funil',
            size: 150,
        },
        {
            accessorKey: 'total_value',
            header: 'Valor',
            size: 150,
            Cell: ({ cell }) => (
                <NumericFormat
                    value={cell.getValue() || 0}
                    displayType="text"
                    thousandSeparator="."
                    decimalSeparator=","
                    prefix="R$ "
                />
            ),
            muiTableHeadCellProps: {
                align: 'right',
            },
            muiTableBodyCellProps: {
                align: 'right',
            }
        },
    ], []);

    const table = useMaterialReactTable({
        columns,
        data: rows,
        enableColumnResizing: true,
        manualPagination: true,
        rowCount: totalRowCount,
        onPaginationChange: setPagination,
        state: {
            isLoading,
            pagination,
            showProgressBars: isRefetching,
            showAlertBanner: isError,
        },
        renderRowActions: ({ row }) => (
            <Button size="small" variant="outlined" onClick={() => handleOpenDetails(row)}>
                Detalhes
            </Button>
        ),
        muitablePaperProps: {
            sx: {
                boxShadow: 'none',
                border: '1px solid',
                borderColor: 'divider',
            }
        },
        localization: MRT_Localization_PT_BR,
        enableRowStriping: true,
        enableColumnBorders: true,
        enableRowActions: true,
    });

    if (isError) {
        console.error("ProposalsTable Fetch Error:", error);
        return (
            <Box display="flex" justifyContent="center" p={2}>
                <Alert severity="error" sx={{ width: '100%', maxWidth: 600 }}>
                    Erro ao carregar dados: {error?.message || 'Falha na conexão com o servidor'}
                </Alert>
            </Box>
        );
    }

    return (
        <>
            <MaterialReactTable table={table} />
            <ProposalDetailsModal
                open={isModalOpen}
                onClose={handleCloseDetails}
                proposalId={selectedProposalId}
            />
        </>
    );
}
