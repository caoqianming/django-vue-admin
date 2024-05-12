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
    hidden: true,
    children: [
      {
        path: '',
        name: 'ChangePassword',
        component: () => import('@/views/system/changepassword'),
        meta: { title: '修改密码', noCache: true, icon: '' },
        hidden: true
      }
    ]
  }

]

/**
 * asyncRoutes
 * the routes that need to be dynamically loaded based on user perms
 */
export const asyncRoutes = [
  {
    path: '/ftz',
    component: Layout,
    redirect: '/ftz/course',
    name: 'new',
    meta: { title: '课包管理', icon: 'example', perms: ['course_manage'] },
    children: [
      {
        path: 'course',
        name: 'course',
        component: () => import('@/views/ftz/course.vue'),
        meta: { title: '课程管理', icon: 'example', perms: ['course_index'] }
      },
      {
        path: 'lesson',
        name: 'lesson',
        component: () => import('@/views/ftz/lesson.vue'),
        meta: { title: '课时管理', icon: 'example', perms: ['lesson_index'] }
      },
      {
        path: 'card',
        name: 'card',
        component: () => import('@/views/ftz/card'),
        meta: { title: '卡片管理', icon: 'example', perms: ['card_index'] }
      },
      {
        path: 'material',
        name: 'material',
        component: () => import('@/views/ftz/material.vue'),
        meta: { title: '素材管理', icon: 'example', perms: ['material_index'] }
      },
      {
        path: 'enum_config',
        name: 'enum_config',
        component: () => import('@/views/ftz/enum_config'),
        meta: { title: '配置管理', icon: 'example', perms: ['enum_config_index'] }
      }
    ]
  },
  // {
  //   path: '/workflow',
  //   component: Layout,
  //   redirect: '/workflow/index',
  //   name: 'workflow',
  //   meta: { title: '工作流', icon: 'example', perms: ['workflow_manage'] },
  //   children: [
  //     {
  //       path: 'index',
  //       name: 'index',
  //       component: () => import('@/views/workflow/index'),
  //       meta: { title: '工作流', icon: 'example', perms: ['workflow_index'] }
  //     },
  //     {
  //       path: 'ticket',
  //       name: 'ticket',
  //       component: () => import('@/views/workflow/ticket'),
  //       meta: { title: '工单管理', icon: 'example', noCache: true, perms: ['workflow_ticket'] }
  //     },
  //     {
  //       path: 'workFlowTickets',
  //       name: 'workFlowTickets',
  //       component: () => import('@/views/workflow/workFlowTickets'),
  //       meta: { title: '工单', icon: 'example', noCache: true },
  //       hidden: true
  //     },
  //     {
  //       path: 'configuration',
  //       name: 'configuration',
  //       component: () => import('@/views/workflow/configuration'),
  //       meta: { title: '工作流配置', icon: 'example' },
  //       hidden: true
  //     },
  //     {
  //       path: 'ticketHandle',
  //       name: 'ticketHandle',
  //       component: () => import('@/views/workflow/ticketHandle'),
  //       meta: { title: '工单处理', icon: 'example', noCache: true },
  //       hidden: true
  //     },
  //     {
  //       path: 'ticketDetail',
  //       name: 'ticketDetail',
  //       component: () => import('@/views/workflow/ticketDetail'),
  //       meta: { title: '工单详情', icon: 'example', noCache: true },
  //       hidden: true
  //     }
  //   ]
  // },
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
        component: () => import('@/views/system/add.vue'),
        meta: { title: '课程列表', icon: 'user', perms: ['add_manage'] }
      },
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
    path: '/monitor',
    component: Layout,
    redirect: '/monitor/service',
    name: 'Monitor',
    meta: { title: '系统监控', icon: 'example', perms: ['monitor_set'] },
    children: [
      {
        path: 'service',
        name: 'service',
        component: () => import('@/views/monitor/service'),
        meta: { title: '服务监控', icon: 'example', perms: ['service_manage'] }
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
      // {
      //   path: 'docs',
      //   component: Layout,
      //   children: [
      //     {
      //       path: process.env.VUE_APP_BASE_API + '/docs/',
      //       meta: { title: '接口文档', icon: 'link', perms: ['dev_docs'] }
      //     }
      //   ]
      // },
      {
        path: 'swagger',
        component: Layout,
        children: [
          {
            path: process.env.VUE_APP_BASE_API + '/swagger/',
            meta: { title: 'Swagger文档', icon: 'link', perms: ['dev_docs'] }
          }
        ]
      },
      // {
      //   path: 'admin-link',
      //   component: Layout,
      //   children: [
      //     {
      //       path: process.env.VUE_APP_BASE_API + '/admin/',
      //       meta: { title: 'Django后台', icon: 'link', perms: ['dev_admin'] }
      //     }
      //   ]
      // }
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
