import request from '@/utils/request'

export function getEnumConfigById(id) {
  return request({
    url: `/ftz/enum_config/${id}/`, method: 'get'
  })
}

export function getEnumConfigList(query) {
  return request({
    url: '/ftz/enum_config/', method: 'get', params: query
  })
}

export function createEnumConfig(data) {
  return request({
    url: '/ftz/enum_config/', method: 'post', data
  })
}

export function updateEnumConfig(id, data) {
  return request({
    url: `/ftz/enum_config/${id}/`, method: 'put', data
  })
}

export function deleteEnumConfig(id) {
  return request({
    url: `/ftz/enum_config/${id}/`, method: 'delete'
  })
}
