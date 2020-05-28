import request from '@/utils/request'

export function getPositionAll() {
  return request({
    url: '/system/position/',
    method: 'get'
  })
}

export function createPosition(data) {
  return request({
    url: '/system/position/',
    method: 'post',
    data
  })
}

export function updatePosition(id, data) {
  return request({
    url: `/system/position/${id}/`,
    method: 'put',
    data
  })
}

export function deletePosition(id) {
  return request({
    url: `/system/position/${id}/`,
    method: 'delete'
  })
}
