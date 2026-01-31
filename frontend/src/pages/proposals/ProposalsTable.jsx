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
import MoreVert from '@mui/icons-material/MoreVert';

// --- Modal Component ---
import { Dialog, DialogTitle, DialogContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, DialogActions, Typography, Grid, MenuItem } from '@mui/material';

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

                        {/* Header Info */}
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

export default function ProposalsTable() {
    // MRT State
    const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });

    // Modal State
    const [selectedProposalId, setSelectedProposalId] = useState(null);
    const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);

    const handleOpenProposalDetails = (row) => {
        setSelectedProposalId(row.original.proposal_id);
        setIsDetailsModalOpen(true);
    };

    const handleCloseDetails = () => {
        setIsDetailsModalOpen(false);
    };

    const handleChangeFunnelStatus = (row) => {
        console.info('Alterar status do funil:', row.original.proposal_id);
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
            size: 100,
            minSize: 100,
            maxSize: 100,
        },
        {
            accessorKey: 'customer_reference',
            header: 'Cliente',
            minSize: 168,
            grow: 1,
        },
        {
            accessorKey: 'proposal_name',
            header: 'Nome Proposta',
            minSize: 441,
            grow: 2,
        },
        {
            accessorKey: 'funnel_percentage',
            header: 'Etapa Funil',
            minSize: 260,
            grow: 1,
        },
        {
            accessorKey: 'total_value',
            header: 'Valor',
            size: 140,
            minSize: 140,
            maxSize: 140,
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
        renderRowActionMenuItems: ({ row, closeMenu }) => [
            <MenuItem
                key="view-details"
                onClick={() => {
                    handleOpenProposalDetails(row);
                    closeMenu();
                }}
            >
                Detalhes
            </MenuItem>,
            <MenuItem
                key="change-funnel-status"
                onClick={() => {
                    handleChangeFunnelStatus(row);
                    closeMenu();
                }}
            >
                Alterar status do funil
            </MenuItem>,
        ],
        displayColumnDefOptions: {
            'mrt-row-actions': {
                header: 'Ações',
                size: 80,
                minSize: 80,
                maxSize: 80,
                enableResizing: false,
                muiTableHeadCellProps: {
                    align: 'center',
                },
                muiTableBodyCellProps: {
                    align: 'center',
                },
            },
        },
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
        icons: {
            MoreHorizIcon: MoreVert,
        },
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
                open={isDetailsModalOpen}
                onClose={handleCloseDetails}
                proposalId={selectedProposalId}
            />
        </>
    );
}
