import request from '@/utils/request'


export function getCardById(id) {
  return request({
    url: `/ftz/card/${id}/`, method: 'get'
  })
}

export function getCardList(query) {
  return request({
    url: '/ftz/card/', method: 'get', params: query
  })
}

export function createCard(data) {
  return request({
    url: '/ftz/card/', method: 'post', data
  })
}

export function updateCard(id, data) {
  return request({
    url: `/ftz/card/${id}/`, method: 'put', data
  })
}

export function deleteCard(id, data) {
  return request({
    url: `/ftz/card/${id}/`, method: 'delete', data
  })
}
