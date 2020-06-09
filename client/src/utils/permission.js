import store from '@/store'

/**
 * @param {Array} value
 * @returns {Boolean}
 * @example see @/views/permission/directive.vue
 */
export default function checkPermission(value) {
  if (value && value instanceof Array && value.length > 0) {
    const perms = store.getters && store.getters.perms
    const permissionperms = value
    if (perms.includes('admin')) {
      return true
    } // 如果是超管,都可以操作
    const hasPermission = perms.some(perm => {
      return permissionperms.includes(perm)
    })

    if (!hasPermission) {
      return false
    }
    return true
  } else {
    console.error(`need perms! Like v-permission="['admin','editor']"`)
    return false
  }
}
