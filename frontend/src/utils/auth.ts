const TOKEN_KEY = 'auth_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user'

export const authUtils = {
  setToken: (token: string) => {
    localStorage.setItem(TOKEN_KEY, token)
  },
  
  getToken: (): string | null => {
    return localStorage.getItem(TOKEN_KEY)
  },
  
  setRefreshToken: (token: string) => {
    localStorage.setItem(REFRESH_TOKEN_KEY, token)
  },
  
  getRefreshToken: (): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },
  
  setUser: (user: any) => {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  
  getUser: (): any => {
    const user = localStorage.getItem(USER_KEY)
    return user ? JSON.parse(user) : null
  },
  
  clear: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
}

