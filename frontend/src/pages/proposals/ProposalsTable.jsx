import { useState, useMemo } from 'react';
import {
    EditNotificationsOutlined
} from '@mui/icons-material';
import {
    MaterialReactTable,
    useMaterialReactTable,
} from 'material-react-table';
import { MRT_Localization_PT_BR } from 'material-react-table/locales/pt-BR';
import { Chip, Box, Alert, CircularProgress } from '@mui/material';
import useSWR from 'swr';
import { NumericFormat } from 'react-number-format';
import { API_BASE_URL } from '../../config/api';

// --- Modal Component ---
import { Dialog, DialogTitle, DialogContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, DialogActions, Typography, Grid } from '@mui/material';

function ProposalDetailsModal({ open, onClose, proposal }) {
    const { data: items, error } = useSWR(proposal ? `${API_BASE_URL}/proposals/${proposal.proposal_id}/items` : null, fetcher);

    const isLoading = !items && !error;

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>Detalhes da Proposta #{proposal?.proposal_id}</DialogTitle>
            <DialogContent dividers>
                {/* Header Info */}
                <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Cliente</Typography>
                        <Typography variant="body1">{proposal?.client_name}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Probabilidade</Typography>
                        <Typography variant="body1">{proposal?.probability}%</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Data Fechamento</Typography>
                        <Typography variant="body1">
                            {proposal?.closing_date ? new Date(proposal.closing_date).toLocaleDateString('pt-BR') : '-'}
                        </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Valor Total</Typography>
                        <Typography variant="h6" color="primary">
                            <NumericFormat value={proposal?.total_value || 0} displayType="text" thousandSeparator="." decimalSeparator="," prefix="R$ " />
                        </Typography>
                    </Grid>
                    <Grid item xs={12}>
                        {proposal?.is_dirty && <Chip label="Editado Manualmente" color="warning" size="small" />}
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
                                <TableCell align="right">Valor</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {isLoading ? (
                                <TableRow><TableCell colSpan={4} align="center">Carregando itens...</TableCell></TableRow>
                            ) : items?.length > 0 ? (
                                items.map((item, index) => (
                                    <TableRow key={index}>
                                        <TableCell>{item.product_name}</TableCell>
                                        <TableCell>{item.type_name}</TableCell>
                                        <TableCell>{item.team_name}</TableCell>
                                        <TableCell align="right">
                                            <NumericFormat value={item.value || 0} displayType="text" thousandSeparator="." decimalSeparator="," prefix="R$ " />
                                        </TableCell>
                                    </TableRow>
                                ))
                            ) : (
                                <TableRow><TableCell colSpan={4} align="center">Nenhum item encontrado (ou erro ao carregar).</TableCell></TableRow>
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

const fetcher = (url) => fetch(url).then((res) => res.json());

export default function ProposalsTable() {
    // MRT State
    const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
    const [sorting, setSorting] = useState([]); // [{ id: 'name', desc: true }]
    const [globalFilter, setGlobalFilter] = useState('');

    // Modal State
    const [selectedProposal, setSelectedProposal] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const handleOpenDetails = (row) => {
        setSelectedProposal(row.original);
        setIsModalOpen(true);
    };

    const handleCloseDetails = () => {
        setIsModalOpen(false);
        setSelectedProposal(null);
    };

    // Construct URL for SWR
    const url = new URL(`${API_BASE_URL}/proposals/`);
    url.searchParams.append('skip', (pagination.pageIndex * pagination.pageSize).toString());
    url.searchParams.append('limit', pagination.pageSize.toString());

    if (sorting.length > 0) {
        url.searchParams.append('sort_by', sorting[0].id);
        url.searchParams.append('sort_order', sorting[0].desc ? 'desc' : 'asc');
    }

    if (globalFilter) {
        url.searchParams.append('search', globalFilter);
    }

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


        // ... (inside columns definition)
        {
            accessorKey: 'client_name', // Was client_name
            header: 'Cliente',
            size: 150,
            Cell: ({ cell, row }) => (
                <Box display="flex" alignItems="center" gap={0.5}>
                    {row.original.is_dirty && (
                        <EditNotificationsOutlined
                            color="warning"
                            fontSize="small"
                            titleAccess="Editado Manualmente"
                        />
                    )}
                    <Typography variant="body2">{cell.getValue()}</Typography>
                </Box>
            ),
        },
        {
            accessorKey: 'closing_date', // Was created_at
            header: 'Data Fechamento',
            size: 150,
            Cell: ({ cell }) => {
                const val = cell.getValue();
                if (!val) return '-';
                return new Date(val).toLocaleDateString('pt-BR');
            },
        },
        {
            accessorKey: 'total_value', // Was total_value
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
        {
            accessorKey: 'probability',
            header: 'Prob. (%)',
            size: 100,
            Cell: ({ cell }) => (
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="body2">{cell.getValue()}%</Typography>
                    {/* Add visual indicator if needed */}
                </Box>
            ),
        }
    ], []);

    const table = useMaterialReactTable({
        columns,
        data: rows,
        enableColumnResizing: true,
        manualPagination: true,
        manualSorting: true,
        manualFiltering: true,
        rowCount: totalRowCount,
        onPaginationChange: setPagination,
        onSortingChange: setSorting,
        onGlobalFilterChange: setGlobalFilter,
        state: {
            isLoading,
            pagination,
            sorting,
            globalFilter,
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
                proposal={selectedProposal}
            />
        </>
    );
}
