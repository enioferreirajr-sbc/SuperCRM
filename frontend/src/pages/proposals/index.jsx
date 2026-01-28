import { Typography } from '@mui/material';
import MainCard from 'components/MainCard';
import ImportProposalBtn from 'components/ImportProposalBtn';
import ProposalsTable from './ProposalsTable';

export default function ProposalsPage() {
    return (
        <MainCard
            title="Propostas Comerciais"
            secondary={
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <ImportProposalBtn />
                </div>
            }
        >
            <ProposalsTable />
        </MainCard>
    );
}
