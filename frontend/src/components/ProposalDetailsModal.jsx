import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  InputAdornment,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import UpdateIcon from '@mui/icons-material/Update';
import CommentIcon from '@mui/icons-material/Comment';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';

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

  const headerText = `#${proposalId} · ${proposal?.customer_reference || '-'} · ${
    proposal?.proposal_name || '-'
  }`;

  const totalGeral = items.reduce((sum, item) => sum + (Number(item.total_sales) || 0), 0);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle
        sx={{
          bgcolor: 'primary.main',
          color: 'common.white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 2,
          pr: 1
        }}
      >
        <Typography
          variant="subtitle1"
          sx={{
            color: 'common.white',
            fontWeight: 600,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }}
          title={headerText}
        >
          {headerText}
        </Typography>

        <IconButton onClick={onClose} aria-label="Fechar" sx={{ color: 'common.white' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

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
              <Grid item xs={12} md={4}>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                  Etapa do funil
                </Typography>
                <Chip
                  label={proposal?.funnel_percentage || '-'}
                  color="primary"
                  variant="outlined"
                  sx={{ width: '100%' }}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  disabled
                  label="Data da proposta"
                  value={formatDate(proposal?.business_proposal_date)}
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <CalendarMonthIcon />
                      </InputAdornment>
                    )
                  }}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  disabled
                  label="Data do status"
                  value={formatDate(proposal?.last_status_date)}
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <UpdateIcon />
                      </InputAdornment>
                    )
                  }}
                />
              </Grid>

              <Grid item xs={12} md={12}>
                <TextField
                  fullWidth
                  size="small"
                  disabled
                  label="Último comentário"
                  value={proposal?.last_note || '-'}
                  multiline
                  minRows={2}
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start" sx={{ alignSelf: 'flex-start', mt: 1 }}>
                        <CommentIcon />
                      </InputAdornment>
                    )
                  }}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  disabled
                  label="Contato"
                  value={proposal?.recipient_name || '-'}
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonIcon />
                      </InputAdornment>
                    )
                  }}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  disabled
                  label="E-mail"
                  value={proposal?.recipient_email || '-'}
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <EmailIcon />
                      </InputAdornment>
                    )
                  }}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                  Status
                </Typography>
                <Chip
                  label={proposal?.proposal_status || '-'}
                  color="primary"
                  variant="outlined"
                  sx={{ width: '100%' }}
                />
              </Grid>
            </Grid>

            <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
              Itens da Proposta
            </Typography>

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
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        Carregando itens...
                      </TableCell>
                    </TableRow>
                  ) : items.length > 0 ? (
                    items.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>{item.product_name}</TableCell>
                        <TableCell>{item.proposal_type_name}</TableCell>
                        <TableCell>{item.team_name}</TableCell>
                        <TableCell>{item.owner}</TableCell>
                        <TableCell align="right">
                          <NumericFormat
                            value={item.total_sales || 0}
                            displayType="text"
                            thousandSeparator="."
                            decimalSeparator=","
                            prefix="R$ "
                          />
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        Nenhum item encontrado.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
            Total Geral:{' '}
            <NumericFormat
              value={totalGeral}
              displayType="text"
              thousandSeparator="."
              decimalSeparator=","
              prefix="R$ "
            />
          </Typography>

          <Button onClick={onClose} color="primary" variant="contained">
            Fechar
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
}
