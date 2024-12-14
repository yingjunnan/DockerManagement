import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

export const fetchImages = async () => {
  try {
    const response = await axios.get(`${API_URL}/images`)
    return response.data
  } catch (error) {
    throw new Error('获取镜像列表失败：' + error.message)
  }
}

export const searchImages = async (term) => {
  try {
    const response = await axios.get(`${API_URL}/images/search`, {
      params: { term }
    })
    return response.data || []
  } catch (error) {
    throw new Error('搜索镜像失败：' + error.message)
  }
}

export const getImageTags = async (name) => {
  try {
    const response = await axios.get(`${API_URL}/images/tags`, {
      params: { name }
    })
    return response.data || []
  } catch (error) {
    throw new Error('获取镜像标签失败：' + error.message)
  }
}

export const pullImage = async (name) => {
  try {
    const response = await axios.post(`${API_URL}/images/pull`, {
      name
    })
    return response.data
  } catch (error) {
    throw new Error('拉取镜像失败：' + error.message)
  }
}

export const subscribePullProgress = (taskId, onProgress, onError) => {
  const eventSource = new EventSource(`${API_URL}/images/pull/progress/${taskId}`)
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.error) {
      onError(new Error(data.error))
      eventSource.close()
      return
    }
    
    onProgress(data)
    
    if (data.status === 'completed' || data.status === 'failed') {
      eventSource.close()
    }
  }
  
  eventSource.onerror = () => {
    onError(new Error('连接中断'))
    eventSource.close()
  }
  
  return eventSource
}

export const deleteImage = async (imageId) => {
  try {
    const response = await axios.delete(`${API_URL}/images/${imageId}`)
    return response.data
  } catch (error) {
    throw new Error('删除镜像失败：' + error.message)
  }
}

export const saveImage = async (imageName, fileName) => {
  try {
    const response = await axios.get(`${API_URL}/images/save/${encodeURIComponent(imageName)}`, {
      responseType: 'blob'
    })
    
    // 使用自定义文件名或默认文件名
    const downloadFileName = (fileName || imageName.replace(/[/:]/g, '-')) + '.tar'
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', downloadFileName)
    document.body.appendChild(link)
    link.click()
    
    // 清理
    window.URL.revokeObjectURL(url)
    document.body.removeChild(link)
    
    return true
  } catch (error) {
    throw new Error('保存镜像失败：' + error.message)
  }
}
