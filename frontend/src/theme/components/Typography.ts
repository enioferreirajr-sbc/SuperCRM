import type { Components, Theme } from '@mui/material/styles';

export function typography(theme: Theme): Components {
  return {
    MuiTypography: {
      styleOverrides: {
        root: {
          color: theme.palette.text.primary
        }
      }
    }
  };
}
