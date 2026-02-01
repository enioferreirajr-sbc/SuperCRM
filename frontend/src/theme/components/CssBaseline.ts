import type { Components, Theme } from '@mui/material/styles';

export function cssBaseline(theme: Theme): Components {
  return {
    MuiCssBaseline: {
      styleOverrides: {
        '*': {
          boxSizing: 'border-box'
        },
        html: {
          height: '100%',
          WebkitFontSmoothing: 'antialiased',
          MozOsxFontSmoothing: 'grayscale'
        },
        body: {
          margin: 0,
          minHeight: '100%',
          backgroundColor: theme.palette.background.default,
          color: theme.palette.onSurface
        },
        '#root': {
          minHeight: '100%'
        }
      }
    }
  };
}
