// assets
import { DashboardOutlined, FileTextOutlined } from '@ant-design/icons';

// icons
const icons = {
  DashboardOutlined,
  FileTextOutlined
};

// ==============================|| MENU ITEMS - DASHBOARD ||============================== //

const dashboard = {
  id: 'group-dashboard',
  title: 'Navigation',
  type: 'group',
  children: [
    {
      id: 'dashboard',
      title: 'Dashboard',
      type: 'item',
      url: '/dashboard/default',
      icon: icons.DashboardOutlined,
      breadcrumbs: false
    },
    {
      id: 'proposals',
      title: 'Propostas',
      type: 'item',
      url: '/proposals',
      icon: icons.FileTextOutlined,
      breadcrumbs: true
    }
  ]
};

export default dashboard;
