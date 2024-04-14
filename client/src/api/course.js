import request from '@/utils/request'

export function getCourseById(id) {
  return request({
    url: `/ftz/course/${id}/`, method: 'get'
  })
}

export function getCourseList(query) {
  return request({
    url: '/ftz/course/', method: 'get', params: query
  })
}

export function createCourse(data) {
  return request({
    url: '/ftz/course/', method: 'post', data
  })
}

export function updateCourse(id, data) {
  return request({
    url: `/ftz/course/${id}/`, method: 'put', data
  })
}

export function deleteCourse(id) {
  return request({
    url: `/ftz/course/${id}/`, method: 'delete'
  })
}
