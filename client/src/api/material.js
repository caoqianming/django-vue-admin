import request from '@/utils/request'

export function getMaterialById(id) {
  return request({
    url: `/ftz/material/${id}/`, method: 'get'
  })
}

export function getMaterialList(query) {
  return request({
    url: '/ftz/material/', method: 'get', params: query
  })
}

export function createMaterial(data) {
  return request({
    url: '/ftz/material/', method: 'post', data
  })
}

export function updateMaterial(id, data) {
  return request({
    url: `/ftz/material/${id}/`, method: 'put', data
  })
}

export function deleteMaterial(id) {
  return request({
    url: `/ftz/material/${id}/`, method: 'delete'
  })
}
