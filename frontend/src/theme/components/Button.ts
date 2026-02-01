import type { Components, Theme } from '@mui/material/styles';

export function button(theme: Theme): Components {
  return {
    MuiButton: {
      defaultProps: {
        disableElevation: true
      },
      styleOverrides: {
        root: {
          borderRadius: theme.shape.borderRadius,
          textTransform: 'none',
          padding: theme.spacing(1, 2),
          fontWeight: theme.typography.button?.fontWeight
        },
        contained: {
          backgroundColor: theme.palette.primary.main,
          color: theme.palette.primary.contrastText,
          '&:hover': {
            backgroundColor: theme.palette.primary.dark
          }
        },
        outlined: {
          borderColor: theme.palette.outlineVariant,
          color: theme.palette.primary.main,
          '&:hover': {
            borderColor: theme.palette.outline,
            backgroundColor: theme.palette.surfaceVariant
          }
        },
        text: {
          color: theme.palette.primary.main,
          '&:hover': {
            backgroundColor: theme.palette.surfaceVariant
          }
        }
      }
    }
  };
}
