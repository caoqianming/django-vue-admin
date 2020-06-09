import defaultSettings from '@/settings'

const title = defaultSettings.title || '认证系统'

export default function getPageTitle(pageTitle) {
  if (pageTitle) {
    return `${pageTitle} - ${title}`
  }
  return `${title}`
}
