import request from '@/utils/request'

export function getOrgAll() {
  return request({
    url: '/system/organization/',
    method: 'get'
  })
}
export function getOrgList(query) {
  return request({
    url: '/system/organization/',
    method: 'get',
    params: query
  })
}
export function createOrg(data) {
  return request({
    url: '/system/organization/',
    method: 'post',
    data
  })
}
export function updateOrg(id, data) {
  return request({
    url: `/system/organization/${id}/`,
    method: 'put',
    data
  })
}
export function deleteOrg(id) {
  return request({
    url: `/system/organization/${id}/`,
    method: 'delete'
  })
}
