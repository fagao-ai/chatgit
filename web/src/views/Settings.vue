<template>
  <span class="flex justify-self-start text-sm text-gray-300">配置后将不再使用系统模型</span>
  <div class="h-full w-full flex flex-col items-center">
    <div class="flex w-full items-center justify-between border-b border-gray-700 py-2">
      <div>接口地址</div>
      <InputText type="text" size="small" v-model="AIConfig.baseUrl" />
    </div>
    <div class="flex w-full items-center justify-between border-b border-gray-700 py-2">
      <div>模型</div>
      <InputText type="text" size="small" v-model="AIConfig.model" />
    </div>
    <div class="flex w-full items-center justify-between border-b border-gray-700 py-2">
      <div>API Key</div>
      <Password :feedback="false" toggleMask size="small" v-model="AIConfig.apiKey" />
    </div>
    <div class="flex w-full items-center justify-between border-b border-gray-700 py-2">
      <div>Github Token</div>
      <Password :feedback="false" toggleMask size="small" v-model="AIConfig.githubToken" />
    </div>
  </div>
</template>

<script setup lang="ts">
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import { AIConfig } from '@/states'
</script>

<style scoped></style>
