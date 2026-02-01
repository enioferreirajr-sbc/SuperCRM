import type { Components, Theme } from '@mui/material/styles';

export function muiAvatar(theme: Theme): Components {
  return {
    MuiAvatar: {
      styleOverrides: {
        root: {
          backgroundColor: theme.palette.surfaceVariant,
          color: theme.palette.text.primary
        }
      }
    }
  };
}
