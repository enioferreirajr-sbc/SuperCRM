import { createTheme } from '@mui/material/styles';
import { palette } from './palette';
import { typography } from './typography';
import { spacing } from './spacing';
import { shape } from './shape';
import { shadows } from './shadows';
import { components } from './components';

const baseTheme = createTheme({
  palette,
  typography,
  spacing,
  shape,
  shadows
});

export const theme = createTheme(baseTheme, {
  components: components(baseTheme)
});
