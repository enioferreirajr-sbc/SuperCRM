import Box from '@mui/material/Box';
import InputAdornment from '@mui/material/InputAdornment';
import TextField from '@mui/material/TextField';
import SearchIcon from '@mui/icons-material/Search';

// ==============================|| HEADER CONTENT - SEARCH ||============================== //

export default function Search() {
  return (
    <Box sx={{ width: '100%', ml: { xs: 0, md: 1 } }}>
      <TextField
        size="small"
        placeholder="Pesquisar…"
        sx={{ width: { xs: '100%', md: 224 } }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon fontSize="small" />
            </InputAdornment>
          )
        }}
      />
    </Box>
  );
}
