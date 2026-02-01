import type { Components, Theme } from '@mui/material/styles';

export function muiIconButton(theme: Theme): Components {
  return {
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: theme.shape.borderRadius,
          padding: theme.spacing(1),
          color: theme.palette.text.primary,
          '&:hover': {
            backgroundColor: theme.palette.surfaceVariant
          }
        }
      }
    }
  };
}
