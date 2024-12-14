<template>
  <el-card class="mb-4">
    <template #header>
      <div class="card-header">
        <span>修改标签</span>
      </div>
    </template>
    <el-form :model="form" inline>
      <el-form-item label="镜像ID">
        <el-input v-model="form.imageId"></el-input>
      </el-form-item>
      <el-form-item label="仓库名">
        <el-input v-model="form.repository"></el-input>
      </el-form-item>
      <el-form-item label="新标签">
        <el-input v-model="form.tag"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleTag" :loading="loading">修改标签</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { tagImage } from '../services/dockerApi'

const emit = defineEmits(['tag-updated'])

const loading = ref(false)
const form = ref({
  imageId: '',
  repository: '',
  tag: ''
})

const handleTag = async () => {
  try {
    loading.value = true
    await tagImage(form.value)
    ElMessage.success('标签修改成功')
    emit('tag-updated')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.mb-4 {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
