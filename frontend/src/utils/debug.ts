import axios from 'axios'

/**
 * Debug utility for API endpoints
 * Use in browser console: debug.checkEndpoint('/api/workorders/')
 */
class DebugUtility {
  async checkEndpoint(url: string, params: Record<string, any> = {}) {
    console.log(`🔍 Testing endpoint: ${url}`)
    console.log(`Parameters:`, params)
    try {
      console.log(`Making request to ${url}...`)
      const response = await axios.get(url, { params })
      console.log(`✅ Response status: ${response.status}`)
      console.log(`Content-Type: ${response.headers['content-type']}`)
      
      if (response.data) {
        console.log('Response data:', response.data)
        if (Array.isArray(response.data)) {
          console.log(`Array response with ${response.data.length} items`)
          if (response.data.length > 0) {
            console.log('First item keys:', Object.keys(response.data[0]))
          }
        } else if (typeof response.data === 'object') {
          console.log('Object response with keys:', Object.keys(response.data))
          if (response.data.results) {
            console.log(`Paginated response with ${response.data.results.length} items (total: ${response.data.count || 'unknown'})`)
            if (response.data.results.length > 0) {
              console.log('First item keys:', Object.keys(response.data.results[0]))
            }
          }
        }
      } else {
        console.log('Empty response')
      }
      return response
    } catch (error: any) {
      console.error(`❌ Error testing endpoint ${url}:`, error)
      if (error.response) {
        console.error('Response status:', error.response.status)
        console.error('Response data:', error.response.data)
      }
      throw error
    }
  }

  checkCsrfToken() {
    // Check if CSRF token cookie exists
    const cookies = document.cookie.split(';').map(c => c.trim())
    const csrfCookie = cookies.find(c => c.startsWith('csrftoken='))
    
    console.log('🔐 CSRF Protection Check:')
    if (csrfCookie) {
      console.log('✅ CSRF cookie found:', csrfCookie)
    } else {
      console.error('❌ No CSRF cookie found')
    }
    
    // Check axios configuration
    console.log('Axios CSRF configuration:')
    console.log('- xsrfCookieName:', axios.defaults.xsrfCookieName)
    console.log('- xsrfHeaderName:', axios.defaults.xsrfHeaderName)
    console.log('- withCredentials:', axios.defaults.withCredentials)
  }
  
  checkAuth() {
    console.log('🔑 Authentication Check:')
    // Try to load user info endpoint
    return this.checkEndpoint('/api/user/info/').catch(error => {
      console.error('Failed to check authentication status')
    })
  }
  
  async fixWorkOrderList() {
    console.log('🛠️ Attempting to fix WorkOrderList:')
    try {
      // 1. Check CSRF token
      this.checkCsrfToken()
      
      // 2. Check backend connection
      await this.checkEndpoint('/api/workorders/')
      
      // 3. Check products endpoint
      await this.checkEndpoint('/api/products/')
      
      console.log('✅ All checks completed. Try refreshing the page.')
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