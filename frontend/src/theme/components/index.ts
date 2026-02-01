import type { Components, Theme } from '@mui/material/styles';
import { muiButton } from './MuiButton';
import { muiIconButton } from './MuiIconButton';
import { muiAvatar } from './MuiAvatar';
import { cssBaseline } from './CssBaseline';

export function components(theme: Theme): Components {
  return {
    ...muiButton(theme),
    ...muiIconButton(theme),
    ...muiAvatar(theme),
    ...cssBaseline(theme)
  };
}
