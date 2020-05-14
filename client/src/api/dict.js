import request from '@/utils/request'

export function getDictTypeList(query) {
  return request({
    url: '/system/dicttype/',
    method: 'get',
    params: query
  })
}
export function createDictType(data) {
  return request({
    url: '/system/dicttype/',
    method: 'post',
    data
  })
}
export function updateDictType(id, data) {
  return request({
    url: `/system/dicttype/${id}/`,
    method: 'put',
    data
  })
}
export function deleteDictType(id) {
  return request({
    url: `/system/dicttype/${id}/`,
    method: 'delete'
  })
}

export function getDictList(query) {
  return request({
    url: '/system/dict/',
    method: 'get',
    params: query
  })
}
export function createDict(data) {
  return request({
    url: '/system/dict/',
    method: 'post',
    data
  })
}
export function updateDict(id, data) {
  return request({
    url: `/system/dict/${id}/`,
    method: 'put',
    data
  })
}
export function deleteDict(id) {
  return request({
    url: `/system/dict/${id}/`,
    method: 'delete'
  })
}
