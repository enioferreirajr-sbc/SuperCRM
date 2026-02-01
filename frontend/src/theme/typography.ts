import { ThemeOptions } from '@mui/material/styles';

const pxToRem = (px: number) => `${px / 16}rem`;

const typography: ThemeOptions['typography'] = {
  htmlFontSize: 16,
  fontFamily: "'Public Sans', 'Roboto', 'Helvetica', 'Arial', sans-serif",

  h1: {
    fontSize: pxToRem(32),
    lineHeight: 1.25,
    fontWeight: 400
  },
  h2: {
    fontSize: pxToRem(28),
    lineHeight: 1.3,
    fontWeight: 400
  },
  h3: {
    fontSize: pxToRem(24),
    lineHeight: 1.3,
    fontWeight: 400
  },
  h4: {
    fontSize: pxToRem(20),
    lineHeight: 1.35,
    fontWeight: 400
  },
  h5: {
    fontSize: pxToRem(18),
    lineHeight: 1.4,
    fontWeight: 400
  },
  h6: {
    fontSize: pxToRem(16),
    lineHeight: 1.4,
    fontWeight: 400
  },

  subtitle1: {
    fontSize: pxToRem(14),
    lineHeight: 1.5,
    fontWeight: 400
  },
  subtitle2: {
    fontSize: pxToRem(13),
    lineHeight: 1.45,
    fontWeight: 500
  },

  body1: {
    fontSize: pxToRem(14),
    lineHeight: 1.5,
    fontWeight: 400
  },
  body2: {
    fontSize: pxToRem(13),
    lineHeight: 1.45,
    fontWeight: 400
  },

  button: {
    fontSize: pxToRem(13),
    lineHeight: 1.5,
    fontWeight: 500,
    textTransform: 'none'
  },

  caption: {
    fontSize: pxToRem(12),
    lineHeight: 1.4,
    fontWeight: 400
  },

  overline: {
    fontSize: pxToRem(11),
    lineHeight: 1.4,
    fontWeight: 500,
    textTransform: 'uppercase'
  }
};

export default typography;
