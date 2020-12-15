import request from '@/utils/request'

export function getTaskList(query) {
  return request({
    url: '/system/task/',
    method: 'get',
    params: query
  })
}

export function getTaskcodeAll() {
  return request({
    url: '/system/taskcode/',
    method: 'get'
  })
}