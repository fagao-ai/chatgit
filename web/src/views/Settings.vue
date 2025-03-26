<template>
  <span class="flex justify-self-start text-xs text-gray-300"
    >配置后将不再使用系统模型{{
      currentTab === 'title' ? ',标题建议使用不含思维链的模型' : ''
    }}</span
  >
  <div class="h-full w-full flex flex-col">
    <div class="flex items-center w-full justify-center">
      <SelectButton
        v-model="currentTab"
        :options="[
          { label: '系统设置', value: 'system' },
          { label: '标题设置', value: 'title' },
        ]"
        optionLabel="label"
        optionValue="value"
      />
    </div>
    <div v-if="currentTab === 'system'" class="flex flex-col items-center">
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
    <div v-else class="flex flex-col items-center">
      <div class="flex w-full items-center justify-between border-b border-gray-700 py-2">
        <div>跟随系统</div>
        <ToggleSwitch v-model="AIConfig.followSystem" />
      </div>
      <div class="flex w-full items-center justify-between border-b border-gray-700 py-2">
        <div>接口地址</div>
        <InputText
          :disabled="AIConfig.followSystem"
          type="text"
          size="small"
          v-model="AIConfig.titleBaseUrl"
        />
      </div>
      <div class="flex w-full items-center justify-between border-b border-gray-700 py-2">
        <div>模型</div>
        <InputText
          :disabled="AIConfig.followSystem"
          type="text"
          size="small"
          v-model="AIConfig.titleModel"
        />
      </div>
      <div class="flex w-full items-center justify-between border-b border-gray-700 py-2">
        <div>API Key</div>
        <Password
          :disabled="AIConfig.followSystem"
          :feedback="false"
          toggleMask
          size="small"
          v-model="AIConfig.titleApiKey"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import ToggleSwitch from 'primevue/toggleswitch'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import SelectButton from 'primevue/selectbutton'
import { AIConfig } from '@/states'

const currentTab = ref<'system' | 'title'>('system')

watch(
  () => AIConfig.value.followSystem,
  (val) => {
    if (val) {
      AIConfig.value.titleApiKey = AIConfig.value.apiKey
      AIConfig.value.titleModel = AIConfig.value.model
      AIConfig.value.titleBaseUrl = AIConfig.value.baseUrl
    }
  },
  { deep: true },
)
</script>

<style scoped></style>
