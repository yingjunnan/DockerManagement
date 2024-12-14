<template>
  <div class="image-list">
    <el-table :data="images" style="width: 100%" v-loading="loading">
      <el-table-column prop="RepoTags" label="镜像名称" min-width="400">
        <template #default="scope">
          <div v-for="tag in scope.row.RepoTags" :key="tag" class="image-tag">
            <el-tag size="large">{{ tag }}</el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="Id" label="镜像ID" width="280" show-overflow-tooltip />
      <el-table-column prop="Size" label="大小" width="120">
        <template #default="scope">
          {{ formatSize(scope.row.Size) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="150">
        <template #default="{ row }">
          <el-button
            type="danger"
            size="small"
            @click="showDeleteConfirm(row)"
            :loading="row.deleting"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 确认删除对话框 -->
    <el-dialog
      v-model="deleteConfirmVisible"
      title="确认删除"
      width="500px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedImage" class="delete-dialog-content">
        <p>确定要删除以下镜像吗？</p>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="镜像ID">
            <div class="image-id">{{ formatImageId(selectedImage.Id) }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="标签">
            <div class="image-tags">
              <el-tag 
                v-for="tag in selectedImage.RepoTags" 
                :key="tag"
                size="small"
                class="tag-item"
              >
                {{ tag }}
              </el-tag>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteConfirmVisible = false">取消</el-button>
          <el-button type="danger" @click="handleDelete" :loading="loading">
            确认删除
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { deleteImage } from '../services/dockerApi'

const props = defineProps({
  images: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh'])

const deleteConfirmVisible = ref(false)
const selectedImage = ref(null)

const formatSize = (size) => {
  return `${(size / 1024 / 1024).toFixed(2)} MB`
}

const formatImageId = (id) => {
  // 移除 "sha256:" 前缀并只显示前12位
  return id.replace('sha256:', '').substring(0, 12)
}

const showDeleteConfirm = (image) => {
  selectedImage.value = image
  deleteConfirmVisible.value = true
}

const handleDelete = async () => {
  if (!selectedImage.value) return
  
  try {
    await deleteImage(selectedImage.value.Id)
    ElMessage.success('镜像删除成功')
    deleteConfirmVisible.value = false
    emit('refresh')
  } catch (error) {
    // 从错误响应中获取具体的错误信息
    const errorMessage = error.response?.data?.error || error.message
    ElMessage.error(errorMessage)
  }
}
</script>

<style scoped>
.image-list {
  padding: 20px;
}
.image-tag {
  margin-bottom: 8px;
}
.image-tag:last-child {
  margin-bottom: 0;
}
.dialog-footer {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.delete-dialog-content {
  padding: 0 20px;
}
.image-id {
  font-family: monospace;
  word-break: break-all;
  padding: 4px 0;
}
.image-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 4px 0;
}
.tag-item {
  margin-right: 8px;
  margin-bottom: 8px;
}
</style>
