<template>
  <div class="image-search">
    <div class="search-container">
      <el-form :model="form" class="search-form" @submit.prevent="handleSearch">
        <el-form-item class="search-form-item">
          <el-input
            v-model="searchTerm"
            placeholder="输入关键词搜索Docker镜像"
            clearable
            size="large"
            class="search-input"
            @keyup.enter.prevent="handleSearch"
          >
            <template #prefix>
              <el-icon class="search-icon"><Search /></el-icon>
            </template>
            <template #append>
              <el-button 
                type="primary" 
                size="large"
                @click="handleSearch" 
                :loading="loading"
              >
                搜索
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      
      <div class="search-tips" v-if="!searchResults.length && !loading">
        <el-empty description="输入关键词开始搜索Docker镜像">
          <template #image>
            <el-icon :size="60" class="search-empty-icon"><Search /></el-icon>
          </template>
        </el-empty>
      </div>
    </div>

    <el-dialog
      v-model="searchDialogVisible"
      title="搜索结果"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="searchResults.length > 0" class="results-container">
        <el-table :data="searchResults" style="width: 100%">
          <el-table-column prop="name" label="镜像名称" min-width="180">
            <template #default="{ row }">
              <div class="image-name">
                <span>{{ row.name }}</span>
                <el-tag v-if="row.official" type="success" size="small">官方</el-tag>
                <el-tag v-if="row.automated" type="info" size="small">自动构建</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
          <el-table-column prop="stars" label="星标数" width="100">
            <template #default="{ row }">
              <div class="stars">
                <el-icon><Star /></el-icon>
                {{ formatNumber(row.stars) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column width="100" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                @click="showPullDialog(row)"
              >
                拉取
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else-if="searched" class="no-results">
        <el-empty description="未找到镜像" />
      </div>
    </el-dialog>

    <el-dialog
      v-model="pullDialogVisible"
      title="拉取镜像"
      width="500px"
      :close-on-click-modal="false"
      :show-close="!pulling"
      append-to-body
    >
      <div v-if="selectedImage" class="pull-form">
        <template v-if="!pulling">
          <h3>{{ selectedImage.name }}</h3>
          <p v-if="selectedImage.description" class="description">
            {{ selectedImage.description }}
          </p>
          
          <div v-if="loadingTags" class="tags-loading">
            <el-skeleton :rows="3" animated />
          </div>
          
          <template v-else>
            <el-form>
              <el-form-item label="标签">
                <el-select 
                  v-model="tag" 
                  filterable 
                  placeholder="选择标签"
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in imageTags"
                    :key="item.name"
                    :label="formatTagLabel(item)"
                    :value="item.name"
                  >
                    <div style="display: flex; align-items: center; justify-content: space-between">
                      <span>{{ item.name }}</span>
                      <span style="color: #8492a6; margin-left: 15px">
                        {{ formatSize(item.full_size) }} | {{ formatDate(item.last_updated) }} | {{ item.architectures.join('/') }}
                      </span>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-form>
          </template>
        </template>

        <template v-else>
          <div class="pulling-status">
            <h3>正在拉取镜像</h3>
            <p class="image-name">{{ selectedImage.name }}:{{ tag }}</p>
            <el-progress 
              :percentage="pullProgress" 
              :status="pullProgress >= 100 ? 'success' : ''"
              :indeterminate="pullProgress === 0"
              :duration="3"
            />
            <p class="status-text">{{ pullStatus }}</p>
          </div>
        </template>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleCancel" :disabled="pulling">取消</el-button>
          <el-button
            type="primary"
            @click="handlePull"
            :loading="pulling"
            :disabled="!tag || loadingTags"
          >
            拉取
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Star, Search } from '@element-plus/icons-vue'
import { searchImages, pullImage, getImageTags, subscribePullProgress } from '../services/dockerApi'

export default {
  name: 'ImageSearch',
  components: {
    Star,
    Search
  },
  emits: ['image-pulled', 'refresh'],
  setup(props, { emit }) {
    const searchTerm = ref('')
    const loading = ref(false)
    const searchResults = ref([])
    const searched = ref(false)
    const searchDialogVisible = ref(false)
    const pullDialogVisible = ref(false)
    const selectedImage = ref(null)
    const tag = ref('')
    const pulling = ref(false)
    const pullProgress = ref(0)
    const pullStatus = ref('')
    
    const loadingTags = ref(false)
    const imageTags = ref([])
    let eventSource = null
    
    // 在组件销毁前清理EventSource
    onBeforeUnmount(() => {
      if (eventSource) {
        eventSource.close()
      }
    })

    const handleSearch = async () => {
      if (!searchTerm.value) return
      
      try {
        loading.value = true
        searchResults.value = await searchImages(searchTerm.value)
        searched.value = true
        searchDialogVisible.value = true
      } catch (error) {
        ElMessage.error(error.message)
      } finally {
        loading.value = false
      }
    }

    const showPullDialog = async (image) => {
      selectedImage.value = image
      tag.value = ''
      pullDialogVisible.value = true
      pullProgress.value = 0
      pullStatus.value = ''
      pulling.value = false
      
      // 加载镜像标签
      try {
        loadingTags.value = true
        imageTags.value = await getImageTags(image.name)
      } catch (error) {
        ElMessage.error(error.message)
      } finally {
        loadingTags.value = false
      }
    }

    const handlePull = async () => {
      if (!selectedImage.value || !tag.value) return
      
      const imageName = `${selectedImage.value.name}:${tag.value}`
      pulling.value = true
      pullStatus.value = '准备拉取...'
      pullProgress.value = 0
      
      try {
        const response = await pullImage(imageName)
        const taskId = response.task_id
        
        // 订阅进度更新
        const eventSource = subscribePullProgress(
          taskId,
          (data) => {
            // 更新进度和状态
            pullProgress.value = data.progress || 0
            pullStatus.value = data.message || ''
            
            // 当拉取完成时
            if (data.status === 'completed') {
              pulling.value = false
              ElMessage.success('镜像拉取成功')
              // 关闭所有对话框
              pullDialogVisible.value = false
              searchDialogVisible.value = false
              // 重置状态
              selectedImage.value = null
              tag.value = ''
              // 发送刷新事件到父组件
              emit('image-pulled')
            } else if (data.status === 'failed') {
              pulling.value = false
              ElMessage.error('镜像拉取失败：' + data.message)
            }
          },
          (error) => {
            pulling.value = false
            pullProgress.value = 0
            pullStatus.value = '拉取失败'
            ElMessage.error(error.message)
          }
        )
      } catch (error) {
        pulling.value = false
        pullProgress.value = 0
        pullStatus.value = '拉取失败'
        ElMessage.error(error.message)
      }
    }

    const handleCancel = () => {
      if (eventSource) {
        eventSource.close()
        eventSource = null
      }
      pullDialogVisible.value = false
      selectedImage.value = null
    }

    const formatNumber = (num) => {
      if (!num) return '0'
      return new Intl.NumberFormat().format(num)
    }

    const formatSize = (size) => {
      return `${(size / 1024 / 1024).toFixed(2)} MB`
    }

    const formatDate = (date) => {
      if (!date) return '未知'
      const d = new Date(date)
      return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
    }

    const formatTagLabel = (item) => {
      return item.name
    }

    return {
      searchTerm,
      loading,
      searchResults,
      searched,
      searchDialogVisible,
      pullDialogVisible,
      selectedImage,
      tag,
      pulling,
      pullProgress,
      pullStatus,
      loadingTags,
      imageTags,
      handleSearch,
      showPullDialog,
      handlePull,
      handleCancel,
      formatNumber,
      formatSize,
      formatDate,
      formatTagLabel
    }
  }
}
</script>

<style scoped>
.image-search {
  padding: 20px;
}

.search-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 0 40px;
}

.search-form {
  margin-bottom: 20px;
}

.search-form-item {
  width: 100%;
  margin-bottom: 0;
}

.search-input {
  --el-input-height: 50px;
  font-size: 16px;
}

.search-input :deep(.el-input__wrapper) {
  padding-left: 15px;
}

.search-icon {
  font-size: 20px;
  color: #909399;
  margin-right: 8px;
}

.search-tips {
  margin-top: 40px;
  text-align: center;
}

.search-empty-icon {
  color: #909399;
}

.loading-container {
  padding: 20px 0;
}

.results-container {
  margin-top: 20px;
}

.image-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stars {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #e6a23c;
}

.no-results {
  padding: 40px 0;
  text-align: center;
}

.pull-form {
  text-align: left;
}

.pull-form .description {
  color: #666;
  margin: 10px 0 20px;
}

.tag-label {
  color: #666;
  font-weight: bold;
}

.pull-progress {
  text-align: center;
  padding: 20px 0;
}

.pull-message {
  margin-top: 16px;
  color: #606266;
  font-size: 14px;
}

.tags-loading {
  padding: 20px 0;
}

.tag-name {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
}

.tag-info {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-info-item {
  font-size: 12px;
}

.tag-details {
  padding: 8px 0;
  width: 100%;
}
</style>
