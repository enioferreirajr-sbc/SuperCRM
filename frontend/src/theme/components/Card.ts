import type { Components, Theme } from '@mui/material/styles';

export function card(theme: Theme): Components {
  return {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: theme.palette.surface,
          borderRadius: theme.shape.borderRadius,
          boxShadow: theme.shadows[1]
        }
      }
    }
  };
}
