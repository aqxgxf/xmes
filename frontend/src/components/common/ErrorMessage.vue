<template>
  <el-alert
    v-if="error"
    :title="error"
    type="error"
    :closable="closable"
    show-icon
    effect="dark"
    class="error-message"
  />
</template>

<script lang="ts" setup>
defineProps({
  error: {
    type: String,
    default: null
  },
  closable: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.error-message {
  margin-bottom: 16px;
}
</style> 