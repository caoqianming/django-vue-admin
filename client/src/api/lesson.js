import request from '@/utils/request'


export function getLessonById(id) {
  return request({
    url: `/ftz/lesson/${id}/`, method: 'get'
  })
}

export function getLessonList(query) {
  return request({
    url: '/ftz/lesson/', method: 'get', params: query
  })
}

export function createLesson(data) {
  return request({
    url: '/ftz/lesson/', method: 'post', data
  })
}

export function updateLesson(id, data) {
  return request({
    url: `/ftz/lesson/${id}/`, method: 'put', data
  })
}

export function deleteLesson(id, data) {
  return request({
    url: `/ftz/lesson/${id}/`, method: 'delete', data
  })
}
