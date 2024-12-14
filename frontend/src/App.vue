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
          <el-row :gutter="20" style="margin-top: 20px;">
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
.app-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}
.header-content {
  padding: 20px 0;
  text-align: center;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.header-content h2 {
  margin: 0;
  color: #303133;
}
.main-content {
  width: 100%;
  padding: 2px;
}
.content-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  padding: 20px;
}
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
}
</style>
