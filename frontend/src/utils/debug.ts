import axios from 'axios'

/**
 * Debug utility for API endpoints
 * Use in browser console: debug.checkEndpoint('/api/workorders/')
 */
class DebugUtility {
  async checkEndpoint(url: string, params: Record<string, any> = {}) {
    try {
      const response = await axios.get(url, { params })
      return response
    } catch (error: any) {
      throw error
    }
  }

  checkCsrfToken() {
    // Check if CSRF token cookie exists
    const cookies = document.cookie.split(';').map(c => c.trim())
    const csrfCookie = cookies.find(c => c.startsWith('csrftoken='))
  }
  
  checkAuth() {
    // Try to load user info endpoint
    return this.checkEndpoint('/api/user/info/').catch(error => {
      console.error('Failed to check authentication status')
    })
  }
  
  async fixWorkOrderList() {
    try {
      // 1. Check CSRF token
      this.checkCsrfToken()
      
      // 2. Check backend connection
      await this.checkEndpoint('/api/workorders/')
      
      // 3. Check products endpoint
      await this.checkEndpoint('/api/products/')
    } catch (error) {
      console.error('Fix attempt failed')
    }
  }
}

// Create instance and expose to window for console debugging
const debug = new DebugUtility()

// Make accessible from console
if (typeof window !== 'undefined') {
  // @ts-ignore
  window.debug = debug
}

export default debug 