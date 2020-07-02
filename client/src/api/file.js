import { getToken } from "@/utils/auth"
import request from '@/utils/request'

export function upUrl() {
  return process.env.VUE_APP_BASE_API + '/file/'
}

export function upHeaders() {
  return { Authorization: "Bearer " + getToken() }
}

export function getFileList(query) {
  return request({
    url: '/file/',
    method: 'get',
    params: query
  })
}