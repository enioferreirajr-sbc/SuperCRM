import { RouterProvider } from 'react-router-dom';

// project imports
import router from 'routes';

import ScrollTop from 'components/ScrollTop';

// ==============================|| APP - THEME, ROUTER, LOCAL ||============================== //

export default function App() {
  return (
    <ScrollTop>
      <RouterProvider router={router} />
    </ScrollTop>
  );
}
