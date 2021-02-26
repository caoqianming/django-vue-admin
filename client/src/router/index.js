import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    perms: ['admin','editor']    control the page perms (you can set multiple perms)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'             the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all perms can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },

  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: '首页', icon: 'dashboard' }
    }]
  },
  {
    path: '/changepassword',
    component: Layout,
    redirect: '/changepassword',
    name: 'ChangePW',
    meta: { title: '修改密码', icon: 'tree' },
    hidden:true,
    children: [
      {
        path: '',
        name: 'ChangePassword',
        component: () => import('@/views/system/changepassword'),
        meta: { title: '修改密码', noCache: true, icon: ''},
        hidden: true
      },
    ]
  },

]

/**
 * asyncRoutes
 * the routes that need to be dynamically loaded based on user perms
 */
export const asyncRoutes = [
  {
    path: '/system',
    component: Layout,
    redirect: '/system/user',
    name: 'System',
    meta: { title: '系统管理', icon: 'example', perms: ['system_manage'] },
    children: [
      {
        path: 'user',
        name: 'User',
        component: () => import('@/views/system/user.vue'),
        meta: { title: '用户管理', icon: 'user', perms: ['user_manage'] }
      },
      {
        path: 'organization',
        name: 'Organization',
        component: () => import('@/views/system/organization'),
        meta: { title: '部门管理', icon: 'tree', perms: ['org_manage'] }
      },
      {
        path: 'role',
        name: 'Role',
        component: () => import('@/views/system/role'),
        meta: { title: '角色管理', icon: 'lock', perms: ['role_manage'] }
      },
      {
        path: 'position',
        name: 'Postion',
        component: () => import('@/views/system/position'),
        meta: { title: '岗位管理', icon: 'position', perms: ['position_manage'] }
      },
      {
        path: 'dict',
        name: 'Dict',
        component: () => import('@/views/system/dict'),
        meta: { title: '数据字典', icon: 'example', perms: ['dict_manage'] }
      },
      {
        path: 'file',
        name: 'File',
        component: () => import('@/views/system/file'),
        meta: { title: '文件库', icon: 'documentation', perms: ['file_room'] }
      },
      {
        path: 'task',
        name: 'Task',
        component: () => import('@/views/system/task'),
        meta: { title: '定时任务', icon: 'list', perms: ['ptask_manage'] }
      }
    ]
  },
  {
    path: '/develop',
    component: Layout,
    redirect: '/develop/perm',
    name: 'Develop',
    meta: { title: '开发配置', icon: 'example', perms: ['dev_set'] },
    children: [
      {
        path: 'perm',
        name: 'Perm',
        component: () => import('@/views/system/perm'),
        meta: { title: '权限菜单', icon: 'example', perms: ['perm_manage'] }
      },
      {
        path: 'form-gen-link',
        component: Layout,
        children: [
          {
            path: 'https://jakhuang.github.io/form-generator/',
            meta: { title: '表单设计器', icon: 'link', perms: ['dev_form_gen'] }
          }
        ]
      },
      {
        path: 'docs-link',
        component: Layout,
        children: [
          {
            path: process.env.VUE_APP_BASE_API + '/docs/',
            meta: { title: '接口文档', icon: 'link', perms: ['dev_docs'] }
          }
        ]
      },
      {
        path: 'admin-link',
        component: Layout,
        children: [
          {
            path: process.env.VUE_APP_BASE_API + '/admin/',
            meta: { title: 'Django后台', icon: 'link', perms: ['dev_admin'] }
          }
        ]
      }
    ]
  },
  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
