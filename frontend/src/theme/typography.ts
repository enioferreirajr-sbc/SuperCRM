import type { TypographyOptions } from '@mui/material/styles/createTypography';

const pxToRem = (px: number) => `${px / 16}rem`;
const ls = (px: number) => `${px / 16}rem`;

export const typography: TypographyOptions = {
  fontFamily: "'Public Sans', 'Roboto', 'Helvetica', 'Arial', sans-serif",
  h1: {
    fontSize: pxToRem(57),
    lineHeight: pxToRem(64),
    fontWeight: 400,
    letterSpacing: ls(-0.25)
  },
  h2: {
    fontSize: pxToRem(45),
    lineHeight: pxToRem(52),
    fontWeight: 400,
    letterSpacing: ls(0)
  },
  h3: {
    fontSize: pxToRem(36),
    lineHeight: pxToRem(44),
    fontWeight: 400,
    letterSpacing: ls(0)
  },
  h4: {
    fontSize: pxToRem(32),
    lineHeight: pxToRem(40),
    fontWeight: 400,
    letterSpacing: ls(0)
  },
  h5: {
    fontSize: pxToRem(28),
    lineHeight: pxToRem(36),
    fontWeight: 400,
    letterSpacing: ls(0)
  },
  h6: {
    fontSize: pxToRem(24),
    lineHeight: pxToRem(32),
    fontWeight: 400,
    letterSpacing: ls(0)
  },
  subtitle1: {
    fontSize: pxToRem(22),
    lineHeight: pxToRem(28),
    fontWeight: 400,
    letterSpacing: ls(0)
  },
  subtitle2: {
    fontSize: pxToRem(16),
    lineHeight: pxToRem(24),
    fontWeight: 500,
    letterSpacing: ls(0.15)
  },
  body1: {
    fontSize: pxToRem(16),
    lineHeight: pxToRem(24),
    fontWeight: 400,
    letterSpacing: ls(0.5)
  },
  body2: {
    fontSize: pxToRem(14),
    lineHeight: pxToRem(20),
    fontWeight: 400,
    letterSpacing: ls(0.25)
  },
  button: {
    fontSize: pxToRem(14),
    lineHeight: pxToRem(20),
    fontWeight: 500,
    letterSpacing: ls(0.1),
    textTransform: 'none'
  },
  caption: {
    fontSize: pxToRem(12),
    lineHeight: pxToRem(16),
    fontWeight: 400,
    letterSpacing: ls(0.4)
  },
  overline: {
    fontSize: pxToRem(11),
    lineHeight: pxToRem(16),
    fontWeight: 500,
    letterSpacing: ls(0.5),
    textTransform: 'uppercase'
  }
};
