import type { PaletteOptions } from '@mui/material/styles';

declare module '@mui/material/styles' {
  interface Palette {
    tertiary: Palette['primary'];
    surface: string;
    surfaceVariant: string;
    onSurface: string;
    outline: string;
    outlineVariant: string;
  }

  interface PaletteOptions {
    tertiary?: PaletteOptions['primary'];
    surface?: string;
    surfaceVariant?: string;
    onSurface?: string;
    outline?: string;
    outlineVariant?: string;
  }
}

const lightScheme = {
  primary: '#39608F',
  onPrimary: '#FFFFFF',
  primaryContainer: '#D3E4FF',
  onPrimaryContainer: '#1D4875',
  primaryFixedDim: '#A3C9FE',
  secondary: '#126B56',
  onSecondary: '#FFFFFF',
  secondaryContainer: '#A3F2D8',
  onSecondaryContainer: '#005140',
  secondaryFixedDim: '#87D6BC',
  tertiary: '#616219',
  onTertiary: '#FFFFFF',
  tertiaryContainer: '#E7E790',
  onTertiaryContainer: '#494A00',
  tertiaryFixedDim: '#CACB77',
  error: '#904A43',
  onError: '#FFFFFF',
  errorContainer: '#FFDAD6',
  onErrorContainer: '#73332D',
  background: '#F8F9FF',
  onBackground: '#191C20',
  surface: '#F8F9FF',
  onSurface: '#191C20',
  surfaceVariant: '#DFE2EB',
  onSurfaceVariant: '#43474E',
  outline: '#73777F',
  outlineVariant: '#C3C6CF'
};

const neutral = {
  0: '#000000',
  5: '#111111',
  10: '#1C1B1B',
  15: '#262626',
  20: '#313030',
  25: '#3C3B3B',
  30: '#484646',
  35: '#535252',
  40: '#5F5E5E',
  50: '#787776',
  60: '#929090',
  70: '#ADAAAA',
  80: '#C9C6C5',
  90: '#E5E2E1',
  95: '#F4F0EF',
  98: '#FCF8F8',
  99: '#FDFCFF',
  100: '#FFFFFF'
};

export const palette: PaletteOptions = {
  mode: 'light',
  primary: {
    main: lightScheme.primary,
    light: lightScheme.primaryContainer,
    dark: lightScheme.primaryFixedDim,
    contrastText: lightScheme.onPrimary
  },
  secondary: {
    main: lightScheme.secondary,
    light: lightScheme.secondaryContainer,
    dark: lightScheme.secondaryFixedDim,
    contrastText: lightScheme.onSecondary
  },
  tertiary: {
    main: lightScheme.tertiary,
    light: lightScheme.tertiaryContainer,
    dark: lightScheme.tertiaryFixedDim,
    contrastText: lightScheme.onTertiary
  },
  error: {
    main: lightScheme.error,
    light: lightScheme.errorContainer,
    dark: lightScheme.onErrorContainer,
    contrastText: lightScheme.onError
  },
  info: {
    main: lightScheme.primary,
    contrastText: lightScheme.onPrimary
  },
  success: {
    main: lightScheme.secondary,
    contrastText: lightScheme.onSecondary
  },
  warning: {
    main: lightScheme.tertiary,
    contrastText: lightScheme.onTertiary
  },
  background: {
    default: lightScheme.background,
    paper: lightScheme.surface
  },
  surface: lightScheme.surface,
  surfaceVariant: lightScheme.surfaceVariant,
  onSurface: lightScheme.onSurface,
  outline: lightScheme.outline,
  outlineVariant: lightScheme.outlineVariant,
  text: {
    primary: lightScheme.onSurface,
    secondary: lightScheme.onSurfaceVariant
  },
  divider: lightScheme.outlineVariant,
  grey: {
    0: neutral[0],
    50: neutral[95],
    100: neutral[90],
    200: neutral[80],
    300: neutral[70],
    400: neutral[60],
    500: neutral[50],
    600: neutral[40],
    700: neutral[30],
    800: neutral[20],
    900: neutral[10],
    A100: neutral[98],
    A200: neutral[99],
    A400: neutral[5],
    A700: neutral[15]
  }
};
