import type { Components, Theme } from '@mui/material/styles';
import { button } from './Button';
import { textField } from './TextField';
import { card } from './Card';
import { typography } from './Typography';
import { cssBaseline } from './CssBaseline';

export function components(theme: Theme): Components {
  return {
    ...button(theme),
    ...textField(theme),
    ...card(theme),
    ...typography(theme),
    ...cssBaseline(theme)
  };
}
