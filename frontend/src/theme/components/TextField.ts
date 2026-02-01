import type { Components, Theme } from '@mui/material/styles';

export function textField(theme: Theme): Components {
  return {
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
        size: 'medium',
        InputLabelProps: { shrink: true }
      }
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: theme.palette.text.secondary
        }
      }
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: theme.shape.borderRadius,
          backgroundColor: theme.palette.surface,
          color: theme.palette.onSurface,
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: theme.palette.outlineVariant
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: theme.palette.outline
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: theme.palette.primary.main
          }
        },
        input: {
          padding: theme.spacing(1.5, 1.5),
          minHeight: theme.spacing(3)
        },
        inputMultiline: {
          padding: 0
        },
        multiline: {
          padding: theme.spacing(1.5, 1.5)
        }
      }
    },
    MuiFormHelperText: {
      styleOverrides: {
        root: {
          color: theme.palette.text.secondary
        }
      }
    }
  };
}
