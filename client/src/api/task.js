import request from '@/utils/request'

export function getptaskList(query) {
  return request({
    url: '/system/ptask/',
    method: 'get',
    params: query
  })
}

export function getTaskAll() {
  return request({
    url: '/system/task/',
    method: 'get'
  })
}
export function createptask(data) {
  return request({
    url: '/system/ptask/',
    method: 'post',
    data
  })
}

export function updateptask(id, data) {
  return request({
    url: `/system/ptask/${id}/`,
    method: 'put',
    data
  })
}

export function toggletask(id) {
  return request({
    url: `/system/ptask/${id}/toggle/`,
    method: 'put'
  })
}

export function deleteptask(id) {
  return request({
    url: `/system/ptask/${id}/`,
    method: 'delete'
  })
}