<template>
  <div class="app-container">
    <el-container>
      <el-header height="auto">
        <div class="header-content">
          <h2>Docker 镜像管理</h2>
        </div>
      </el-header>
      <el-main>
        <div class="main-content">
          <el-row :gutter="20">
            <el-col :span="24">
              <div class="content-section">
                <div class="section-header">
                  <h3>搜索镜像</h3>
                </div>
                <image-search @image-pulled="handleImagePulled" />
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 50px;">
            <el-col :span="24">
              <div class="content-section">
                <div class="section-header">
                  <h3>本地镜像管理</h3>
                  <el-button type="primary" @click="refreshImages">
                    刷新列表
                  </el-button>
                </div>
                <image-list 
                  :images="images" 
                  :loading="loading"
                  @refresh="fetchImages"
                />
              </div>
            </el-col>
          </el-row>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import ImageSearch from './components/ImageSearch.vue'
import ImageList from './components/ImageList.vue'
import { ref, onMounted } from 'vue'
import { fetchImages as fetchImagesApi } from './services/dockerApi'

const images = ref([])
const loading = ref(false)

const fetchImages = async () => {
  try {
    loading.value = true
    images.value = await fetchImagesApi()
  } catch (error) {
    console.error('Error fetching images:', error)
  } finally {
    loading.value = false
  }
}

const refreshImages = () => {
  fetchImages()
}

const handleImagePulled = () => {
  fetchImages()
}

onMounted(() => {
  fetchImages()
})
</script>

<style>
/* 重置默认样式 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

/* 应用容器 */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  background-color: #f5f7fa;
}

/* 主布局容器 */
.el-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 头部 */
.header-content {
  padding: 16px;
  text-align: center;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 20;
  z-index: 100;
}

.header-content h2 {
  margin: 0;
  color: #303133;
}

/* 主要内容区域 */
.el-main {
  flex: 1;
  padding: 20px;
  overflow-x: hidden;
  background-color: #f5f7fa;
}

.main-content {
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 内容区块 */
.content-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  padding: 20px;
  margin-bottom: 20px;
  height: 100%;
}

/* 区块头部 */
.section-header {
  margin-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
}

/* 响应式布局 */
@media screen and (max-width: 768px) {
  .main-content {
    padding: 0 10px;
  }
  
  .content-section {
    padding: 15px;
  }
  
  .section-header {
    padding-bottom: 10px;
    margin-bottom: 15px;
  }
  
  .section-header h3 {
    font-size: 16px;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>
