import { useState, useMemo } from 'react';
import {
    MaterialReactTable,
    useMaterialReactTable,
} from 'material-react-table';
import { MRT_Localization_PT_BR } from 'material-react-table/locales/pt-BR';
import { Chip, Box } from '@mui/material';
import useSWR from 'swr';
import { NumericFormat } from 'react-number-format';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const statusColorMap = {
    'Won': 'success',
    'Lost': 'error',
    'Open': 'primary',
    'Draft': 'warning',
    'Submitted': 'info'
};

function StatusChip({ status }) {
    const color = statusColorMap[status] || 'default';
    return <Chip label={status || 'Unknown'} color={color} size="small" variant="light" />;
}

// --- Modal Component ---
import { Dialog, DialogTitle, DialogContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, DialogActions, Typography, Grid } from '@mui/material';

function ProposalDetailsModal({ open, onClose, proposal }) {
    const { data: items, error } = useSWR(proposal ? `${API_URL}/proposals/${proposal.proposal_id}/items` : null, fetcher);

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
                        <Typography variant="subtitle2" color="textSecondary">Status</Typography>
                        <StatusChip status={proposal?.status} />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Funil</Typography>
                        <Typography variant="body1">{proposal?.funnel_stage}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="textSecondary">Total (Agregado)</Typography>
                        <Typography variant="h6" color="primary">
                            <NumericFormat value={proposal?.total_value || 0} displayType="text" thousandSeparator="." decimalSeparator="," prefix="R$ " />
                        </Typography>
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
                                <TableRow><TableCell colSpan={4} align="center">Nenhum item encontrado.</TableCell></TableRow>
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
    const url = new URL(`${API_URL}/proposals/`);
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
            header: 'ID',
            size: 90,
        },
        {
            accessorKey: 'proposal_name',
            header: 'Nome da Proposta',
            size: 250,
        },
        {
            accessorKey: 'client_name',
            header: 'Cliente',
            size: 150,
        },
        // Product Column Removed for Consolidated View
        {
            accessorKey: 'funnel_stage',
            header: 'Funil',
            size: 150,
            Cell: ({ cell }) => (
                <Chip
                    label={cell.getValue() || 'N/A'}
                    size="small"
                    variant="outlined"
                    sx={{
                        borderColor: 'primary.main',
                        color: 'primary.main',
                        fontSize: '0.75rem',
                        height: 24
                    }}
                />
            ),
        },
        {
            accessorKey: 'total_value',
            header: 'Valor Total',
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
            accessorKey: 'status',
            header: 'Status',
            size: 120,
            Cell: ({ cell }) => <StatusChip status={cell.getValue()} />,
            muiTableHeadCellProps: {
                align: 'center',
            },
            muiTableBodyCellProps: {
                align: 'center',
            }
        },
    ], []);

    const table = useMaterialReactTable({
        columns,
        data: rows,
        manualPagination: true,
        manualSorting: true,
        manualFiltering: true, // We use global filter as the main search
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
        localization: MRT_Localization_PT_BR,
        enableRowStriping: true,
        enableColumnBorders: true,
        enableRowActions: true,
        renderRowActions: ({ row }) => (
            <Button size="small" variant="outlined" onClick={() => handleOpenDetails(row)}>
                Detalhes
            </Button>
        ),
        muitablePaperProps: {
            sx: {
                // Remove shadow if needed or keep default
                boxShadow: 'none',
                border: '1px solid',
                borderColor: 'divider',
            }
        },
        muiTableHeadCellProps: {
            sx: {
                backgroundColor: (theme) => theme.palette.mode === 'light' ? theme.palette.grey[200] : theme.palette.grey[800],
                fontWeight: 'bold',
                borderBottom: '1px solid',
                borderColor: 'divider',
            },
        },
        muiTableBodyCellProps: {
            sx: {
                borderRight: '1px solid',
                borderColor: 'divider',
            },
        },
    });

    if (isError) {
        return <Box p={2}>Erro ao carregar dados.</Box>;
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
