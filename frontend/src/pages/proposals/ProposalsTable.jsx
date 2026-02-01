import { useState, useMemo } from 'react';
import {
    MaterialReactTable,
    useMaterialReactTable,
} from 'material-react-table';
import { MRT_Localization_PT_BR } from 'material-react-table/locales/pt-BR';
import { Box, Alert, MenuItem } from '@mui/material';
import useSWR from 'swr';
import { NumericFormat } from 'react-number-format';
import { API_BASE_URL } from '../../config/api';
import MoreVert from '@mui/icons-material/MoreVert';
import ProposalDetailsModal from '../../components/ProposalDetailsModal';

const fetcher = async (url) => {
    const res = await fetch(url);
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const message = err?.message || err?.detail || 'Erro ao carregar dados.';
        throw new Error(message);
    }
    return res.json();
};

export default function ProposalsTable() {
    // MRT State
    const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });

    // Modal State
    const [selectedProposalId, setSelectedProposalId] = useState(null);
    const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);

    const handleOpenDetails = (row) => {
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
                    handleOpenDetails(row);
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
