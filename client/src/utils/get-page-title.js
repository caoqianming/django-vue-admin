import defaultSettings from '@/settings'

const title = defaultSettings.title || 'Django Vue Admin'

export default function getPageTitle(pageTitle) {
  if (pageTitle) {
    return `${pageTitle} - ${title}`
  }
  return `${title}`
}
