import Cookies from 'js-cookie'

const TokenKey = 'token'

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
  return Cookies.set(TokenKey, token)
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}

// export function refreshToken() {
//   let token = getToken()
//   let data = {"token": token}
//   return request({
//     url: '/token/refresh/',
//     method: 'post',
//     data
//   })
// }
